---
layout: post
title: "Building an Interactive Mach-Zehnder Interferometer Simulator"
date: 2026-06-04
categories: quantum physics simulation
tags: [quantum, perceval, pyqt5, interferometer, simulation]
---

## Introduction

The Mach-Zehnder interferometer (MZI) is one of the most fundamental and elegant experiments in quantum optics. It demonstrates wave-particle duality, quantum interference, and the counterintuitive nature of measurement — all in a simple tabletop setup.

I built an interactive PyQt5 desktop application that simulates a single-photon MZI in real time, combining the Perceval quantum computing framework with a responsive matplotlib-based GUI. This post walks through the physics, the implementation, and the design decisions along the way.

<div style="text-align: center;">
    <img src="{{ '/assets/images/ui_overview.png' | relative_url }}" alt="Application UI Overview" width="750"/>
    <p><em>The main application window: controls panel (left), interference plots (right).</em></p>
</div>

---

## Physics Background

### The Mach-Zehnder Interferometer

A Mach-Zehnder interferometer consists of:

1. **Two 50:50 beam splitters (BS)** — each splits an incoming photon into a superposition of two paths
2. **A phase shifter** — introduces a relative phase shift between the two arms
3. **Two detectors** — placed at the two output ports

<div style="text-align: center;">
    <img src="{{ '/assets/images/schematic.png' | relative_url }}" alt="Interferometer Schematic" width="500"/>
    <p><em>Schematic of the Mach-Zehnder interferometer.</em></p>
</div>

The process:

1. A single photon enters the first beam splitter, entering a superposition of the two paths
2. One path accumulates a phase shift φ (controlled by the user)
3. The second beam splitter recombines the two paths
4. Interference determines which detector clicks

### The Mathematics

The output state after both beam splitters and the phase shifter is:

```
|ψ_out⟩ = cos(φ/2) |1,0⟩ + sin(φ/2) |0,1⟩
```

The probabilities of detecting the photon at each output are:

```
P(Mode 0) = cos²(φ/2) = (1 + cos φ) / 2
P(Mode 1) = sin²(φ/2) = (1 - cos φ) / 2
```

When φ = 0, the photon always exits through Mode 1 (constructive interference). When φ = π, it always exits through Mode 0 (destructive interference). At φ = π/2, the output is 50:50.

---

## Related Work

Several educational quantum simulators exist:

- **Quirk** (Strilanc) — browser-based quantum circuit simulator with drag-and-drop gates
- **IBM Quantum Composer** — visual quantum circuit builder with real hardware access
- **Quantum Circuit Simulator** (QCS) — various web-based educational tools

What sets this project apart is the **real-time interactive control** with a physical slider metaphor, combined with **live plot updates** showing theory vs simulation side by side, making the connection between the abstract phase parameter and the measured interference pattern immediately visible.

---

## Implementation

### Technology Stack

| Component | Technology |
|-----------|-----------|
| GUI Framework | PyQt5 |
| Quantum Simulation | Perceval (SLOS backend) |
| Plotting | Matplotlib |
| Numerical | NumPy |

### Why Perceval?

I chose Perceval because it's built specifically for simulating light-based (photonic) quantum circuits. It provides high-level abstractions for beam splitters, phase shifters, and other optical components, making it straightforward to model the MZI. 

Perceval has different "backends" — I used the **SLOS** backend (Strong Linear Optical Simulation) because it's optimized for light-based circuits, allowing for fast simulations that can update in real time as the user adjusts the phase slider.

