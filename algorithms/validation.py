from __future__ import annotations

from typing import Iterable, List, Sequence


def _as_int(value, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a nonnegative integer.")
    if isinstance(value, int):
        integer = value
    elif isinstance(value, float):
        if value.is_integer():
            integer = int(value)
        else:
            raise ValueError(f"{label} must be a nonnegative integer.")
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{label} must be a nonnegative integer.")
        try:
            integer = int(stripped)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError(f"{label} must be a nonnegative integer.") from exc
    else:
        raise ValueError(f"{label} must be a nonnegative integer.")

    if integer < 0:
        raise ValueError(f"{label} must be nonnegative.")
    return integer


def _normalize_matrix(matrix: Sequence[Sequence[object]], rows: int, cols: int, name: str) -> List[List[int]]:
    if len(matrix) != rows:
        raise ValueError(f"{name} must have {rows} rows, received {len(matrix)}.")

    normalized: List[List[int]] = []
    for r_index, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)):
            raise ValueError(f"Row {r_index} in {name} is not a list-like object.")
        if len(row) != cols:
            raise ValueError(f"{name} row {r_index} must have {cols} entries, received {len(row)}.")
        normalized_row: List[int] = []
        for c_index, value in enumerate(row):
            normalized_row.append(_as_int(value, f"{name}[{r_index}][{c_index}]") )
        normalized.append(normalized_row)
    return normalized


def validate_resource_configuration(total_instances: Sequence[object], allocation: Sequence[Sequence[object]], maximum: Sequence[Sequence[object]]) -> dict:
    errors: List[str] = []
    try:
        total = [_as_int(value, f"Resource total[{idx}]") for idx, value in enumerate(total_instances)]
    except ValueError as exc:
        return {"valid": False, "errors": [str(exc)]}

    if not total:
        return {"valid": False, "errors": ["At least one resource type is required."]}

    process_count = len(allocation)
    resource_count = len(total)

    if process_count == 0:
        return {"valid": False, "errors": ["At least one process is required."]}

    if len(maximum) != process_count:
        errors.append(f"Maximum demand matrix must have {process_count} rows, received {len(maximum)}.")

    for i, row in enumerate(allocation):
        if len(row) != resource_count:
            errors.append(f"Allocation row {i} must have {resource_count} values, received {len(row)}.")

    for i, row in enumerate(maximum):
        if len(row) != resource_count:
            errors.append(f"Maximum row {i} must have {resource_count} values, received {len(row)}.")

    try:
        alloc_matrix = _normalize_matrix(allocation, process_count, resource_count, "Allocation")
    except ValueError as exc:
        errors.append(str(exc))
        alloc_matrix = []

    try:
        max_matrix = _normalize_matrix(maximum, process_count, resource_count, "Maximum")
    except ValueError as exc:
        errors.append(str(exc))
        max_matrix = []

    if alloc_matrix and max_matrix:
        for i in range(process_count):
            for j in range(resource_count):
                if alloc_matrix[i][j] > total[j]:
                    errors.append(
                        f"Allocation[{i}][{j}] ({alloc_matrix[i][j]}) exceeds total resource {j} ({total[j]})."
                    )
                if alloc_matrix[i][j] > max_matrix[i][j]:
                    errors.append(
                        f"Allocation[{i}][{j}] ({alloc_matrix[i][j]}) exceeds Maximum[{i}][{j}] ({max_matrix[i][j]})."
                    )
                if max_matrix[i][j] > total[j]:
                    errors.append(
                        f"Maximum[{i}][{j}] ({max_matrix[i][j]}) exceeds total resource {j} ({total[j]})."
                    )
        for j in range(resource_count):
            col_alloc_sum = sum(alloc_matrix[i][j] for i in range(process_count))
            if col_alloc_sum > total[j]:
                errors.append(
                    f"Total allocated instances of resource {j} ({col_alloc_sum}) exceeds total capacity ({total[j]})."
                )

    return {
        "valid": not errors,
        "errors": errors,
        "total_instances": total,
        "allocation": alloc_matrix,
        "maximum": max_matrix,
    }


def validate_state(total_instances: Sequence[int], allocation: Sequence[Sequence[int]], maximum: Sequence[Sequence[int]]) -> dict:
    result = validate_resource_configuration(total_instances, allocation, maximum)
    if not result["valid"]:
        return result

    available = [total_instances[j] - sum(row[j] for row in allocation) for j in range(len(total_instances))]
    need = [
        [maximum[i][j] - allocation[i][j] for j in range(len(total_instances))]
        for i in range(len(allocation))
    ]
    result["available"] = available
    result["need"] = need
    return result


def validate_request(process_id: int, request: Sequence[int], need: Sequence[Sequence[int]], available: Sequence[int], total_instances: Sequence[int]) -> dict:
    errors: List[str] = []
    if process_id < 0 or process_id >= len(need):
        return {"valid": False, "status": "invalid", "errors": [f"Process ID {process_id} is invalid."], "message": "Invalid process identifier."}

    try:
        request_vec = [_as_int(value, f"Request[{idx}]") for idx, value in enumerate(request)]
    except ValueError as exc:
        return {"valid": False, "status": "invalid", "errors": [str(exc)]}

    if len(request_vec) != len(available):
        return {"valid": False, "status": "invalid", "errors": [f"Request length must be {len(available)}, got {len(request_vec)}."]}

    if any(value < 0 for value in request_vec):
        errors.append("Request vector contains a negative resource value.")

    if any(request_vec[i] > need[process_id][i] for i in range(len(request_vec))):
        errors.append("Request exceeds the process's remaining need.")

    if any(request_vec[i] > available[i] for i in range(len(request_vec))):
        if not errors:
            return {
                "valid": False,
                "status": "waiting",
                "errors": ["Request is valid but exceeds currently available resources."],
                "message": "Request cannot be granted immediately because resources are not currently available.",
                "request": request_vec,
            }
        errors.append("Request also exceeds the available vector.")

    if errors:
        return {"valid": False, "status": "invalid", "errors": errors, "request": request_vec, "message": errors[0]}

    return {"valid": True, "status": "ready", "errors": [], "request": request_vec, "message": "Request is valid and available."}
