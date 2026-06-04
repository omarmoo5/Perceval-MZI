#!/usr/bin/env python3
"""
Main execution script for Mach-Zehnder interferometer simulation.

This script:
1. Initializes the interferometer
2. Runs simulations across a range of phase shifts
3. Generates visualizations of the results
4. Demonstrates quantum interference effects
"""

import numpy as np

from quantum_sim import (
    MachZehnderInterferometer,
    plot_interference_pattern,
    plot_output_distribution,
    plot_detailed_analysis,
)


def main():
    """Run the Mach-Zehnder interferometer simulation."""

    print("=" * 70)
    print("Mach-Zehnder Interferometer Simulation")
    print("=" * 70)

    # Step 1: Initialize the interferometer
    print("\n[1/4] Initializing Mach-Zehnder interferometer...")
    mzi = MachZehnderInterferometer()
    print("✓ Interferometer initialized successfully")

    # Step 2: Run simulation for a single phase shift (demonstration)
    print("\n[2/4] Running single-phase simulation (phase = π/2)...")
    mzi.set_phase(np.pi / 2)
    single_phase_results = mzi.run_simulation(num_samples=10000)
    print("Output distribution for phase = π/2:")
    for state, prob in sorted(single_phase_results.items()):
        print(f"  State {state}: {prob:.4f}")

    # Save single phase distribution plot
    plot_output_distribution(single_phase_results, "output_distribution.png")

    # Step 3: Sweep through phase range and collect data
    print("\n[3/4] Sweeping phase from 0 to 2π...")
    phase_range = np.linspace(0, 2 * np.pi, 50)
    phase_values, output_probs = mzi.sweep_phase(phase_range, num_samples=5000)
    print(f"✓ Completed {len(phase_values)} phase measurements")

    # Step 4: Generate visualizations
    print("\n[4/4] Generating visualizations...")
    plot_interference_pattern(phase_values, output_probs, "interference_pattern.png")
    plot_detailed_analysis(phase_values, output_probs, "detailed_analysis.png")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY OF RESULTS")
    print("=" * 70)
    print("Phase range tested: 0 to 2π radians")
    print(f"Number of phase points: {len(phase_values)}")
    print(f"Maximum output probability: {output_probs.max():.4f}")
    print(f"Minimum output probability: {output_probs.min():.4f}")
    print(f"Mean probability: {output_probs.mean():.4f}")

    # Calculate visibility (contrast) of interference pattern
    visibility = (output_probs.max() - output_probs.min()) / (
        output_probs.max() + output_probs.min()
    )
    print(f"Interference visibility: {visibility:.4f}")

    print("\n Simulation completed successfully!")

if __name__ == "__main__":
    main()