The official docs explain all the available backends here: [Perceval Backends Reference](https://perceval.quandela.net/docs/v1.2/reference/backends/slos.html)

### Architecture

The application is split into two main modules:

**`quantum_sim/interferometer.py`** — The simulation backend, wrapping Perceval's `Circuit`, `Processor`, and `Sampler` to build and simulate the MZI:

```python
# Build the MZI circuit
bs1 = Circuit(2)
bs1.add(0, BS(theta=np.pi / 2))

ps = Circuit(2)
ps.add(1, PS(phi=phase))

bs2 = Circuit(2)
bs2.add(0, BS(theta=np.pi / 2))

circuit = bs1 // ps // bs2
```

**`qt_app.py`** — The PyQt5 frontend with the slider, plots, schematic, and sweep functionality.

### Key Features

#### Dual-Mode Interference Plots

Two stacked subplots show Mode 0 and Mode 1 probabilities simultaneously:
- **Green/orange dashed lines**: Theoretical predictions
- **Blue/orange dots**: Full-phase sweep data (30 points)
- **Red diamond/purple square**: Current simulation result
- **Vertical red line**: Instant phase indicator

<div style="text-align: center;">
    <img src="{{ '/assets/images/interference_pattern.png' | relative_url }}" alt="Interference Pattern" width="700"/>
    <p><em>Interference pattern for Mode 0 (top) and Mode 1 (bottom) with theory curves and simulation data.</em></p>
</div>

#### Full Phase Sweep

The sweep button runs the simulation at 30 evenly-spaced phase points from 0° to 360°, plotting all results on the interference subplots for comparison with theory.

#### Output Distribution

A bar chart in the left panel shows the current probability distribution over the two output states, with numerical values displayed above each bar.

---

## Thought Process & Design Decisions

### Why PyQt5?

I chose PyQt5 over web-based alternatives (Dash, Streamlit) for two reasons: real-time responsiveness with the slider, and native desktop integration without browser overhead. PyQt5 + matplotlib gives a snappy, native-feeling experience.

### The BS(theta) Bug

The trickiest bug was a mismatch between theory and simulation at φ = 0° and φ = 360°. Instead of the expected deterministic output (all photons in one mode), the simulation showed 50:50.

The root cause was twofold:

1. **Wrong BS angle**: Perceval's `BS(theta)` uses `cos²(θ/2)` for transmissivity, so `θ = π/4` gives ≈85:15 splitting, not 50:50. The correct parameter is `θ = π/2`.

2. **Circuit layering**: `circuit.add(0, BS())` followed by another `circuit.add(0, BS())` doesn't create sequential layers — it overwrites the previous component. Sequential composition requires the `//` operator:

```python
circuit = bs1 // ps // bs2
```

Fixing these two issues made the simulation perfectly match theory:

<div style="text-align: center;">
    <img src="{{ '/assets/images/phase_sweep.png' | relative_url }}" alt="Phase Sweep" width="700"/>
    <p><em>Phase sweep showing theory vs simulation agreement after the fix.</em></p>
</div>

### Snap vs Free Movement

I wanted the slider to have guided snap points for the key angles (multiples of 90°) while still allowing free exploration. The compromise: free movement during drag, snap on release within a ±10° threshold. Visual blue dots indicate the snap positions, and tick marks align with them.

### Layout Evolution

The layout went through several iterations:
1. Initially all plots in a single grid
2. Split distribution bar chart into a separate smaller canvas
3. Split the single interference plot into two stacked subplots (Mode 0 top, Mode 1 bottom)
4. Moved the schematic to the left panel for a cleaner right-hand plotting area

Each change was driven by the goal of making the data as readable as possible at a glance.

---

## Gallery

<!-- Placeholder — add your screenshots to assets/images/ -->

| Screenshot | Description |
|------------|-------------|
| `ui_overview.png` | Full application window showing all components |
| `interference_pattern.png` | Close-up of the interference subplots |
| `phase_sweep.png` | Sweep results comparing theory to simulation |
| `schematic.png` | The interferometer circuit diagram |

---

## Try It Yourself

```bash
git clone https://github.com/omarmoo5/Perceval-MZI.git
cd Perceval-MZI
uv venv
source .venv/bin/activate
uv pip install -e ".[qt]"
bash run_qt_app.sh
```

Requires Python 3.9+, PyQt5, Perceval, NumPy, and Matplotlib.

---

## References

1. Perceval Documentation — [https://perceval.quandela.net/](https://perceval.quandela.net/)
2. Mach, L. (1892). "Ueber einen Interferenzrefraktor". *Zeitschrift für Instrumentenkunde*.
3. Zehnder, L. (1891). "Ein neuer Interferenzrefraktor". *Zeitschrift für Instrumentenkunde*.
4. Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
