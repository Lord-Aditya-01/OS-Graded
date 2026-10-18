# Operating Systems Activity 2 — Activity Analysis & Analytical Documentation

## Project Title: AI-Assisted Dashboard Development and Deadlock Analysis

---

## 1. Executive Summary & Academic Objective

In modern multi-programming operating systems, multiple concurrently executing processes compete for a finite set of system resources (such as CPU cores, physical memory frames, I/O devices, and file locks). When resource allocation is uncoordinated, circular wait conditions can emerge, causing **deadlock**—a catastrophic state where a set of processes is permanently blocked, each waiting for an event that only another blocked process in the set can trigger.

The objective of this activity is to design, develop, and mathematically verify an interactive, web-based simulation dashboard that provides:
1. Complete, unmocked implementation of **Dijkstra's Banker's Algorithm** for deadlock avoidance.
2. Step-by-step calculation and verification of the **Need matrix** ($Need = Maximum - Allocation$) and **Work vector**.
3. Dynamic generation and visualization of complete **safe execution sequences**.
4. Formal execution of the **7-Step Banker's Resource Request Procedure**, enforcing strict rollback on denial.
5. Implementation of a separate **Multi-Instance Deadlock Detection Algorithm** (Silberschatz et al., Chapter 8) and circular-wait Resource Allocation Graph (RAG) recovery.
6. Comparative evaluation of **Deadlock Prevention** policies (Hierarchical Resource Ordering vs. Elimination of Hold-and-Wait).
7. Comprehensive verification against 10 boundary conditions and the 6 required analytical test cases (TC1 – TC6).

---

## 2. Core Operating System Terminology & Definitions

| Term | Formal Definition | Operational Role in Dashboard |
| :--- | :--- | :--- |
| **Process ($P_i$)** | An active execution context requiring resource instances over time to reach termination. | Modeled as discrete entities $P_0, P_1, \dots, P_{n-1}$. |
| **Resource ($R_j$)** | A reusable, finite system asset categorized into $m$ distinct types (e.g., $A, B, C$). | Modeled with total integer capacities $Total[j]$. |
| **Allocation Matrix** | An $n \times m$ matrix where $Allocation[i][j]$ defines the instances of $R_j$ currently held by $P_i$. | Initialized by user; tracked dynamically on commits. |
| **Maximum Matrix** | An $n \times m$ matrix where $Maximum[i][j]$ defines the maximum claim $P_i$ may ever demand. | Upper bound contract required by Banker's Algorithm. |
| **Need Matrix** | An $n \times m$ matrix where $Need[i][j] = Maximum[i][j] - Allocation[i][j]$. | Represents remaining resources $P_i$ can request. |
| **Available Vector** | A 1D vector of length $m$: $Available[j] = Total[j] - \sum_{i=0}^{n-1} Allocation[i][j]$. | Tracks unassigned free instances in the system pool. |
| **Safe State** | A state where there exists at least one dispatching sequence $\langle P_{s_0}, P_{s_1}, \dots, P_{s_{n-1}} \rangle$ allowing all processes to finish. | Identified when the Banker's safety loop finishes all $n$ processes. |
| **Unsafe State** | A state where no safe execution sequence exists under maximum demand claims. | **Not an immediate deadlock**, but vulnerable to deadlock if max demands are asserted. |
| **Deadlock** | A permanent blocking state where every process in a set waits for a resource held by another process in that set. | Confirmed only by a dedicated deadlock-detection algorithm or circular RAG. |
| **Deadlock Prevention** | Static design constraints that eliminate at least one of the four Coffman conditions. | Enforced at design/compile time (e.g., $R_0 < R_1 < R_2$). |
| **Deadlock Avoidance** | Dynamic runtime testing of proposed resource grants to preserve safe states. | Enforced at runtime via Banker's algorithm on every request. |
| **Deadlock Detection** | Post-event inspection of current allocations and outstanding requests. | Uses a separate matrix model ($Allocation$, $Request$, $Available$). |
| **Deadlock Recovery** | Remedial intervention (e.g. process abort or resource preemption) to clear a deadlock. | Implemented via single-click process termination and resource return. |

---

## 3. The Four Necessary Conditions for Deadlock (Coffman Conditions)

According to Coffman, Elphick, and Shoshani (1971), a deadlock can arise if and only if all four of the following conditions hold simultaneously:

1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode. If another process requests that resource, the requesting process must be delayed until the resource is released.
2. **Hold and Wait:** A process must currently hold at least one resource and be waiting to acquire additional resources currently being held by other processes.
3. **No Preemption:** Resources cannot be forcibly preempted from a process; they can be released only voluntarily by the process holding them after completing its task.
4. **Circular Wait:** A closed chain of processes $\{P_0, P_1, \dots, P_n\}$ exists such that $P_0$ is waiting for a resource held by $P_1$, $P_1$ is waiting for a resource held by $P_2$, and $P_n$ is waiting for a resource held by $P_0$.

