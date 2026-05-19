To find a meaningful and more general joint sufficient condition that subsumes both **symmetric opinions** and **equal stakes**, we can analyze why voting fails against paternalism (planner's dictatorship) in the asymmetric case, as demonstrated by the counter-example.

Paternalism beats voting when a **high-stake minority** gets overridden by a **low-stake majority**. In the counter-example, there is a state where a majority of agents prefer outcome `0`, but the minority who prefer `1` have vastly higher stakes. Because unweighted voting cannot reflect preference intensities, it chooses `0`, leading to lower expected aggregate welfare than a paternalistic mandate of `1`.

To prevent this mismatch, we can define a joint condition using the **empirical covariance** between individual stakes and their alignment with the collective majority.

---

### 1. Mathematical Formulation

Let $\mathcal{N} = \{1, \dots, N\}$ be a population of odd size $N$. Let $Y_{\mathcal{N}}$ be the outcome of the universal franchise majority vote. The expected aggregate welfare difference between the universal franchise and a planner's dictatorship of $y=1$ is:


$$\mathbb{E}[U_{\mathcal{N}}] - \mathbb{E}[V(1)] = \sum_{i \in \mathcal{N}} \Delta_i \Big( P[X_i = Y_{\mathcal{N}}] - P[X_i = 1] \Big)$$

By expanding the joint probabilities, the difference for each agent simplifies to their alignment when the majority chooses `0`:


$$P[X_i = Y_{\mathcal{N}}] - P[X_i = 1] = P[X_i = 0, Y_{\mathcal{N}} = 0] - P[X_i = 1, Y_{\mathcal{N}} = 0] = \mathbb{E}[1_{Y_{\mathcal{N}} = 0}(1 - 2X_i)]$$

Let us define the **majority-alignment vectors** $A$ and $B$ for each agent $i$:

* $A_i = \mathbb{E}[1_{Y_{\mathcal{N}} = 0}(1 - 2X_i)]$ *(Tendency to align with a '0' majority)*
* $B_i = \mathbb{E}[1_{Y_{\mathcal{N}} = 1}(2X_i - 1)]$ *(Tendency to align with a '1' majority)*

By definition of a strict majority vote, when $Y_{\mathcal{N}} = 0$, more than half the population votes `0`, meaning $\sum_{i\in\mathcal{N}} (1 - 2X_i) \ge 1$ point-wise. Under the full support assumption, the unweighted sums of these vectors across the population are always strictly positive:


$$\sum_{i \in \mathcal{N}} A_i > 0 \quad \text{and} \quad \sum_{i \in \mathcal{N}} B_i > 0$$

---

### 2. The Generalized Sufficient Condition

For franchised voting to strictly dominate both paternalistic outcomes ($y=1$ and $y=0$), we require $\sum_i \Delta_i A_i > 0$ and $\sum_i \Delta_i B_i > 0$. Using the definition of empirical covariance, we can rewrite the welfare gain as:


$$\sum_{i \in \mathcal{N}} \Delta_i A_i = N \cdot \text{Cov}(\Delta, A) + \frac{1}{N}\left(\sum_{i \in \mathcal{N}} \Delta_i\right)\left(\sum_{i \in \mathcal{N}} A_i\right)$$

Because $\sum_i \Delta_i > 0$ and $\sum_i A_i > 0$, the baseline right-hand term is always strictly positive. Therefore, a joint sufficient condition for franchised voting to dominate paternalism is:

$$\text{Cov}(\Delta, A) \ge 0 \quad \text{and} \quad \text{Cov}(\Delta, B) \ge 0$$

(Alternatively, if the agents are ordered by decreasing stakes $\Delta_1 \ge \dots \ge \Delta_N$, the condition is satisfied if $A_i$ and $B_i$ are also **co-monotone**—i.e., decreasing sequences in $i$, which guarantees non-negative covariance by Chebyshev's sum inequality).

---

### 3. How It Subsumes the Two Base Cases

This covariance condition perfectly generalizes and unifies both of your known benchmarks:

1. 
**Symmetric Opinions Case:** If the distribution of opinions is permutation invariant , the probability of any agent aligning with the majority is identical ($A_i = \bar{A}$ and $B_i = \bar{B}$ for all $i$). Because $A$ and $B$ are constant vectors, their covariance with **any** stake distribution $\Delta$ is exactly zero ($\text{Cov}(\Delta, A) = 0 \ge 0$).


2. **Equal Stakes Case:** If all stakes are equal ($\Delta_i = \bar{\Delta}$ for all $i$), the vector $\Delta$ becomes a constant. The covariance of a constant vector with **any** opinion distribution's alignment vectors $A$ and $B$ is also exactly zero ($\text{Cov}(\Delta, A) = 0 \ge 0$).

---

### 4. Meaningful Intuition

In plain economic terms, this condition requires that **agents with larger stakes must be on average more aligned with (or better predictors of) the collective majority opinion than agents with lower stakes**.

If high-stake individuals naturally move with the political majority, a simple unweighted franchise safely protects their intense preferences. Paternalism is only capable of beating democracy when this condition is violated—meaning the distribution creates an adversarial environment where the individuals care the most but are systematically trapped in the minority.
