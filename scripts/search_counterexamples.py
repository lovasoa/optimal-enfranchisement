"""Search routines that reproduce the counterexamples.

These are not needed for the proofs, but they document how one can find the
examples mechanically.  The search space is deliberately small and uses exact
integer weights, so it runs quickly and deterministically.
"""

from __future__ import annotations

from fractions import Fraction

from common import (
    best_dictatorship_welfare,
    format_franchise,
    is_high_stake,
    mix_distributions,
    normalize_weighted_states,
    uniform_distribution,
    unique_argmax,
    welfare_table,
)


def find_dictatorship_counterexample() -> None:
    """Find a full-support case where dictatorship beats all franchises.

    The search scans a small hand-chosen support pattern and nearby integer
    probability weights.  Once it finds a strict sparse example, it adds a tiny
    uniform component to make the distribution full-support.
    """
    n = 5
    stakes = (17, 8, 7, 4, 1)
    support = [
        (1, 1, 1, 1, 0),
        (0, 1, 1, 1, 0),
        (1, 0, 1, 1, 0),
        (1, 1, 1, 0, 0),
        (1, 1, 0, 1, 0),
        (1, 0, 0, 1, 0),
        (1, 1, 0, 0, 0),
        (1, 0, 1, 1, 1),
        (1, 1, 1, 1, 1),
        (1, 0, 1, 0, 0),
    ]
    candidate_weights = [
        (864, 51, 49, 21, 4, 3, 2, 1, 1, 1),
        (100, 6, 6, 2, 1, 1, 1, 1, 1, 1),
        (90, 5, 5, 2, 1, 1, 1, 1, 1, 1),
    ]

    for weights in candidate_weights:
        sparse = normalize_weighted_states(zip(support, weights))
        full_support = mix_distributions(
            sparse,
            Fraction(9999, 10000),
            uniform_distribution(n),
            Fraction(1, 10000),
        )
        values = welfare_table(stakes, full_support)
        dictatorship_welfare, dictatorship_outcome = best_dictatorship_welfare(
            stakes, full_support
        )
        best_franchise_welfare = max(values.values())
        if dictatorship_welfare > best_franchise_welfare:
            print("Found dictatorship counterexample")
            print(f"  N={n}, stakes={stakes}")
            print(f"  sparse support weights={weights}")
            print(f"  best dictatorship=constant {dictatorship_outcome}")
            print(f"  dictatorship welfare={dictatorship_welfare}")
            print(f"  best franchise welfare={best_franchise_welfare}")
            print(f"  margin={dictatorship_welfare - best_franchise_welfare}")
            print()
            return

    raise RuntimeError("no dictatorship counterexample found in the candidate grid")


def find_non_high_stake_counterexample() -> None:
    """Reproduce a sparse distribution with a unique non-high-stake optimum.

    Earlier exploratory searches scanned three-state supports and integer
    weights.  The known minimal example is checked directly here so the script
    remains fast and deterministic.
    """
    n = 5
    stakes = (5, 4, 3, 2, 1)
    target = (0, 1, 3)  # {1,2,4}
    support = [
        (0, 1, 1, 1, 0),
        (0, 1, 1, 0, 0),
        (0, 0, 1, 1, 1),
    ]
    raw_weights = (10, 3, 9)
    distribution = normalize_weighted_states(zip(support, raw_weights))
    values = welfare_table(stakes, distribution)

    if unique_argmax(values) != target or is_high_stake(stakes, target):
        raise RuntimeError("known non-high-stake counterexample did not verify")

    margin = min(
        values[target] - value
        for franchise, value in values.items()
        if franchise != target
    )
    print("Found non-high-stake counterexample")
    print(f"  stakes={stakes}")
    print(f"  unique optimum={format_franchise(target)}")
    print(f"  margin={margin}")
    print("  weighted states:")
    for state, weight in zip(support, raw_weights):
        print(f"    weight {weight:>2}: {state}")
    print("  top franchises:")
    for franchise, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:5]:
        high = "high" if is_high_stake(stakes, franchise) else "not high"
        print(f"    {format_franchise(franchise):>9}: {value} ({high})")
    print()


def main() -> None:
    find_dictatorship_counterexample()
    find_non_high_stake_counterexample()
    print("Counterexample searches completed.")


if __name__ == "__main__":
    main()
