from __future__ import annotations

import argparse
import sys

from rde_eval.evaluator import evaluate_samples, load_samples, write_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic RDE scaffold evaluation.")
    parser.add_argument("--input", required=True, help="Input JSONL sample file.")
    parser.add_argument("--output", required=True, help="Output JSONL result file.")
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        samples = load_samples(args.input)
        results = evaluate_samples(samples)
        write_results(args.output, results)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Evaluated {len(results)} samples -> {args.output}")


if __name__ == "__main__":
    main()
