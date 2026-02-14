# Neural Terrain

**Interactive procedural terrain generator built through multi-model AI orchestration.**

Four AI models each contributed independently-tested code. Claude Opus 4.6 designed the architecture, wrote test suites, evaluated outputs, and integrated everything into a working pipeline.

[**→ Live Demo**](https://markusisaksson1982.github.io/neural-terrain/) · [Orchestration Log](ORCHESTRATION_LOG.md)

---

## What This Demonstrates

This project is a portfolio piece showcasing **AI orchestration as a meta-skill**:

- **Architecture**: Designing a system that can be built by multiple AI contributors
- **Evaluation**: 114 tests across 4 components with objective pass/fail criteria
- **Integration**: Making independently-developed code work together
- **Judgment**: Choosing which models to use, which tasks to assign, and when to stop

## Model Contributions

| Model | Component | Test Results |
|-------|-----------|-------------|
| Gemini 3.0 Pro | Perlin noise, Simplex noise | 25/25, 27/27 |
| gpt-5.3-codex | Hydraulic erosion simulation | 22/22 |
| Grok 4.1 | Biome classification system | 42/42 |
| Claude Opus 4.6 | Architecture, tests, integration, frontend | — |

## Interactive Demo

Open `index.html` in a browser. Controls:

- **Noise type**: Perlin, Simplex, or blended
- **Terrain shape**: Scale, octaves, persistence, lacunarity
- **Erosion**: Iteration count and strength (simulates water carving valleys)
- **Biome**: Sea level, temperature, moisture
- **Display mode**: Biome colors, elevation, moisture, temperature, erosion diff

Hover over the canvas to see per-pixel biome/elevation/moisture/temperature values.

## Python Pipeline

```bash
cd python/terrain
python pipeline.py --seed 42 --size 256 --noise simplex --erosion 3000 --output terrain.ppm
```

Run all tests:
```bash
cd python
pytest tests/ -v --tb=short
```

## Project Structure

```
neural-terrain/
├── index.html                    # Interactive browser demo (GitHub Pages)
├── ORCHESTRATION_LOG.md          # Full documentation of the multi-model process
├── README.md                     # This file
└── python/
    ├── terrain/
    │   ├── noise.py              # Perlin noise      (Gemini 3.0 Pro)
    │   ├── simplex.py            # Simplex noise      (Gemini 3.0 Pro)
    │   ├── erosion.py            # Hydraulic erosion   (gpt-5.3-codex)
    │   ├── biome.py              # Biome classifier    (Grok 4.1)
    │   └── pipeline.py           # Unified pipeline    (Claude Opus 4.6)
    └── tests/
        ├── test_noise.py         # 25 tests
        ├── test_simplex.py       # 27 tests
        ├── test_erosion.py       # 22 tests
        └── test_biome.py         # 42 tests
```

## Process

The full process is documented in [ORCHESTRATION_LOG.md](ORCHESTRATION_LOG.md). Summary:

1. **Phase 1** — All candidate models implemented Perlin noise against the same 25-test suite. Three models advanced.
2. **Phase 2** — Each model received a specialized task matching its demonstrated strengths.
3. **Phase 3** — Claude integrated all components, ported to JavaScript, and built the browser demo.

## License

MIT
