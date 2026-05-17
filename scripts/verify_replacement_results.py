"""Verify the replacement results in suggestions-codex-gpt5.5-xhigh.tex.

The proofs in the note are symbolic.  This script provides independent
finite checks of the formulas and examples using exact rational arithmetic.
"""

from __future__ import annotations

from fractions import Fraction

from common import (
    alpha_beta_iid,
    balanced_prefix_score,
    expected_welfare,
    format_franchise,
    iid_bernoulli_distribution,
    insider_advantage_formula,
    is_high_stake,
    odd_franchises,
    unique_argmax,
    welfare_table,
)


def check_insider_advantage_formula() -> None:
    """Check alpha_m - beta_m against the closed-form binomial expression."""
    probabilities = [Fraction(1, 10), Fraction(3, 10), Fraction(1, 2), Fraction(9, 10)]
    for p in probabilities:
        for m in range(1, 16, 2):
            alpha, beta = alpha_beta_iid(m, p)
            assert alpha - beta == insider_advantage_formula(m, p)
            assert alpha > beta
    print("Insider-advantage identity checked for sample p and m values.")


def check_iid_high_stake_by_enumeration() -> None:
    """Enumerate small iid cases and confirm all optimizers are high-stake."""
    examples = [
        ((5, 4, 3, 2, 1), Fraction(1, 2)),
        ((8, 5, 4, 1, 1), Fraction(3, 10)),
        ((9, 7, 3, 2, 1, 1, 0), Fraction(7, 10)),
    ]
    for stakes, p in examples:
        distribution = iid_bernoulli_distribution(len(stakes), p)
        values = welfare_table(stakes, distribution)
        best_value = max(values.values())
        optimizers = [franchise for franchise, value in values.items() if value == best_value]
        assert all(is_high_stake(stakes, franchise) for franchise in optimizers)
    print("Iid high-stake theorem checked by enumeration on sample cases.")


def check_balanced_dictatorship_comparison() -> None:
    """Check that balanced iid franchises weakly beat every independent dictatorship."""
    stakes = (6, 5, 3, 2, 1)
    distribution = iid_bernoulli_distribution(len(stakes), Fraction(1, 2))
    dictatorship_welfare = Fraction(sum(stakes), 2)

    for franchise in odd_franchises(len(stakes)):
        assert expected_welfare(stakes, distribution, franchise) >= dictatorship_welfare
    print("Balanced dictatorship comparison checked on a sample stake vector.")


def check_balanced_prefix_rule() -> None:
    """Compare exhaustive optimization with the prefix score formula."""
    stakes = (5, 4, 3, 2, 1)
    distribution = iid_bernoulli_distribution(len(stakes), Fraction(1, 2))
    values = welfare_table(stakes, distribution)
    exhaustive_best = unique_argmax(values)

    prefix_scores = {
        tuple(range(m)): balanced_prefix_score(stakes, m)
        for m in range(1, len(stakes) + 1, 2)
    }
    score_best = unique_argmax(prefix_scores)

    assert exhaustive_best == score_best
    print(f"Balanced prefix rule checked; best prefix is {format_franchise(score_best)}.")


def check_equal_stakes_full_franchise() -> None:
    """Check the equal-stakes corollary via the prefix score formula."""
    for n in range(1, 22, 2):
        stakes = tuple(1 for _ in range(n))
        prefix_scores = {
            tuple(range(m)): balanced_prefix_score(stakes, m)
            for m in range(1, n + 1, 2)
        }
        assert unique_argmax(prefix_scores) == tuple(range(n))
    print("Equal-stakes full-franchise corollary checked up to N=21.")


def main() -> None:
    check_insider_advantage_formula()
    check_iid_high_stake_by_enumeration()
    check_balanced_dictatorship_comparison()
    check_balanced_prefix_rule()
    check_equal_stakes_full_franchise()
    print("All replacement-result checks passed.")


if __name__ == "__main__":
    main()