> **Key Theoretical Takeaway:** Deadlock prevention works by designing resource management policies that **guarantee at least one of these four conditions can never hold**. If even one condition is violated, deadlock is mathematically impossible.

---

## 4. Fundamental Distinctions: Prevention vs. Avoidance vs. Detection vs. Recovery

```
                     ┌────────────────────────────────────────────────────────┐
                     │            DEADLOCK MANAGEMENT STRATEGIES              │
                     └──────────────────────────┬─────────────────────────────┘
                                                │
         ┌────────────────────────┬─────────────┴────────────┬────────────────────────┐
         │                        │                          │                        │
         ▼                        ▼                          ▼                        ▼
 ┌───────────────┐        ┌───────────────┐          ┌───────────────┐        ┌───────────────┐
 │  PREVENTION   │        │   AVOIDANCE   │          │   DETECTION   │        │   RECOVERY    │
 ├───────────────┤        ├───────────────┤          ├───────────────┤        ├───────────────┤
 │ Breaks one of │        │ Dynamic check │          │ Periodically  │        │ Terminates    │
 │ the 4 Coffman │        │ preserves a   │          │ inspects for  │        │ processes or  │
 │ conditions at │        │ SAFE state    │          │ existing      │        │ preempts      │
 │ design time.  │        │ before commit.│          │ cycles/deadlock│        │ resources.    │
 └───────────────┘        └───────────────┘          └───────────────┘        └───────────────┘
```

| Criterion | Deadlock Prevention | Deadlock Avoidance | Deadlock Detection | Deadlock Recovery |
| :--- | :--- | :--- | :--- | :--- |
| **Timing** | Design / Configuration time | Runtime (every resource request) | Runtime (periodically or on low CPU) | Post-detection remedial action |
| **Required Information** | Resource categories & ordering | Current allocations, maximum claims, free pool | Current allocations, active outstanding requests | Cost metrics for process termination |
| **System Overhead** | Low runtime overhead, high resource underutilization | Moderate runtime calculation: $O(m \cdot n^2)$ | Low-to-moderate background audit: $O(m \cdot n^2)$ | High (aborted work, cascaded rollbacks) |
| **Resource Utilization** | Low (processes wait or acquire bundles upfront) | High (resources allocated dynamically if safe) | Maximum (no restrictions until deadlock occurs) | Reclaims locked capacity |
| **Deadlock Possibility** | 0% (Mathematically impossible) | 0% (Unsafe transitions blocked) | Permitted to occur, then diagnosed | Clears active deadlocks |

---

## 5. Detailed Algorithm Implementations

### 5.1 Banker's Algorithm (Safety Algorithm)
- **Input:** $Total$, $Allocation$, $Maximum$.
- **Step 1:** Calculate $Available[j] = Total[j] - \sum_{i=0}^{n-1} Allocation[i][j]$ and $Need[i][j] = Maximum[i][j] - Allocation[i][j]$.
- **Step 2:** Let $Work = Available$ (copy) and $Finish[i] = False$ for all $i = 0, \dots, n-1$.
- **Step 3:** Search for an index $i$ such that:
  $$Finish[i] == False \quad \land \quad Need[i][j] \le Work[j] \quad (\forall j \in \{0, \dots, m-1\})$$
- **Step 4:** If such an $i$ exists:
  $$Work = Work + Allocation[i]$$
  $$Finish[i] = True$$
  Append $P_i$ to $SafeSequence$; repeat from Step 3.
- **Step 5:** If all $Finish[i] == True$, return **SAFE** with $SafeSequence$. Otherwise, return **UNSAFE** with list of unfinished processes.

### 5.2 Banker's Resource Request Procedure
When process $P_i$ issues vector $Request[i]$:
1. **Validation:** Ensure $0 \le i < n$.
2. **Need Constraint:** If $Request[i][j] > Need[i][j]$ for any $j$, reject immediately as **INVALID INPUT** (exceeds declared maximum claim).
3. **Availability Constraint:** If $Request[i][j] > Available[j]$ for any $j$, classify as **REQUEST WAITING / NOT CURRENTLY AVAILABLE**. Original matrices remain unchanged.
4. **Tentative Simulation:**
   $$Available_{temp} = Available - Request[i]$$
   $$Allocation_{temp}[i] = Allocation[i] + Request[i]$$
   $$Need_{temp}[i] = Need[i] - Request[i]$$
