#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

# Repo-root auf den Importpfad legen
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zip_generator.generator import generate_puzzle  # noqa: E402


def build_run_record(requested_seed: int, result: dict) -> dict:
    record = {
        "requested_seed": requested_seed,
        "error": result.get("error", False),
    }

    if result.get("error"):
        record["message"] = result.get("message", "Unknown error")
        return record

    record.update(
        {
            "seed": result.get("seed"),
            "attempts": result.get("attempts"),
            "scanned_attempts": result.get("scanned_attempts"),
            "collected_candidates": result.get("collected_candidates"),
            "target_candidate_pool_size": result.get("target_candidate_pool_size"),
            "difficulty_score_raw": result.get("difficulty_score_raw"),
            "difficulty_score": result.get("difficulty_score"),
            "solver_steps": result.get("solver_steps"),
            "branch_count": result.get("branch_count"),
            "dead_end_count": result.get("dead_end_count"),
            "forced_move_count": result.get("forced_move_count"),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "checkpoint_count": result.get("checkpoint_count"),
            "wall_count": len(result.get("walls", [])),
        }
    )
    return record


def mean_or_none(values: list[float | int]) -> float | None:
    return round(statistics.mean(values), 2) if values else None


def print_progress(current: int, total: int, start_time: float) -> None:
    width = 30
    filled = int(width * current / total) if total else width
    bar = "#" * filled + "-" * (width - filled)
    elapsed = time.time() - start_time
    rate = current / elapsed if elapsed > 0 else 0
    remaining = (total - current) / rate if rate > 0 else 0
    message = (
        f"\rProgress: [{bar}] {current}/{total} "
        f"({current / total * 100:5.1f}%) "
        f"Elapsed: {elapsed:5.1f}s ETA: {remaining:5.1f}s"
    )
    print(message, end="", file=sys.stderr, flush=True)
    if current >= total:
        print(file=sys.stderr, flush=True)


