# Neural Terrain — Multi-Model AI Orchestration Project

## Project Overview

**Neural Terrain** is an interactive procedural terrain generator that runs entirely in the browser. It synthesizes multiple noise algorithms, erosion simulations, and biome classification to produce realistic, explorable landscapes — all rendered in real-time on an HTML5 canvas.

### Why This Project?

This project is chosen because it **genuinely benefits from multi-model collaboration** in ways a recruiter can see and understand:

1. **Algorithmically diverse** — Different noise functions (Perlin, Simplex, Worley, Diamond-Square, Value noise) are mathematically distinct. Each can be implemented independently, tested against known outputs, and swapped in/out. Different models may produce subtly different quality implementations.
2. **Layered complexity** — The pipeline has clear stages (noise generation → erosion simulation → biome classification → rendering) where each stage can be developed and tested in isolation before integration.
3. **Visually impressive** — The output is a beautiful, interactive terrain map that immediately communicates technical competence.
4. **Testable** — Every algorithm has mathematical properties that can be verified (value ranges, statistical distributions, continuity, gradient correctness), making quality assessment objective.
5. **Python + JS** — Core algorithms are implemented in Python (your primary focus) with comprehensive tests, then ported/adapted to JS for the browser demo.

### What Makes This "Beyond One Model"?

A single model could produce a basic Perlin noise demo. This project pushes further by:

- Combining 4-5 noise algorithms with proper octave layering and domain warping
- Adding hydraulic and thermal erosion (computationally complex, easy to get subtly wrong)
- Including biome classification with temperature/moisture gradients
- Building a polished interactive UI with real-time parameter controls
- Maintaining a full Python test suite that validates mathematical correctness

The orchestration challenge — getting models to produce compatible, high-quality code that integrates cleanly — is itself the skill being demonstrated.

---

## Architecture

```
neural-terrain/
├── README.md                    # Project overview & AI orchestration story
├── ORCHESTRATION_LOG.md         # Detailed log of which model did what
├── index.html                   # Main demo page (single-file, GitHub Pages)
│
├── python/                      # Python reference implementations + tests
│   ├── terrain/
│   │   ├── __init__.py
│   │   ├── noise.py             # All noise algorithm implementations
│   │   ├── erosion.py           # Hydraulic & thermal erosion
│   │   ├── biome.py             # Biome classification
│   │   └── pipeline.py          # Full terrain generation pipeline
│   ├── tests/
│   │   ├── test_noise.py        # Noise algorithm correctness tests
│   │   ├── test_erosion.py      # Erosion simulation tests
│   │   ├── test_biome.py        # Biome classification tests
│   │   └── test_integration.py  # Full pipeline tests
│   └── requirements.txt         # numpy (only hard dependency)
│
└── js/                          # JS implementations (embedded in index.html for GH Pages)
    └── (code lives inside index.html <script> tags)
```

### The Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────┐
│ Noise Layer │ →  │   Erosion    │ →  │    Biome      │ →  │  Render  │
│ Generation  │    │  Simulation  │    │Classification │    │  Canvas  │
└─────────────┘    └──────────────┘    └───────────────┘    └──────────┘
  Perlin             Hydraulic           Temperature           2D/3D
  Simplex            Thermal             Moisture              Color map
  Worley                                 Altitude              Contours
  Diamond-Square                         Biome lookup          Controls
  Value noise
