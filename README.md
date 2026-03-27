# Zip Puzzle Generator

Python tool to generate uniquely solvable Zip-style puzzles.

## What changed in this refactor

The original single-file script was split into modules:

- `zip_generator/config.py` — difficulty presets
- `zip_generator/pathing.py` — Hamiltonian path generation, path transforms, checkpoint placement
- `zip_generator/validation.py` — connectivity checks
- `zip_generator/solver.py` — unique-solution solver
- `zip_generator/generator.py` — wall generation and orchestration
- `zip_generator/cli.py` — command-line entry point

This makes the project easier to test, extend, and publish on GitHub.

## Features

- Difficulty levels: `easy`, `medium`, `hard`
- Deterministic generation via seed
- Unique-solution verification
- JSON output
- CLI mode and stdin JSON mode

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
  "attempts": 1,
  "elapsed_seconds": 0.41
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

## Suggested GitHub files

This starter repo includes:

- `README.md`
- `LICENSE`
- `.gitignore`
- `tests/`
- GitHub Actions workflow for tests

That is enough for a first public repo without looking half-finished.

## Notes

- Generation can take multiple attempts, especially on harder difficulties.
- The returned seed is the actual successful attempt seed.
- The logic is preserved from the uploaded single-file script. This is a structural refactor, not a new algorithm.

## License

MIT
