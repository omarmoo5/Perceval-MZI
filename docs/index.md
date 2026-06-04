# Quantum Mach-Zehnder Interferometer — Interactive Simulator

An interactive PyQt5 desktop application for exploring quantum interference in a photonic Mach-Zehnder interferometer, built with the Perceval quantum computing framework.

- [Full Blog Post: Building an Interactive MZI Simulator]({{ site.baseurl }}{% post_url 2026-06-04-mach-zehnder-interferometer-interactive-simulator %})
- [GitHub Repository](https://github.com/omarmoo5/Perceval-MZI)
---

## Quick Overview

<div style="text-align: center;">
    <img src="{{ '/assets/images/ui_overview.png' | relative_url }}" alt="Application UI Overview" width="700"/>
    <p><em>Main application window showing controls, schematic, and interference plots.</em></p>
</div>

This project simulates a single-photon Mach-Zehnder interferometer with:

- Real-time phase control via a snap-enabled slider (snaps to 0°, 90°, 180°, 270°, 360°)
- Live interference pattern plots (theory vs simulation)
- Full phase sweep (30 points, 0°–360°)
- Output distribution bar chart
- Circuit schematic visualization

---

## Features

| Feature | Description |
|---------|-------------|
| **Phase Control** | Slider from 0° to 360° with 5° step, 90° snap points |
| **Live Plots** | Two stacked interference subplots (Mode 0 & Mode 1) |
| **Phase Sweep** | 30-point sweep comparing theory to simulated data |
| **Distribution** | Bar chart showing output state probabilities |
| **Schematic** | Visual block diagram of the interferometer circuit |
| **History** | Track previous simulation runs with toggle |
| **Caching** | Automatic caching of repeated simulations for speed |

---

## Getting Started

```bash
git clone https://github.com/omarmoo5/Perceval-MZI.git
cd Perceval-MZI
uv venv
source .venv/bin/activate
uv pip install -e ".[qt]"
bash run_qt_app.sh
```

---

*Built with [Perceval](https://perceval.quandela.net/), [PyQt5](https://www.riverbankcomputing.com/software/pyqt/), [NumPy](https://numpy.org/), and [Matplotlib](https://matplotlib.org/).*