```

---

## Model Roles & Assignment Strategy

### Claude Opus 4.6 (Orchestrator)

- **Role**: Architecture, integration, final review, the interactive frontend, orchestration documentation
- **Responsible for**: `index.html`, `pipeline.py`, `test_integration.py`, `ORCHESTRATION_LOG.md`, all final integration

### Other Models — Foundational Stage Candidates

Each model gets the **same foundational task** to enable fair comparison:

| Model | CLI/Interface | Best suited for |
|-------|--------------|-----------------|
| Gemini 3.0 Pro | Gemini CLI | Noise algorithms (strong math reasoning) |
| gpt-5.3-codex | OpenAI Codex CLI | Erosion simulation (strong code generation) |
| Grok 4.1 | Web | Biome classification (good at structured logic) |
| GLM-5 | Web | Alternative noise implementations |
| Big Pickle | OpenCode CLI | Erosion or noise (evaluate first) |
| Kimi K2.5 Free | OpenCode CLI | Biome or noise (evaluate first) |

**Important**: These assignments are tentative. The foundational assessment (Phase 1) will determine which models actually produce useful code. It is better to use 2-3 models well than 6 models poorly.

---

## Phase 1: Foundational Assessment

### Goal

Give each candidate model the **same structured prompt** for implementing Perlin noise in Python. This serves as a calibration task — it's well-defined, mathematically verifiable, and reveals each model's code quality, correctness, and style.

### Assessment Criteria (the "gate")

Each implementation is tested against the provided test suite. The threshold for advancing to Phase 2:

| Criterion | Threshold | Weight |
|-----------|-----------|--------|
| Unit tests passing | ≥ 85% | 40% |
| Value range correctness (output in [-1, 1]) | Must pass | Required |
| Gradient continuity (no discontinuities) | Must pass | Required |
| Code quality (readable, typed, documented) | Subjective 1-5 | 20% |
| Performance (512×512 grid < 5s on reasonable HW) | Should pass | 10% |
| **Overall score** | **≥ 70/100** | |

### How to Run Assessment

```bash
cd neural-terrain/python
pip install numpy pytest
pytest tests/test_noise.py -v --tb=short 2>&1 | tee results.txt
```

Count passed/failed, note any errors, and calculate the score using the rubric in `EVALUATION_TEMPLATE.md`.

### Iteration Protocol

Before sending results to Claude for review:

1. **First attempt**: Give the model the prompt, collect output
2. **Run tests**: If < 85% pass rate, give the model the test failures
3. **Second attempt**: Let the model fix issues (provide test output)
4. **Run tests again**: If still < 85%, give one more chance with specific failing test names
5. **Third attempt** (final): Run tests. Record final score regardless.

This gives each model up to 3 iterations. Record all attempts in the evaluation template.

---

## Phase 1 Prompt (Give This to Each Model)

### The Prompt

Copy everything between the `---START PROMPT---` and `---END PROMPT---` markers below:

---START PROMPT---

# Task: Implement 2D Perlin Noise in Python

Implement a complete, production-quality 2D Perlin noise generator in Python.

## Requirements

1. Create a file `noise.py` containing a class `PerlinNoise` with the following interface:

```python
class PerlinNoise:
    """2D Perlin noise generator."""
    
    def __init__(self, seed: int = 0):
        """Initialize with a seed for reproducibility."""
        ...
    
    def noise(self, x: float, y: float) -> float:
        """
        Generate Perlin noise value at (x, y).
        Returns a float in the range [-1, 1].
        """
        ...
    
    def octave_noise(self, x: float, y: float, octaves: int = 6, 
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """
        Generate fractal Brownian motion (fBm) using multiple octaves.
        Returns a float approximately in [-1, 1] (may slightly exceed due to octave stacking).
        """
        ...
    
    def generate_grid(self, width: int, height: int, scale: float = 50.0,
                      octaves: int = 6, persistence: float = 0.5,
                      lacunarity: float = 2.0) -> list[list[float]]:
        """
        Generate a 2D grid of noise values.
        Returns a width×height nested list of floats, normalized to [0, 1].
        """
        ...
```

2. Implementation requirements:
   - Use Ken Perlin's improved noise algorithm (2002) with the standard permutation table
   - Use a proper fade function: f(t) = 6t⁵ - 15t⁴ + 10t³
   - Use gradient vectors derived from the permutation table hash
   - The seed should shuffle the permutation table deterministically
   - Pure Python with only `numpy` allowed as an optional dependency for grid generation
   - Include type hints on all methods
   - Include docstrings on all public methods

3. Mathematical properties that MUST hold:
   - `noise(x, y)` returns values in [-1, 1]
   - Same seed + same coordinates = same output (deterministic)
   - Different seeds produce different outputs
   - The noise is continuous (small changes in input → small changes in output)
   - Integer coordinates produce 0 (this is a property of Perlin noise)
   - `generate_grid` output is normalized to [0, 1]

4. Code quality expectations:
   - Clean, readable code with meaningful variable names
   - No magic numbers without explanation
   - Efficient (avoid unnecessary allocations in hot loops)
   - The file should be self-contained (runnable as `python noise.py` for a quick demo)

5. If run as main, the script should print a small 10×10 grid of noise values to demonstrate it works.

## Do NOT:
- Use any external noise libraries (like `noise`, `opensimplex`, etc.)
- Use randomness that isn't seeded
- Return values outside the specified ranges

---END PROMPT---

---

## Phase 1 Test Suite

Save this as `tests/test_noise.py` before running assessments.

(See the standalone `test_noise.py` file — provided separately.)

---

## Evaluation Template

After running each model's code through the test suite, fill in the standalone `EVALUATION_TEMPLATE.md` (provided separately).

---

## Phase 2: Specialized Tasks (After Assessment)

Once we know which models produce quality code, we assign specialized tasks:

### Task A: Simplex Noise (assign to best-performing model)
Similar to Perlin but uses a simplex grid. Less directional artifacts, slightly more complex math.

### Task B: Hydraulic Erosion Simulation
Simulate water flow over terrain: rain → water accumulation → sediment transport → deposition. This is the hardest computational task and should go to the model that produced the cleanest, most correct Perlin implementation.

### Task C: Thermal Erosion
Simpler than hydraulic: material above a talus angle collapses downhill. Good for a secondary model.

### Task D: Biome Classification
Given altitude, temperature, and moisture maps, classify each cell into a biome (ocean, beach, grassland, forest, desert, tundra, mountain, snow). This is more of a structured logic task.

### Task E: Worley/Voronoi Noise
Distance-based noise useful for cave systems, cell patterns. Mathematically different from Perlin/Simplex.

Each task will have its own test suite (I'll provide those when we reach Phase 2).

---

## Phase 3: Integration & Frontend (Claude Opus)

I will handle:
- Integrating all passing implementations into a unified Python pipeline
- Porting the algorithms to JavaScript for the browser demo
- Building the interactive `index.html` with canvas rendering and parameter controls
- Writing the `ORCHESTRATION_LOG.md` that tells the story of the collaboration
- Final quality pass on all code

---

## Timeline & Workflow

```
Week 1: Phase 1 — Foundational Assessment
  ├── Give each model the Perlin noise prompt
  ├── Run tests, iterate up to 3× per model
  ├── Score using evaluation template
  └── Report results to Claude → decide Phase 2 assignments

Week 2: Phase 2 — Specialized Tasks  
  ├── Distribute specialized prompts to advancing models
  ├── Run task-specific test suites
  ├── Iterate and evaluate
  └── Send passing code to Claude for integration

Week 3: Phase 3 — Integration & Polish
  ├── Claude integrates Python pipeline
  ├── Claude builds interactive frontend
  ├── Final testing and polish
  └── Deploy to GitHub Pages
```

---

## Getting Started — Step by Step

### Step 1: Set Up the Project Locally

```bash
mkdir -p neural-terrain/python/terrain
mkdir -p neural-terrain/python/tests
cd neural-terrain/python
```

Create `terrain/__init__.py` (empty file) and save the test file above as `tests/test_noise.py`.

### Step 2: Run the Assessment for Each Model

For each model (start with 2-3, not all 6):

1. Open the model's interface (CLI or web)
2. Paste the prompt from the "Phase 1 Prompt" section above
3. Save the output as `terrain/noise.py`
4. Run: `pytest tests/test_noise.py -v --tb=short`
5. If < 85% pass: give the model the failing test output and ask it to fix
6. Repeat up to 3 attempts total
7. Fill in the Evaluation Template

### Step 3: Report Back to Claude

Share:
- The filled evaluation templates for each model
- The final `noise.py` from the best-performing model(s)
- Any observations about the models' strengths/weaknesses

I'll then design Phase 2 prompts tailored to each model's demonstrated strengths.

---

## Recommended Model Priority

Start with these 3 (most likely to produce strong results based on known capabilities):

1. **Gemini 3.0 Pro** (Gemini CLI) — Strong mathematical reasoning
2. **gpt-5.3-codex** (OpenAI Codex CLI) — Strong code generation
3. **Grok 4.1** (Web) — Good general capability

If these three cover the pipeline well, the remaining models may not be needed. If any underperform, try:

4. **Big Pickle** (OpenCode CLI)
5. **Kimi K2.5 Free** (OpenCode CLI)
6. **GLM-5** (Web) — Test last, as it may have less consistent English code output

---

## Notes for Recruiters

The `ORCHESTRATION_LOG.md` in the final project will document:
- Which model contributed which algorithm
- How quality was evaluated (test suites, scoring rubrics)
- Integration challenges and how they were resolved  
- What the orchestrator (Claude Opus 4.6) contributed vs. delegated
- Why certain models were chosen for certain tasks

This transparency is the point — it demonstrates that AI-assisted development is a skill involving judgment, evaluation, and synthesis, not just prompt-and-paste.
