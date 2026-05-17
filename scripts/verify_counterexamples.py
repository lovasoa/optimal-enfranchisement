"""Verify the counterexamples in proof-codex-gpt5.5-xhigh.tex.

This script checks both original conjectures:

1. A full-support five-agent example where planner dictatorship beats every
   majority franchise.
2. A five-agent example where the unique optimal franchise is not high-stake,
   even after adding a small uniform component to guarantee full support.
"""

from __future__ import annotations

from fractions import Fraction

from common import (
    best_dictatorship_welfare,
    expected_welfare,
    format_franchise,
    is_full_support,
    is_high_stake,
    mix_distributions,
    normalize_weighted_states,
    odd_franchises,
    uniform_distribution,
    unique_argmax,
    welfare_table,
)


def verify_dictatorship_counterexample() -> None:
    """Check Conjecture 1 counterexample exactly."""
    n = 5
    stakes = (17, 8, 7, 4, 1)
    sparse_distribution = normalize_weighted_states(
        [
            ((1, 1, 1, 1, 0), 864),
            ((0, 1, 1, 1, 0), 51),
            ((1, 0, 1, 1, 0), 49),
            ((1, 1, 1, 0, 0), 21),
            ((1, 1, 0, 1, 0), 4),
            ((1, 0, 0, 1, 0), 3),
            ((1, 1, 0, 0, 0), 2),
            ((1, 0, 1, 1, 1), 1),
            ((1, 1, 1, 1, 1), 1),
            ((1, 0, 1, 0, 0), 1),
        ]
    )

    # The tiny uniform component enforces the paper's full-support assumption
    # without changing the strict ranking.
    distribution = mix_distributions(
        sparse_distribution,
        Fraction(9999, 10000),
        uniform_distribution(n),
        Fraction(1, 10000),
    )

    values = welfare_table(stakes, distribution)
    dictatorship_welfare, dictatorship_outcome = best_dictatorship_welfare(stakes, distribution)
    best_franchise = max(values.values())

    assert is_full_support(distribution, n)
    assert dictatorship_welfare > best_franchise

    print("Conjecture 1 counterexample")
    print(f"  stakes: {stakes}")
    print(f"  best dictatorship: constant {dictatorship_outcome}, welfare {dictatorship_welfare}")
    print(f"  best franchise welfare: {best_franchise}")
    print(f"  dictatorship margin: {dictatorship_welfare - best_franchise}")
    for franchise, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))[:6]:
        print(f"  {format_franchise(franchise):>13}: {value}")
    print()


def verify_high_stake_counterexample() -> None:
    """Check Conjecture 2 counterexample exactly."""
    n = 5
    stakes = (5, 4, 3, 2, 1)
    c_star = (0, 1, 3)  # {1,2,4} in the paper's labels.

    base_distribution = normalize_weighted_states(
        [
            ((0, 1, 1, 1, 0), 10),
            ((0, 1, 1, 0, 0), 3),
            ((0, 0, 1, 1, 1), 9),
        ]
    )
    base_values = welfare_table(stakes, base_distribution)
    base_margin = min(
        base_values[c_star] - value
        for franchise, value in base_values.items()
        if franchise != c_star
    )

    assert unique_argmax(base_values) == c_star
    assert base_margin == Fraction(3, 22)
    assert not is_high_stake(stakes, c_star)

    # Add a tiny uniform component so every state has positive probability.
    full_support_distribution = mix_distributions(
        base_distribution,
        Fraction(999, 1000),
        uniform_distribution(n),
        Fraction(1, 1000),
    )
    full_support_values = welfare_table(stakes, full_support_distribution)
    full_support_margin = min(
        full_support_values[c_star] - value
        for franchise, value in full_support_values.items()
        if franchise != c_star
    )

    assert is_full_support(full_support_distribution, n)
    assert unique_argmax(full_support_values) == c_star
    assert full_support_margin > 0

    print("Conjecture 2 counterexample")
    print(f"  unique optimum under base distribution: {format_franchise(c_star)}")
    print(f"  base margin: {base_margin}")
    print(f"  full-support margin: {full_support_margin}")
    print("  base welfare table, scaled by 22:")
    for franchise, value in sorted(base_values.items(), key=lambda item: (-item[1], item[0])):
        high = "high" if is_high_stake(stakes, franchise) else "not high"
        print(f"  {format_franchise(franchise):>13}: {str(22 * value):>3} ({high})")
    print()


def main() -> None:
    verify_dictatorship_counterexample()
    verify_high_stake_counterexample()
    print("All counterexample checks passed.")


if __name__ == "__main__":
    main()
