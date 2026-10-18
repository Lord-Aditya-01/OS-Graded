# OS-Graded# Operating Systems Activity 2: Deadlock Analysis and Resource Allocation Dashboard

**AI-Assisted Dashboard Development and Deadlock Analysis**  
*An Academic Web Application & Viva Demonstration Platform for Operating Systems*

[![Python Version](https://img.shields.io/badge/Python-3.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.49.1-red.svg)](https://streamlit.io/)
[![Test Suite](https://img.shields.io/badge/Pytest-30%20Passed-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/badge/Course-Operating%20Systems%20Graded-orange.svg)]()

---

## 1. Project Overview

This project delivers a comprehensive, interactive Operating Systems simulation dashboard for **Activity 2: “AI-Assisted Dashboard Development and Deadlock Analysis”**. 

Built with **Python, Streamlit, NumPy, Pandas, and Plotly**, the application provides unmocked, mathematically rigorous implementations of:
- **Dijkstra's Banker's Algorithm** for Deadlock Avoidance and safe-state verification.
- **Need Matrix Calculation** ($Need = Maximum - Allocation$) and dynamic Work vector tracing.
- **The 7-Step Resource Request Procedure** with guaranteed rollback on denial.
- **Multi-Instance Deadlock Detection Algorithm** (Silberschatz et al., Chapter 8) and Resource Allocation Graph (RAG) circular-wait visualization.
- **Deadlock Recovery** via interactive process termination and resource reclamation.
- **Deadlock Prevention** policies (Hierarchical Resource Ordering and Hold-and-Wait Elimination).
- **Automated Verification Suite** covering 10 boundary edge cases and the 6 required analytical test cases (TC1–TC6).

---

## 2. Key Features

- **Responsive Dark Slate / Navy UI:** Clean, high-contrast visual hierarchy designed for college viva presentation.
- **Sidebar Multipage Navigation:** 8 fully functioning sections without static mockups or placeholder buttons.
- **Metric Cards & Real-Time Badges:** Clear visual indicators for `SAFE`, `UNSAFE`, `DEADLOCK DETECTED`, `REQUEST WAITING`, `REQUEST DENIED`, `REQUEST GRANTED`, and `INVALID INPUT`.
- **Interactive Resource Allocation Graph (RAG):** Visualizes the circular-wait cycle ($P_0 \to R_1 \to P_1 \to R_0 \to P_0$) using Plotly.
- **Interactive Step-by-Step Stepper:** Walk through Banker's safety iterations, inspecting Work before, resources released, and Work after.
- **Non-Mutating Request Simulator:** Safely simulates requests on cloned states; commits only if safe, and provides formal before/after comparisons.
- **Dynamic Analytical Results Table:** TC1 through TC6 are executed dynamically live from the algorithms—no hardcoded "PASS" strings.
- **Educational Glossary & 6-Minute Demonstration Guide:** Complete timing roadmap and model viva questions and answers.

---

## 3. Technology Stack

- **Python 3.12 / 3.13:** Core algorithmic programming language.
- **Streamlit (>= 1.36.0):** Responsive reactive web dashboard framework.
- **Pandas (>= 2.2.0):** Matrix representations and analytical test reporting.
- **Plotly (>= 5.22.0):** Interactive utilization charts and directed Resource Allocation Graphs.
- **NumPy (>= 1.26.0):** Matrix calculations and component-wise vector comparisons.
- **Pytest (>= 8.0.0):** Automated test suite with 30 passing unit tests.

---

## 4. Project Directory Structure

```text
deadlock-dashboard/
├── .venv/                         # Local Python Virtual Environment
├── algorithms/                    # Modular, Reusable OS Algorithm Engine
│   ├── __init__.py                # Package exports
│   ├── bankers.py                 # Safety algorithm & safe sequence generation
│   ├── boundary_tests.py          # 10 boundary edge tests & TC1-TC6 runner
│   ├── deadlock_detection.py      # Silberschatz multi-instance detection & RAG
│   ├── deadlock_prevention.py     # Hierarchical ordering & hold-and-wait simulation
│   ├── resource_requests.py       # 7-step Banker's request procedure & commit/rollback
│   └── validation.py              # Strict matrix validation & capacity bounds
├── docs/                          # Academic Documentation & Records
│   ├── activity_analysis.md       # Full OS theoretical analysis & Coffman proofs
│   ├── ai_usage_record.md         # Transparent AI usage table & verification
│   └── viva_preparation.md        # 6-minute demonstration script & viva Q&A
├── tests/                         # Automated Pytest Suite (30 Passing Tests)
│   ├── __init__.py
│   ├── test_bankers.py            # Safety, Need matrix, Available, step traces
│   ├── test_boundary_cases.py     # All 10 boundary conditions & TC1-TC6 assertions
│   ├── test_deadlock_detection.py # Circular wait detection, recovery, RAG edges
│   ├── test_prevention.py         # Order enforcement, hold-and-wait trade-offs
│   ├── test_resource_requests.py  # Unsafe denial, commit helper, state restoration
│   └── test_validation.py         # Capacity overflow, negative inputs, invalid IDs
├── app.py                         # Complete Streamlit Dashboard Entrypoint
├── README.md                      # Comprehensive project documentation
└── requirements.txt               # Project dependencies
```

---

## 5. Algorithm Architecture & Working

### 5.1 Banker's Algorithm (Deadlock Avoidance)
1. **Need Calculation:** $Need[i][j] = Maximum[i][j] - Allocation[i][j]$.
2. **Work Initialization:** $Work = Available$, $Finish[i] = False$ for all processes.
3. **Loop:** Find an index $i$ where $Finish[i] == False$ and $Need[i] \le Work$ component-wise.
4. **Execution Simulation:** Process $P_i$ executes, releases its allocation: $Work = Work + Allocation[i]$, $Finish[i] = True$.
5. **Outcome:** If all processes finish, state is **SAFE** and the safe sequence is returned. If not, state is **UNSAFE** and blocked processes are listed.

### 5.2 Banker's Resource Request Procedure
When $P_i$ requests vector $Request[i]$:
1. Validate $0 \le i < n$.
2. If $Request[i] > Need[i]$: Reject as **INVALID INPUT** (exceeds maximum claim).
3. If $Request[i] > Available$: Classify as **REQUEST WAITING / NOT CURRENTLY AVAILABLE** without mutating state.
4. Temporarily allocate on isolated copies:
   $$Available_{temp} = Available - Request[i]$$
   $$Allocation_{temp}[i] = Allocation[i] + Request[i]$$
   $$Need_{temp}[i] = Need[i] - Request[i]$$
5. Run Banker's Safety Algorithm on tentative state.
6. If Safe $\to$ Grant request and optionally commit to active session.
7. If Unsafe $\to$ Deny request with status **REQUEST DENIED** and discard tentative state.

### 5.3 Deadlock Detection & Recovery
- Operates on $Available$, $Allocation$, and an outstanding $Request$ matrix.
- Sets $Finish[i] = True$ for processes holding no resources ($Allocation[i] == 0$).
- Repeatedly satisfies requests where $Request[i] \le Work$.
- Processes remaining unfinished ($Finish[i] == False$) are identified as **DEADLOCKED**.
- Recovery terminates a selected deadlocked process, reclaims its resources into $Available$, and immediately clears the deadlock.

### 5.4 Deadlock Prevention
- **Option 1 (Resource Ordering):** Enforces a global order $R_0 < R_1 < R_2$. Rejects backward requests, guaranteeing that the wait-for graph is an acyclic DAG.
- **Option 2 (Eliminate Hold-and-Wait):** Enforces all-at-once allocation upfront. Completely eliminates circular wait at the cost of increased average wait time and ~28% resource idle penalty.

---

## 6. Installation & Setup on Windows 11

Open PowerShell or Windows Terminal in the project root directory (`E:\OS graded\OS graded`):

### Step 1: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Step 2: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 7. Running the Application

Launch the Streamlit web dashboard:
```powershell
streamlit run app.py
```

The application will start and open automatically in your default browser at:
```text
http://localhost:8501
```

---

## 8. Running Automated Tests

Run the complete 30-test suite with detailed output:
```powershell
pytest -v
```

Expected output:
```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\OS graded\OS graded
collected 30 items

tests/test_bankers.py::test_need_matrix_calculation PASSED               [  3%]
tests/test_bankers.py::test_available_vector_calculation PASSED          [  6%]
tests/test_bankers.py::test_safe_sequence_generation PASSED              [ 10%]
tests/test_bankers.py::test_unsafe_state_detection PASSED                [ 13%]
tests/test_bankers.py::test_step_trace_details PASSED                    [ 16%]
tests/test_bankers.py::test_request_exceeding_need_is_invalid PASSED     [ 20%]
tests/test_bankers.py::test_waiting_request_is_not_invalid PASSED        [ 23%]
tests/test_bankers.py::test_unsafe_request_denial_restores_state PASSED  [ 26%]
tests/test_boundary_cases.py::test_all_10_boundary_cases_pass PASSED     [ 30%]
tests/test_boundary_cases.py::test_all_6_analytical_test_cases_pass PASSED [ 33%]
tests/test_deadlock_detection.py::test_deadlock_detection_for_circular_wait_example PASSED [ 36%]
tests/test_deadlock_detection.py::test_recovery_after_terminating_a_process PASSED [ 40%]
tests/test_deadlock_detection.py::test_recover_and_detect_clears_deadlock PASSED [ 43%]
tests/test_deadlock_detection.py::test_rag_edge_generation PASSED        [ 46%]
tests/test_deadlock_detection.py::test_no_deadlock_when_work_is_sufficient PASSED [ 50%]
tests/test_prevention.py::test_resource_order_prevention PASSED          [ 53%]
tests/test_prevention.py::test_simulate_fixed_ordering_policy PASSED     [ 56%]
tests/test_prevention.py::test_simulate_hold_and_wait_prevention PASSED  [ 60%]
tests/test_prevention.py::test_prevention_policy_summary PASSED          [ 63%]
tests/test_resource_requests.py::test_request_resulting_in_unsafe_state_is_denied PASSED [ 66%]
tests/test_resource_requests.py::test_successful_request_commit PASSED   [ 70%]
tests/test_resource_requests.py::test_commit_request_helper PASSED       [ 73%]
tests/test_resource_requests.py::test_denial_leaves_matrices_strictly_identical PASSED [ 76%]
tests/test_validation.py::test_negative_input_validation PASSED          [ 80%]
tests/test_validation.py::test_invalid_process_identifier PASSED         [ 83%]
tests/test_validation.py::test_inconsistent_matrix_is_rejected PASSED    [ 86%]
tests/test_validation.py::test_allocation_exceeding_total_capacity_rejected PASSED [ 90%]
tests/test_validation.py::test_allocation_exceeding_maximum_demand_rejected PASSED [ 93%]
tests/test_validation.py::test_maximum_exceeding_total_instances_rejected PASSED [ 96%]
tests/test_validation.py::test_valid_state_is_accepted PASSED            [100%]

============================= 30 passed in 0.10s ==============================
```

---

## 9. Six-Minute Demonstration Roadmap for Viva

Follow this recommended timeline during your presentation:

| Time | Section | Key Demonstration Actions |
| :--- | :--- | :--- |
| **0:00 – 0:45** | **1. Overview Dashboard** | Introduce the project, technology stack, metric cards, and live safety status badge. |
| **0:45 – 2:15** | **3. Banker's Algorithm** | Show calculated Need matrix. Run Banker's Safety check. Display safe sequence `P1 → P3 → P4 → P0 → P2`. Walk through the step-by-step trace. |
| **2:15 – 3:15** | **4. Request Simulator (Scenario B)** | Click **Scenario B: Exceeds Available (Waiting)** ($P_0$ requests $[4, 0, 0]$). Show status **REQUEST WAITING**. Explain why it is valid but must wait. |
| **3:15 – 4:30** | **4. Request Simulator (Scenario C)** | Click **Scenario C: Produces Unsafe State (Denied)** ($P_0$ requests $[0, 0, 2]$). Run simulation. Show status **REQUEST DENIED**, explain unsafe outcome, and demonstrate exact rollback. |
| **4:30 – 5:30** | **5. Deadlock Detection** | Show 2-process circular wait in the Resource Allocation Graph ($P_0 \to R_1 \to P_1 \to R_0 \to P_0$). Detect deadlock. Terminate $P_0$ to show recovery. |
| **5:30 – 6:00** | **7. Test Cases & Summary** | Show dynamic Analytical Results Table (TC1–TC6) and summarize distinctions between Prevention, Avoidance, and Detection. |

---

## 10. Required Analytical Results Summary

| Test Case | Description | Expected Result | Actual Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **TC1** | Safe State Analysis | Safe sequence found | Sequence: `[1, 3, 4, 0, 2]` | **PASS** |
| **TC2** | Request Exceeds Available | Request not granted immediately | Status: `waiting` (state unchanged) | **PASS** |
| **TC3** | Request Makes State Unsafe | Request denied; state restored | Status: `denied` (state unchanged) | **PASS** |
| **TC4** | Deadlocked Scenario | Circular wait identified | Deadlocked: `['P0', 'P1']` | **PASS** |
| **TC5** | Prevention Policy Applied | Deadlock condition eliminated | Circular wait: `False` (Enforced) | **PASS** |
| **TC6** | Boundary & Invalid Inputs | Correct validation handling | 10/10 boundary tests passed | **PASS** |

---

## 11. Known Assumptions and Academic Limitations

1. **Static Maximum Claims in Avoidance:** In accordance with the classical Banker's model, processes declare their maximum resource demands upfront.
2. **Discrete Integer Modeling:** All resource allocations are discrete non-negative integer quantities.
3. **Single vs Multiple Instance Equivalence:** Cycles in a Resource Allocation Graph (RAG) indicate guaranteed deadlock under single-instance resources; for multiple instances, matrix-based detection is used.
4. **Immediate Process Termination:** Deadlock recovery in this activity models single-process termination with complete resource return to the Available pool.

---

## 12. Authors & Acknowledgments

- **Course:** Operating Systems Graded Activity 2
- **Topic:** AI-Assisted Dashboard Development and Deadlock Analysis
- **References:** *Operating System Concepts* (10th Edition), Abraham Silberschatz, Peter B. Galvin, Greg Gagne.
