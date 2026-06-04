# Simulation of a Mach–Zehnder Interferometer using Perceval

## Objective
This project aims to simulate a Mach–Zehnder interferometer using the Perceval framework in Python. 
The objective is to demonstrate fundamental quantum phenomena such as superposition and interference using a photonic quantum computing approach, in which information is carried by photons rather than traditional qubits.

## Background
Photonic quantum computing is an alternative model of quantum computation that relies on photons propagating through optical components. One of the most fundamental and illustrative setups in this domain is the Mach–Zehnder interferometer, which consists of two beam splitters and a phase shifter. 
This system provides a clear and intuitive way to observe how quantum interference arises from phase differences between paths.
Perceval is a software framework designed to simulate photonic quantum circuits. It allows users to construct optical systems programmatically and analyze their behavior without requiring physical experimental setups.

## Methodology

The project will begin by setting up the Perceval environment and reviewing the basic principles of photonic quantum systems. 
A Mach–Zehnder interferometer will then be constructed using two beam splitters and a tunable phase shifter.
A single-photon input state will be injected into the system. The simulation will track how the photon evolves through the interferometer, splitting into multiple paths and recombining at the second beam splitter. 
By varying the phase shift between the two paths, the resulting interference pattern will be
observed.
The simulation results will be collected as probability distributions over the possible output modes. 
These results will be visualized to clearly demonstrate how constructive and destructive interference affect the final measurement outcomes.

## Expected Outcomes

The expected outcome is a working simulation of a Mach–Zehnder interferometer that demonstrates quantum interference in a photonic system. The project will produce visualizations showing how output probabilities vary with phase shift. 

This will provide an intuitive understanding of how interference governs quantum behavior in optical circuits.

## Tools and Technologies
- Python
- Perceval framework
- NumPy and Matplotlib for computation and visualization

## Getting Started
```
uv venv
source .venv/bin/activate
uv pip install -e ".[qt]"
```
To run the Qt application:
```bash 
run_qt_app.sh
```
