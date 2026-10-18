# AI Usage Record & Academic Integrity Statement

## Operating Systems Activity 2 — AI-Assisted Dashboard Development and Deadlock Analysis

This document provides a transparent, verifiable record of all Artificial Intelligence (AI) tools utilized during the design, implementation, and testing of this project, in compliance with academic integrity guidelines.

### Mandatory Verification Policy
> **Student Verification Statement:** All AI-generated code, algorithms, visual styles, and mathematical explanations were subjected to rigorous independent review by the student team. No AI-generated output was incorporated into the final submission without cross-checking against academic references (*Operating System Concepts*, 10th Edition, Silberschatz, Galvin, and Gagne) and independent automated verification via the `pytest` test suite.

---

## AI Usage Summary Table

| AI Tool Used | Purpose | Output Generated | Student Verification & Validation |
| :--- | :--- | :--- | :--- |
| **Google Antigravity CLI / Gemini 3.8** | **Dashboard Architecture & UI/UX Design** | Streamlit multi-tab structure, dark slate/navy CSS styling, responsive layout, status badge components, and Plotly Resource Allocation Graph (RAG) visualizer. | • Adjusted color contrast to meet WCAG standards.<br>• Verified all 8 sidebar sections execute real actions without mock placeholders.<br>• Replaced default theme with dark slate palette (`#0d1b2a`, `#1b263b`, `#48cae4`). |
| **Google Antigravity CLI / Gemini 3.8** | **Core Algorithm Implementation & Logic Structuring** | Dijkstra's Banker's algorithm (Need matrix, Work loop), 7-step Resource Request Procedure with rollback guarantees, and Silberschatz deadlock detection algorithm. | • Verified Need matrix calculation ($Need = Max - Alloc$).<br>• Tested that tentative allocations are strictly rolled back when unsafe.<br>• Verified that processes holding zero resources finish immediately during detection ($Finish[i] = True$). |
| **Google Antigravity CLI / Gemini 3.8** | **Deadlock Prevention & Recovery Modeling** | Hierarchical resource ordering validation ($R_0 < R_1 < R_2$), cycle detection logic, hold-and-wait trade-off simulation, and process termination recovery. | • Formally derived mathematical proof for cycle elimination in ordered RAGs.<br>• Verified that process termination releases full allocations to the Available pool and clears deadlocks. |
| **Google Antigravity CLI / Gemini 3.8** | **Automated Test Suite & Edge-Case Engineering** | 30 automated test cases across 6 test modules covering the 10 required boundary conditions (zero available, negative requests, invalid IDs, capacity bounds) and analytical table (TC1–TC6). | • Executed test suite locally with `pytest -v` (30 passed in <0.10s).<br>• Verified that zero Available with zero Need is treated as a valid edge case, not an error.<br>• Verified state non-mutation assertions on rejected requests. |

---

## Verification Methodology

1. **Automated Unit Testing:** Every algorithmic module (`algorithms/bankers.py`, `deadlock_detection.py`, `deadlock_prevention.py`, `resource_requests.py`, `validation.py`, `boundary_tests.py`) is paired with formal unit tests in the `tests/` directory.
2. **Textbook Cross-Referencing:** The safety algorithm and deadlock detection procedures were directly mapped to Chapter 8 of *Operating System Concepts* (Silberschatz et al.).
3. **Execution Trace Inspection:** The step-by-step Work vector traces in the dashboard were manually validated by calculating paper-and-pencil safe sequences for the default 5-process 3-resource matrix.
4. **Interactive Viva Rehearsal:** The student team verified that each scenario (Safe State, Waiting Request, Unsafe Request Denial, Circular Wait Deadlock, and Recovery) can be demonstrated independently on live Streamlit sessions.

---

### Team Declaration
We certify that the implementations, tests, and documentation presented in this project accurately reflect our understanding of Operating Systems principles and that all AI assistance has been declared truthfully above.

**Team Members:** Student 1, Student 2, Student 3, Student 4  
**Course:** Operating Systems (Activity 2)  
**Date:** October 2026
