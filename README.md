# Zip Puzzle Generator

Python tool to generate uniquely solvable Zip-style puzzles.

## Features

- Difficulty levels: `easy`, `medium`, `hard`
- Deterministic generation via seed
- Unique-solution verification
- JSON output
- CLI mode and stdin JSON mode

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

## Notes

- Generation can take multiple attempts, especially on harder difficulties.
- The returned seed is the actual successful attempt seed.
- If a seed is provided, the first generation attempt uses exactly that seed.
- If generation fails, subsequent attempts increment the seed until a valid puzzle is found.
- The `attempts` field indicates how many seeds were tried.

## License

MIT
