# Six-Minute Viva Demonstration Guide & Oral Exam Preparation

## Operating Systems Activity 2: Deadlock Analysis & Resource Allocation Dashboard

---

## 1. Six-Minute Demonstration Script & Presentation Roadmap

This guide is structured to allow four student team members to present a polished, comprehensive demonstration within a strict 6-minute window.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   6-MINUTE DEMONSTRATION TIMELINE                      │
├──────────────┬───────────────────────────────┬─────────────────────────┤
│ 0:00 - 0:45  │ Project Intro & Architecture  │ Student 1               │
│ 0:45 - 2:15  │ Need Calculation & Banker's   │ Student 2               │
│ 2:15 - 3:15  │ Scenario B: Request Waiting   │ Student 3               │
│ 3:15 - 4:30  │ Scenario C: Unsafe Denial     │ Student 4               │
│ 4:30 - 5:30  │ Deadlock Detection & Recovery │ Students 1 & 2          │
│ 5:30 - 6:00  │ Analytical Results & Wrap-up  │ Students 3 & 4          │
└──────────────┴───────────────────────────────┴─────────────────────────┘
```

---

### Segment 1: Introduction & Dashboard Overview (0:00 – 0:45) | Presenter: Student 1
- **Action:** Open `http://localhost:8501` to the **1. Overview Dashboard** page.
- **Speaking Script:**
  > "Good morning/afternoon, Professor. Today we present our interactive Operating Systems dashboard for Activity 2: *AI-Assisted Dashboard Development and Deadlock Analysis*.
  > Our application is implemented in Python 3.13 and Streamlit, featuring unmocked, real mathematical implementations of Dijkstra's Banker's Algorithm, deadlock detection, prevention, and recovery.
  > On the home screen, you see live metric cards showing 5 processes, 3 resource types (A, B, C), total capacity of 22 instances, currently available instances, and our dynamic safety badge. You can also see our resource utilization stacked bar chart and allocation breakdown. Everything is calculated in real time."

---

### Segment 2: Banker's Safety Algorithm & Safe Sequence (0:45 – 2:15) | Presenter: Student 2
- **Action:** Navigate to **3. Banker's Algorithm**.
- **Speaking Script:**
  > "Here we demonstrate Dijkstra's Banker's algorithm for deadlock avoidance. First, the system automatically computes the Need matrix using the formula $Need[i][j] = Maximum[i][j] - Allocation[i][j]$.
  > Notice Available is $[3, 3, 2]$. When we click **Run Banker's Safety Analysis**, the algorithm initializes $Work = Available$ and searches for an unfinished process whose Need is component-wise less than or equal to Work.
  > In iteration 1, process $P_1$ needs $[1, 2, 2] \le [3, 3, 2]$, so $P_1$ finishes and releases its allocation $[2, 0, 0]$, updating Work to $[5, 3, 2]$.
  > Continuing this loop produces the safe sequence: $\mathbf{\langle P_1, P_3, P_4, P_0, P_2 \rangle}$.
  > Using our interactive stepper, we can inspect Work before, resources released, and Work after at every single iteration."

---

### Segment 3: Scenario B — Resource Request Waiting (2:15 – 3:15) | Presenter: Student 3
- **Action:** Navigate to **4. Resource Request Simulator**. Click **Scenario B: Exceeds Available (Waiting)**.
- **Speaking Script:**
  > "Next, we demonstrate Scenario B: a resource request that is valid but cannot be granted immediately.
  > In this scenario, process $P_0$ requests $[4, 0, 0]$. Notice $P_0$'s remaining Need is $[7, 4, 3]$, so $Request \le Need$ passes.
  > However, currently Available for resource A is only $3$. Therefore, $Request[0] > Available[0]$.
  > Following the Banker's specification, our simulator marks this as **REQUEST WAITING / NOT CURRENTLY AVAILABLE**.
  > Importantly, this is **not an error or invalid input**; it simply means the process must wait for other processes to release resources. Notice that our Allocation, Need, and Available matrices remain strictly untouched."

---

### Segment 4: Scenario C — Unsafe Request Denial & Rollback (3:15 – 4:30) | Presenter: Student 4
- **Action:** In **4. Resource Request Simulator**, click **Scenario C: Produces Unsafe State (Denied)**. Click **Execute Banker's Request Procedure**.
- **Speaking Script:**
  > "Now we demonstrate Scenario C: a request that appears available but leads to an UNSAFE state.
  > Here, $P_0$ requests $[0, 0, 2]$.
  > Step 2 checks: $[0, 0, 2] \le Need [7, 4, 3]$ (Pass).
  > Step 3 checks: $[0, 0, 2] \le Available [3, 3, 2]$ (Pass).
  > In Step 4, the algorithm tentatively simulates allocation: Available drops to $[3, 3, 0]$.
  > In Step 5, we execute the safety algorithm on this tentative state. With $Available_C = 0$, every single remaining process needs at least one unit of resource C. No process can even start!
  > Therefore, the tentative state is **UNSAFE**. In Step 7, the system denies the request with status **REQUEST DENIED** and rolls back the tentative changes. As shown in our comparison table, the original state is restored with zero corruption."

---

