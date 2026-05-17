"""Shared utilities for the enfranchisement calculations.

The LaTeX notes use 1-indexed agent labels.  The Python code uses normal
0-indexed tuples internally and converts labels only when printing.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb
from typing import Iterable, Mapping

State = tuple[int, ...]
Franchise = tuple[int, ...]
Distribution = Mapping[State, Fraction]


def all_states(n: int) -> list[State]:
    """Return all binary opinion profiles for n agents."""
    return list(product((0, 1), repeat=n))


def odd_franchises(n: int) -> list[Franchise]:
    """Return all nonempty odd-size franchises."""
    return [
        tuple(franchise)
        for size in range(1, n + 1, 2)
        for franchise in combinations(range(n), size)
    ]


def format_franchise(franchise: Franchise) -> str:
    """Format a 0-indexed franchise with the 1-indexed labels used in the paper."""
    return "{" + ",".join(str(i + 1) for i in franchise) + "}"


def majority_outcome(state: State, franchise: Franchise) -> int:
    """Strict majority outcome for an odd-size franchise."""
    return int(sum(state[i] for i in franchise) > len(franchise) / 2)


def welfare_for_state(stakes: tuple[int, ...], franchise: Franchise, state: State) -> int:
    """Aggregate welfare in one realized opinion profile."""
    outcome = majority_outcome(state, franchise)
    return sum(stake for stake, opinion in zip(stakes, state) if opinion == outcome)


def expected_welfare(
    stakes: tuple[int, ...],
    distribution: Distribution,
    franchise: Franchise,
) -> Fraction:
    """Expected aggregate welfare under a probability distribution over states."""
    return sum(
        probability * welfare_for_state(stakes, franchise, state)
        for state, probability in distribution.items()
    )


def normalize_weighted_states(weighted_states: Iterable[tuple[State, int]]) -> dict[State, Fraction]:
    """Normalize positive integer state weights into a probability distribution."""
    pairs = list(weighted_states)
    total = sum(weight for _, weight in pairs)
    if total <= 0:
        raise ValueError("total probability weight must be positive")
    return {state: Fraction(weight, total) for state, weight in pairs}


def uniform_distribution(n: int) -> dict[State, Fraction]:
    """Uniform distribution on all binary profiles."""
    probability = Fraction(1, 2**n)
    return {state: probability for state in all_states(n)}


def iid_bernoulli_distribution(n: int, p: Fraction) -> dict[State, Fraction]:
    """Distribution of n independent Bernoulli(p) opinions."""
    return {
        state: (p ** sum(state)) * ((1 - p) ** (n - sum(state)))
        for state in all_states(n)
    }


def mix_distributions(
    first: Distribution,
    first_weight: Fraction,
    second: Distribution,
    second_weight: Fraction,
) -> dict[State, Fraction]:
    """Return first_weight * first + second_weight * second."""
    states = set(first) | set(second)
    return {
        state: first_weight * first.get(state, Fraction(0))
        + second_weight * second.get(state, Fraction(0))
        for state in states
    }


def is_full_support(distribution: Distribution, n: int) -> bool:
    """Check that every binary profile has positive probability."""
    return all(distribution.get(state, Fraction(0)) > 0 for state in all_states(n))


def is_high_stake(stakes: tuple[int, ...], franchise: Franchise) -> bool:
    """Weak high-stake condition from the conjecture file."""
    n = len(stakes)
    if len(franchise) == n:
        return True
    insiders = set(franchise)
    outsiders = set(range(n)) - insiders
    return all(stakes[i] >= stakes[j] for i in insiders for j in outsiders)


def welfare_table(stakes: tuple[int, ...], distribution: Distribution) -> dict[Franchise, Fraction]:
    """Compute expected welfare for every admissible franchise."""
    return {
        franchise: expected_welfare(stakes, distribution, franchise)
        for franchise in odd_franchises(len(stakes))
    }


def expected_weight_for_outcome_one(
    stakes: tuple[int, ...],
    distribution: Distribution,
) -> Fraction:
    """Expected stake weight of agents whose opinion is 1."""
    return sum(
        probability * sum(stake for stake, opinion in zip(stakes, state) if opinion == 1)
        for state, probability in distribution.items()
    )


def best_dictatorship_welfare(
    stakes: tuple[int, ...],
    distribution: Distribution,
) -> tuple[Fraction, int]:
    """Return the best independent dictatorship welfare and its constant outcome.

    The objective is linear in q, so an optimal planner dictatorship is always
    q=0 or q=1.  The returned outcome is the better of these two constants.
    """
    outcome_one = expected_weight_for_outcome_one(stakes, distribution)
    outcome_zero = sum(stakes) - outcome_one
    if outcome_one >= outcome_zero:
        return outcome_one, 1
    return outcome_zero, 0


def unique_argmax(values: Mapping[Franchise, Fraction]) -> Franchise | None:
    """Return the unique maximizer, or None if there is a tie."""
    best_value = max(values.values())
    best = [key for key, value in values.items() if value == best_value]
    return best[0] if len(best) == 1 else None


def alpha_beta_iid(m: int, p: Fraction) -> tuple[Fraction, Fraction]:
    """Return insider and outsider success probabilities for iid Bernoulli(p).

    The franchise size m must be odd.  The formulas match the notation
    alpha_m and beta_m in suggestions-codex-gpt5.5-xhigh.tex.
    """
    if m % 2 != 1 or m < 1:
        raise ValueError("m must be a positive odd integer")
    h = (m - 1) // 2

    # Insider: condition on the other m - 1 voters.
    alpha = p * sum(binomial_probability(m - 1, t, p) for t in range(h, m))
    alpha += (1 - p) * sum(binomial_probability(m - 1, t, p) for t in range(0, h + 1))

    # Outsider: compare an independent outsider's opinion with the franchise majority.
    beta = p * sum(binomial_probability(m, t, p) for t in range(h + 1, m + 1))
    beta += (1 - p) * sum(binomial_probability(m, t, p) for t in range(0, h + 1))
    return alpha, beta


def binomial_probability(n: int, k: int, p: Fraction) -> Fraction:
    """Exact binomial probability P[Binomial(n, p) = k]."""
    return Fraction(comb(n, k), 1) * (p**k) * ((1 - p) ** (n - k))


def insider_advantage_formula(m: int, p: Fraction) -> Fraction:
    """Closed-form alpha_m - beta_m from the iid insider-advantage lemma."""
    h = (m - 1) // 2
    return 2 * p * (1 - p) * binomial_probability(m - 1, h, p)


def balanced_prefix_score(stakes: tuple[int, ...], m: int) -> Fraction:
    """Score a highest-stake prefix of odd size m under balanced iid opinions."""
    if m % 2 != 1:
        raise ValueError("m must be odd")
    prefix_stake = sum(stakes[:m])
    central = Fraction(comb(m - 1, (m - 1) // 2), 2 ** (m - 1))
    a_m = Fraction(1, 2) * central
    return a_m * prefix_stake
