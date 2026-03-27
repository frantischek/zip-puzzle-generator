# Zip Puzzle Generator

Python tool to generate uniquely solvable Zip-style puzzles.

## Features

- Difficulty levels: `easy`, `medium`, `hard`
- Deterministic generation via seed
- Unique-solution verification
- JSON output
- CLI mode and stdin JSON mode
- Candidate pool selection for improved puzzle quality
- Multiple wall-configuration retries per attempt
- Advanced solver metrics (branching, dead ends, forced moves, depth)
- Difficulty scoring (raw and normalized)
- Solver pruning for faster uniqueness checks

## Inspiration

The generated puzzles are inspired by the "Zip" puzzle format popularized by LinkedIn games.

This project is an independent implementation and is not affiliated with or endorsed by LinkedIn.

A German version of a similar puzzle can be played here:
https://www.spielekisterl.at/zip

This generator is designed for use in web or mobile puzzle games.

## Requirements

- Python 3.10+

## Usage

### CLI

```bash
python -m zip_generator.cli --difficulty medium --seed 1234
```

### JSON via stdin

```bash
echo '{"difficulty":"medium","seed":1234}' | python -m zip_generator.cli --stdin-json
```

### Compatibility wrapper

```bash
echo '{"difficulty":"medium","seed":1234}' | python zip_generator.py --stdin-json
```

## Benchmarking

You can benchmark puzzle generation across multiple seeds with:

```bash
python tools/benchmark_generator.py --difficulty medium --start-seed 1234 --count 20
```

Optional CSV output:

```bash
python tools/benchmark_generator.py --difficulty medium --start-seed 1234 --count 20 --csv medium_benchmark.csv
```

## Output

Successful runs return JSON like this:

```json
{
  "error": false,
  "grid_size": 7,
  "checkpoints": [...],
  "solution_path": [...],
  "checkpoint_count": 6,
  "walls": [...],
  "seed": 1235,
  "solver_steps": 1542,
  "branch_count": 120,
  "dead_end_count": 450,
  "forced_move_count": 300,
  "difficulty_score_raw": 123456,
  "difficulty_score": 123.5,
  "attempts": 1,
  "elapsed_seconds": 0.41,
  "collected_candidates": 3,
  "target_candidate_pool_size": 5,
  "scanned_attempts": 20
}
```

Failed runs return:

```json
{
  "error": true,
  "message": "Failed after ..."
}
```

## Development

Run tests:

```bash
pytest
```

## Notes

- Generation can take multiple attempts, especially on harder difficulties.
- The returned seed is the actual successful attempt seed.
- If a seed is provided, the first generation attempt uses exactly that seed.
- If generation fails, subsequent attempts increment the seed until a valid puzzle is found.
- The `attempts` field indicates how many seeds were tried.
- Multiple wall configurations may be tested per generation attempt to improve success rate.
- The generator may evaluate multiple candidate puzzles and select one based on difficulty scoring.
- Difficulty is estimated using solver-derived metrics such as branching and dead ends.
- `difficulty_score_raw` is used internally for ranking; `difficulty_score` is a normalized, human-readable value.
- Higher difficulties may require significantly more computation time.

## License

MIT
