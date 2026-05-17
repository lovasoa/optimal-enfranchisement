"""Run all enfranchisement verification scripts."""

from __future__ import annotations

import search_counterexamples
import verify_counterexamples
import verify_replacement_results


def main() -> None:
    verify_counterexamples.main()
    verify_replacement_results.main()
    search_counterexamples.main()


if __name__ == "__main__":
    main()