def summarize_runs(difficulty: str, start_seed: int, count: int, seed_step: int, runs: list[dict]) -> dict:
    successes = [run for run in runs if not run["error"]]
    failures = [run for run in runs if run["error"]]

    summary = {
        "difficulty": difficulty,
        "start_seed": start_seed,
        "count": count,
        "seed_step": seed_step,
        "success_count": len(successes),
        "failure_count": len(failures),
        "runs": runs,
    }

    if not successes:
        return summary

    def vals(key: str) -> list[int | float]:
        return [run[key] for run in successes if run.get(key) is not None]

    summary["metrics"] = {
        "avg_attempts": mean_or_none(vals("attempts")),
        "avg_scanned_attempts": mean_or_none(vals("scanned_attempts")),
        "avg_collected_candidates": mean_or_none(vals("collected_candidates")),
        "avg_difficulty_score": mean_or_none(vals("difficulty_score")),
        "min_difficulty_score": min(vals("difficulty_score")),
        "max_difficulty_score": max(vals("difficulty_score")),
        "avg_solver_steps": mean_or_none(vals("solver_steps")),
        "avg_branch_count": mean_or_none(vals("branch_count")),
        "avg_dead_end_count": mean_or_none(vals("dead_end_count")),
        "avg_forced_move_count": mean_or_none(vals("forced_move_count")),
        "avg_elapsed_seconds": mean_or_none(vals("elapsed_seconds")),
        "min_elapsed_seconds": min(vals("elapsed_seconds")),
        "max_elapsed_seconds": max(vals("elapsed_seconds")),
        "avg_checkpoint_count": mean_or_none(vals("checkpoint_count")),
        "avg_wall_count": mean_or_none(vals("wall_count")),
    }

    ranked = sorted(successes, key=lambda run: run["difficulty_score_raw"])
    summary["easiest_run"] = ranked[0]
    summary["hardest_run"] = ranked[-1]
    summary["median_run"] = ranked[len(ranked) // 2]

    return summary


def run_benchmark(difficulty: str, start_seed: int, count: int, seed_step: int) -> dict:
    runs: list[dict] = []
    started = time.time()
    for offset in range(count):
        requested_seed = start_seed + (offset * seed_step)
        result = generate_puzzle(difficulty=difficulty, seed=requested_seed)
        runs.append(build_run_record(requested_seed, result))
        print_progress(offset + 1, count, started)
    return summarize_runs(difficulty, start_seed, count, seed_step, runs)


def print_human_summary(summary: dict) -> None:
    print(f"Difficulty:           {summary['difficulty']}")
    print(f"Start seed:           {summary['start_seed']}")
    print(f"Count:                {summary['count']}")
    print(f"Seed step:            {summary['seed_step']}")
    print(f"Successes:            {summary['success_count']}")
    print(f"Failures:             {summary['failure_count']}")

    metrics = summary.get("metrics")
    if not metrics:
        return

    print()
    print("Averages")
    print(f"  Attempts:           {metrics['avg_attempts']}")
    print(f"  Scanned attempts:   {metrics['avg_scanned_attempts']}")
    print(f"  Candidates:         {metrics['avg_collected_candidates']}")
    print(f"  Difficulty score:   {metrics['avg_difficulty_score']}")
    print(f"  Solver steps:       {metrics['avg_solver_steps']}")
    print(f"  Branch count:       {metrics['avg_branch_count']}")
    print(f"  Dead ends:          {metrics['avg_dead_end_count']}")
    print(f"  Forced moves:       {metrics['avg_forced_move_count']}")
    print(f"  Elapsed seconds:    {metrics['avg_elapsed_seconds']}")
    print(f"  Checkpoints:        {metrics['avg_checkpoint_count']}")
    print(f"  Walls:              {metrics['avg_wall_count']}")

    print()
    print("Difficulty score range")
    print(f"  Min:                {metrics['min_difficulty_score']}")
    print(f"  Max:                {metrics['max_difficulty_score']}")

    hardest = summary["hardest_run"]
    easiest = summary["easiest_run"]
    median = summary["median_run"]

    print()
    print("Representative runs")
    print(
        f"  Easiest:            requested_seed={easiest['requested_seed']}, "
        f"used_seed={easiest['seed']}, score={easiest['difficulty_score']}"
    )
    print(
        f"  Median:             requested_seed={median['requested_seed']}, "
        f"used_seed={median['seed']}, score={median['difficulty_score']}"
    )
    print(
        f"  Hardest:            requested_seed={hardest['requested_seed']}, "
        f"used_seed={hardest['seed']}, score={hardest['difficulty_score']}"
    )


def write_csv(path: Path, runs: list[dict]) -> None:
    fieldnames = [
        "requested_seed",
        "error",
        "message",
        "seed",
        "attempts",
        "scanned_attempts",
        "collected_candidates",
        "target_candidate_pool_size",
        "difficulty_score_raw",
        "difficulty_score",
        "solver_steps",
        "branch_count",
        "dead_end_count",
        "forced_move_count",
        "elapsed_seconds",
        "checkpoint_count",
        "wall_count",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            writer.writerow({key: run.get(key) for key in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Zip puzzle generation over multiple seeds.")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium")
    parser.add_argument("--start-seed", type=int, required=True)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--seed-step", type=int, default=1)
    parser.add_argument("--format", choices=["human", "json"], default="human")
    parser.add_argument("--csv", type=Path, help="Optional CSV output path for per-run data.")
    args = parser.parse_args()

    if args.count <= 0:
        print("count must be greater than 0", file=sys.stderr)
        return 2
    if args.seed_step <= 0:
        print("seed-step must be greater than 0", file=sys.stderr)
        return 2

    summary = run_benchmark(
        difficulty=args.difficulty,
        start_seed=args.start_seed,
        count=args.count,
        seed_step=args.seed_step,
    )

    if args.csv:
        write_csv(args.csv, summary["runs"])

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print_human_summary(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())