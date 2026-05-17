"""Explore smaller counterexamples before hard-coding them in the paper.

This script is intentionally exploratory: it uses scipy's linear-programming
solver to search for sparse distributions that violate the conjectures, then
prints exact integer-weight candidates that can be checked by the dependency-
free verification scripts.

Run with:

    UV_CACHE_DIR=/private/tmp/uv-cache uv run --with scipy python scripts/explore_counterexamples.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Callable, Iterable

try:
    from scipy.optimize import linprog
except ModuleNotFoundError as exc:  # pragma: no cover - exercised manually.
    raise SystemExit(
        "scipy is required for this exploratory script. Run it with:\n"
        "  UV_CACHE_DIR=/private/tmp/uv-cache uv run --with scipy "
        "python scripts/explore_counterexamples.py"
    ) from exc

from common import (
    State,
    all_states,
    best_dictatorship_welfare,
    format_franchise,
    is_high_stake,
    normalize_weighted_states,
    odd_franchises,
    unique_argmax,
    welfare_for_state,
    welfare_table,
)


@dataclass(frozen=True)
class WeightedCandidate:
    stakes: tuple[int, ...]
    support: tuple[tuple[State, int], ...]
    margin: Fraction
    label: str

    @property
    def total_weight(self) -> int:
        return sum(weight for _, weight in self.support)


def descending_stakes(n: int, max_stake: int) -> Iterable[tuple[int, ...]]:
    """Generate strictly decreasing positive stake vectors."""
    for stakes in combinations(range(1, max_stake + 1), n):
        yield tuple(reversed(stakes))


def one_weight(stakes: tuple[int, ...], state: State) -> int:
    """Stake weight agreeing with the constant-one dictatorship."""
    return sum(stake for stake, opinion in zip(stakes, state) if opinion == 1)


def solve_dictatorship_lp(stakes: tuple[int, ...]) -> tuple[float, list[float]]:
    """Maximize the margin by which constant one beats every franchise."""
    states = all_states(len(stakes))
    franchises = odd_franchises(len(stakes))
    variable_count = len(states) + 1
    margin_index = len(states)

    objective = [0.0] * variable_count
    objective[margin_index] = -1.0

    constraints: list[list[float]] = []
    bounds: list[float] = []

    for franchise in franchises:
        row = [
            welfare_for_state(stakes, franchise, state) - one_weight(stakes, state)
            for state in states
        ]
        row.append(1.0)
        constraints.append(row)
        bounds.append(0.0)

    total_stake = sum(stakes)
    dictatorship_one_minus_zero = [
        total_stake - 2 * one_weight(stakes, state)
        for state in states
    ]
    dictatorship_one_minus_zero.append(0.0)
    constraints.append(dictatorship_one_minus_zero)
    bounds.append(0.0)

    result = linprog(
        c=objective,
        A_ub=constraints,
        b_ub=bounds,
        A_eq=[[1.0] * len(states) + [0.0]],
        b_eq=[1.0],
        bounds=[(0.0, 1.0)] * len(states) + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        return 0.0, []
    return float(result.x[margin_index]), list(result.x[: len(states)])


def lp_support(probabilities: list[float], tolerance: float = 1e-8) -> tuple[int, ...]:
    """Return support indices used by a numerical LP solution."""
    return tuple(index for index, probability in enumerate(probabilities) if probability > tolerance)


def integer_weight_search(
    stakes: tuple[int, ...],
    support: tuple[State, ...],
    margin_coefficients: Callable[[tuple[int, ...], State], list[int]],
    max_total_weight: int,
    label: str,
) -> WeightedCandidate | None:
    """Find the best small exact integer weights on a fixed support."""
    best: WeightedCandidate | None = None

    coefficient_rows = [margin_coefficients(stakes, state) for state in support]
    for weights in positive_weight_vectors(len(support), max_total_weight):
        total = sum(weights)
        scaled_margin = min(
            sum(weight * row[index] for weight, row in zip(weights, coefficient_rows))
            for index in range(len(coefficient_rows[0]))
        )
        if scaled_margin <= 0:
            continue

        margin = Fraction(scaled_margin, total)
        candidate = WeightedCandidate(
            stakes=stakes,
            support=tuple(zip(support, weights)),
            margin=margin,
            label=label,
        )
        if best is None or (candidate.total_weight, -candidate.margin) < (
            best.total_weight,
            -best.margin,
        ):
            best = candidate
    return best


def positive_weight_vectors(length: int, max_total_weight: int) -> Iterable[tuple[int, ...]]:
    """Generate positive integer vectors with bounded total weight."""
    if length <= 0:
        return

    def extend(prefix: tuple[int, ...], remaining_length: int, remaining_total: int) -> Iterable[tuple[int, ...]]:
        if remaining_length == 1:
            for value in range(1, remaining_total + 1):
                yield prefix + (value,)
            return

        for value in range(1, remaining_total - remaining_length + 2):
            yield from extend(prefix + (value,), remaining_length - 1, remaining_total - value)

    yield from extend((), length, max_total_weight)


def dictatorship_margin_coefficients(stakes: tuple[int, ...], state: State) -> list[int]:
    """Margins of constant one against each odd franchise in one state."""
    return [
        one_weight(stakes, state) - welfare_for_state(stakes, franchise, state)
        for franchise in odd_franchises(len(stakes))
    ]


def find_small_dictatorship_examples(
    ns: tuple[int, ...],
    max_stake: int,
    max_support: int,
    max_total_weight: int,
) -> list[WeightedCandidate]:
    """Search for simple dictatorship counterexamples with small N and stakes."""
    candidates: list[WeightedCandidate] = []
    states_by_n = {n: all_states(n) for n in ns}

    for n in ns:
        for stakes in descending_stakes(n, max_stake=max_stake):
            margin, probabilities = solve_dictatorship_lp(stakes)
            if margin <= 1e-7:
                continue

            support_indices = lp_support(probabilities)
            support = tuple(states_by_n[n][index] for index in support_indices)
            if len(support) > max_support:
                continue

            candidate = integer_weight_search(
                stakes,
                support,
                dictatorship_margin_coefficients,
                max_total_weight=max_total_weight,
                label=f"dictatorship n={n}",
            )
            if candidate is not None:
                candidates.append(candidate)

    return sorted(candidates, key=lambda candidate: (len(candidate.stakes), len(candidate.support), candidate.total_weight, -candidate.margin))


def high_stake_margin_coefficients(
    stakes: tuple[int, ...],
    target: tuple[int, ...],
) -> Callable[[tuple[int, ...], State], list[int]]:
    """Build target-franchise margin rows for non-high-stake searches."""
    competitors = [franchise for franchise in odd_franchises(len(stakes)) if franchise != target]

    def coefficients(_: tuple[int, ...], state: State) -> list[int]:
        target_welfare = welfare_for_state(stakes, target, state)
        return [
            target_welfare - welfare_for_state(stakes, competitor, state)
            for competitor in competitors
        ]

    return coefficients


def solve_target_franchise_lp(
    stakes: tuple[int, ...],
    target: tuple[int, ...],
) -> tuple[float, list[float]]:
    """Maximize the margin by which target beats every other franchise."""
    states = all_states(len(stakes))
    competitors = [franchise for franchise in odd_franchises(len(stakes)) if franchise != target]
    variable_count = len(states) + 1
    margin_index = len(states)

    objective = [0.0] * variable_count
    objective[margin_index] = -1.0

    constraints: list[list[float]] = []
    bounds: list[float] = []

    for competitor in competitors:
        row = [
            welfare_for_state(stakes, competitor, state) - welfare_for_state(stakes, target, state)
            for state in states
        ]
        row.append(1.0)
        constraints.append(row)
        bounds.append(0.0)

    result = linprog(
        c=objective,
        A_ub=constraints,
        b_ub=bounds,
        A_eq=[[1.0] * len(states) + [0.0]],
        b_eq=[1.0],
        bounds=[(0.0, 1.0)] * len(states) + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        return 0.0, []
    return float(result.x[margin_index]), list(result.x[: len(states)])


def find_small_non_high_stake_examples(
    ns: tuple[int, ...],
    max_stake: int,
    max_support: int,
    max_total_weight: int,
) -> list[WeightedCandidate]:
    """Search exact small-support examples where the optimum is not high-stake."""
    candidates: list[WeightedCandidate] = []

    for n in ns:
        states = all_states(n)
        franchises = odd_franchises(n)
        for stakes in descending_stakes(n, max_stake=max_stake):
            for target in franchises:
                if is_high_stake(stakes, target):
                    continue

                margin, probabilities = solve_target_franchise_lp(stakes, target)
                if margin <= 1e-7:
                    continue

                support_indices = lp_support(probabilities)
                support = tuple(states[index] for index in support_indices)
                if len(support) > max_support:
                    continue

                candidate = integer_weight_search(
                    stakes,
                    support,
                    high_stake_margin_coefficients(stakes, target),
                    max_total_weight=max_total_weight,
                    label=f"non-high-stake target={format_franchise(target)}",
                )
                if candidate is None:
                    continue

                distribution = normalize_weighted_states(candidate.support)
                values = welfare_table(stakes, distribution)
                if unique_argmax(values) == target:
                    candidates.append(candidate)

    return sorted(candidates, key=lambda candidate: (len(candidate.stakes), len(candidate.support), candidate.total_weight, -candidate.margin))


def print_candidate(candidate: WeightedCandidate) -> None:
    """Print one exact candidate in a paper-friendly form."""
    distribution = normalize_weighted_states(candidate.support)
    values = welfare_table(candidate.stakes, distribution)
    best_dictatorship, outcome = best_dictatorship_welfare(candidate.stakes, distribution)

    print(candidate.label)
    print(f"  stakes={candidate.stakes}")
    print(f"  total weight={candidate.total_weight}")
    print(f"  certified sparse margin={candidate.margin}")
    print("  support:")
    for state, weight in candidate.support:
        print(f"    {weight:>2}  {state}")
    if candidate.label.startswith("dictatorship"):
        print(f"  best dictatorship=constant {outcome}, welfare={best_dictatorship}")
        print(f"  best franchise welfare={max(values.values())}")
    else:
        target = unique_argmax(values)
        print(f"  unique optimum={format_franchise(target) if target else None}")
    print("  top franchises:")
    for franchise, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:6]:
        high = "high" if is_high_stake(candidate.stakes, franchise) else "not high"
        print(f"    {format_franchise(franchise):>13}: {value} ({high})")
    print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for scoped exploratory runs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--problem",
        choices=("all", "dictatorship", "non-high-stake"),
        default="all",
        help="which counterexample family to search",
    )
    parser.add_argument(
        "--n",
        type=int,
        nargs="+",
        default=[3, 5],
        help="population sizes to search",
    )
    parser.add_argument(
        "--max-stake",
        type=int,
        default=8,
        help="largest integer stake allowed in descending stake vectors",
    )
    parser.add_argument(
        "--max-support",
        type=int,
        default=5,
        help="largest LP support to convert to exact integer weights",
    )
    parser.add_argument(
        "--max-total-weight",
        type=int,
        default=50,
        help="largest total integer support weight to try",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="number of candidates to print for each search",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ns = tuple(args.n)

    if args.problem in ("all", "dictatorship"):
        dictatorship_candidates = find_small_dictatorship_examples(
            ns,
            max_stake=args.max_stake,
            max_support=args.max_support,
            max_total_weight=args.max_total_weight,
        )

        print("Small dictatorship candidates")
        for candidate in dictatorship_candidates[: args.top]:
            print_candidate(candidate)

    if args.problem in ("all", "non-high-stake"):
        non_high_stake_candidates = find_small_non_high_stake_examples(
            ns,
            max_stake=args.max_stake,
            max_support=args.max_support,
            max_total_weight=args.max_total_weight,
        )

        print("Small non-high-stake candidates")
        for candidate in non_high_stake_candidates[: args.top]:
            print_candidate(candidate)


if __name__ == "__main__":
    main()