### Segment 5: Deadlock Detection & Recovery (4:30 – 5:30) | Presenter: Student 1 & 2
- **Action:** Navigate to **5. Deadlock Detection**.
- **Speaking Script:**
  > "We also emphasize that **Banker's Algorithm is Deadlock Avoidance, which is fundamentally distinct from Deadlock Detection**.
  > On this page, we model a textbook circular-wait condition: $P_0$ holds $R_0$ and waits for $R_1$, while $P_1$ holds $R_1$ and waits for $R_0$.
  > In our interactive Resource Allocation Graph (RAG), you can see the cycle $P_0 \to R_1 \to P_1 \to R_0 \to P_0$.
  > Running our multi-instance detection algorithm confirms status **DEADLOCK DETECTED** with deadlocked processes $\{P_0, P_1\}$.
  > For recovery, we select $P_0$ and click **Terminate Process & Recover**. $P_0$ is terminated, its held resources are reclaimed into Available, and our immediate detection re-run shows **SAFE: Deadlock Cleared**."

---

### Segment 6: Prevention, Analytical Results & Conclusion (5:30 – 6:00) | Presenter: Student 3 & 4
- **Action:** Navigate to **7. Test Cases and Analysis**.
- **Speaking Script:**
  > "Finally, in our Prevention section, we demonstrate how fixed resource ordering ($R_0 < R_1 < R_2$) mathematically prevents circular wait by enforcing a Directed Acyclic Graph.
  > In our Test Cases page, our **Required Analytical Results Table (TC1 through TC6)** is computed dynamically from real execution passes. All 6 main test cases and all 10 boundary tests pass with 100% compliance.
  > Furthermore, our automated `pytest` suite executes 30 unit tests verifying every edge case in less than 0.1 seconds.
  > Thank you, Professor. We are now ready for viva questions."

---

## 2. Likely Viva Questions & Technical Model Answers

### Question 1: What is the exact difference between Deadlock Prevention and Deadlock Avoidance?
**Model Answer:**
> "Deadlock Prevention imposes static design constraints on how resources can be requested to ensure that at least one of the four necessary Coffman conditions (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait) can never hold. An example is global resource ordering $R_0 < R_1 < R_2$.
> In contrast, Deadlock Avoidance does not restrict resource ordering; instead, it dynamically inspects every runtime resource request using the Banker's Algorithm to verify whether granting the request keeps the system in a SAFE state. If safe, it is granted; if unsafe, it is delayed or denied."

### Question 2: Why is an UNSAFE state not equivalent to a DEADLOCK?
**Model Answer:**
> "An unsafe state is not necessarily a deadlock; rather, it is a state from which the operating system can no longer *guarantee* that deadlock will not occur.
> In an unsafe state, if all processes simultaneously demand their declared maximum resources, a deadlock will result. However, if processes finish and release resources early without demanding their full maximum claims, the system may run to completion without ever experiencing an actual deadlock."

### Question 3: Why did you implement Deadlock Detection as a separate module from the Banker's Algorithm?
**Model Answer:**
> "Because they solve fundamentally different problems under different operational models.
> The Banker's Algorithm requires processes to declare their *Maximum Demand upfront* before execution and runs *proactively* on every request to avoid entering an unsafe state.
> Deadlock Detection runs *reactively* on systems where maximum claims are unknown. It uses an *Outstanding Request matrix* rather than a Maximum matrix, inspecting whether processes currently blocked waiting for resources can be satisfied with currently available resources."

### Question 4: Under what conditions is a cycle in a Resource Allocation Graph (RAG) both necessary and sufficient for deadlock?
**Model Answer:**
> "A cycle in a RAG is both necessary and sufficient for deadlock **if and only if every resource type has exactly one instance**.
> If any resource type has multiple instances, a cycle is a necessary condition, but it is **not sufficient**, because other resource instances held by processes outside the cycle might be released and break the deadlock. For multiple instances, the matrix-based detection algorithm must be used."

### Question 5: Why does strictly increasing resource ordering ($F(R_i) < F(R_j)$) prevent Circular Wait?
**Model Answer:**
> "Assume circular wait exists among processes $P_0, P_1, \dots, P_k$, where $P_i$ holds $R_{a_i}$ and requests $R_{a_{i+1}}$, and $P_k$ holds $R_{a_k}$ and requests $R_{a_0}$.
> Under the ordering rule, $F(R_{a_0}) < F(R_{a_1}) < F(R_{a_2}) < \dots < F(R_{a_k}) < F(R_{a_0})$.
> This implies $F(R_{a_0}) < F(R_{a_0})$, which is a mathematical impossibility. Thus, no directed cycle can ever form, making circular wait impossible."

### Question 6: What happens if a request exceeds a process's declared Need versus exceeding Available?
**Model Answer:**
> "If $Request[i] > Need[i]$, the request is classified as **INVALID INPUT** because the process has violated its initial maximum demand contract.
> If $Request[i] \le Need[i]$ but $Request[i] > Available$, the request is completely valid, but the system lacks the physical capacity to fulfill it immediately. It is classified as **REQUEST WAITING / NOT CURRENTLY AVAILABLE**, and the process must be placed on a wait queue without changing any matrix states."

### Question 7: How does your implementation ensure that denied requests leave the system state unchanged?
**Model Answer:**
> "In `algorithms/bankers.py` and `algorithms/resource_requests.py`, we strictly perform tentative allocation on cloned, isolated copies of the matrices:
> `temp_available = available[:]` and `temp_allocation = [list(r) for r in allocation]`.
> Only after the safety check succeeds is the allocation committed to the session state. If the safety check fails, the tentative copies are immediately discarded and the original state is returned with the boolean flag `state_unchanged = True`, which is formally asserted in our test suite."