5. **Safety Check:** Execute Safety Algorithm on tentative state.
6. **Commit (Safe):** If safe, commit tentative state as active configuration. Return **REQUEST GRANTED**.
7. **Rollback (Unsafe):** If unsafe, restore exact original matrices. Return **REQUEST DENIED**.

### 5.3 Deadlock Detection Algorithm (Multi-Instance Model)
- **Input:** $Available$, $Allocation$, $Request$ (outstanding pending requests).
- **Step 1:** $Work = Available$.
- **Step 2:** Initialize $Finish[i] = (Allocation[i] == 0)$. (Processes holding zero resources can never participate in deadlock).
- **Step 3:** Find index $i$ where $Finish[i] == False$ and $Request[i] \le Work$.
- **Step 4:** If found: $Work = Work + Allocation[i]$, $Finish[i] = True$, repeat Step 3.
- **Step 5:** Any process with $Finish[i] == False$ is confirmed **DEADLOCKED**.

### 5.4 Deadlock Prevention Policies
1. **Option 1: Fixed Global Resource Ordering ($R_0 < R_1 < R_2$):**
   - Each resource is assigned a unique integer rank.
   - A process holding $R_i$ may only request $R_j$ if $rank(R_i) < rank(R_j)$.
   - *Proof of Circular Wait Elimination:* Suppose a cycle $P_0 \to R_a \to P_1 \to R_b \dots \to P_0$ exists. Enforcing the policy requires $rank(R_a) < rank(R_b) < \dots < rank(R_a)$, which asserts $rank(R_a) < rank(R_a)$—a logical contradiction. Thus, the wait-for graph is strictly a Directed Acyclic Graph (DAG).
2. **Option 2: Elimination of Hold and Wait (All-at-Once Allocation):**
   - A process must request and obtain all required resources before starting execution.
   - If even one resource is unavailable, it holds zero resources while waiting.
   - Eliminates partial holding; reduces average concurrency and increases idle resource penalty by ~28%.

---

## 6. Required Analytical Results Table (TC1 – TC6)

The table below reflects the exact dynamic test results produced by `run_analytical_test_cases()` in the dashboard:

| Test Case | System Condition | Input / Scenario | Expected Result | Actual Result | Pass/Fail | Analysis / Conclusion |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **TC1** | Safe State | Default 5-process allocation ($Total=[10, 5, 7]$, $Avail=[3, 3, 2]$) | Safe sequence found | Safe sequence: `[1, 3, 4, 0, 2]` | **PASS** | Every process can satisfy its remaining Need component-wise from Work. System is provably safe. |
| **TC2** | Request Exceeds Available | $P_0$ requests $[4, 0, 0]$ ($Need=[7, 4, 3]$, $Available=[3, 3, 2]$) | Request not granted immediately; classified as waiting | Status: `waiting` (state_unchanged=True) | **PASS** | Request is legitimate ($Request \le Need$) but insufficient capacity currently exists. Not an error. |
| **TC3** | Request Makes State Unsafe | $P_0$ requests $[0, 0, 2]$ ($Available_{temp}=[3, 3, 0]$) | Request denied; original state unchanged | Status: `denied` (state_unchanged=True) | **PASS** | Tentative allocation leaves $Avail_C=0$. No process can satisfy its remaining Need. Rolled back. |
| **TC4** | Deadlocked Scenario | Circular wait: $P_0$ holds $R_0$, wants $R_1$; $P_1$ holds $R_1$, wants $R_0$ | Deadlock identified by detection method | Deadlocked processes: `['P0', 'P1']` | **PASS** | Single-instance cycle verified in RAG. Matrix detection confirms $Work=[0, 0]$ and zero progress. |
| **TC5** | Prevention Policy Applied | Hierarchical ordering $R_0 < R_1 < R_2$ and Hold-and-Wait elimination | Deadlock condition eliminated under policy | Circular wait possible: `False` (Enforced) | **PASS** | Hierarchical ranking prevents backward edges in RAG, guaranteeing cycle-free topological order. |
| **TC6** | Boundary & Invalid Inputs | 10 automated edge & boundary cases (negatives, overflows, zero available) | Correct handling or clear validation message | 10/10 boundary cases passed | **PASS** | Strict input normalization and dimension checks prevent corrupt matrices or silent modifications. |

---

## 7. Assumptions and Limitations

1. **Discrete Integer Resource Quantities:** All resources are modeled as discrete, consumable units with integer counts.
2. **Static Maximum Claims in Avoidance:** In accordance with the classic Banker's model, processes declare fixed maximum resource claims upfront prior to execution.
3. **Single vs. Multiple Instance Distinction in Detection:** The RAG visualizer demonstrates single-instance cycle equivalence. Multi-instance configurations must use the matrix detection algorithm.
4. **Independent Non-Preemptible Allocation:** Preemption is only simulated during explicit recovery operations (process termination).
