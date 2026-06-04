"""
Visualization utilities for Mach-Zehnder interferometer simulation results.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


def plot_interference_pattern(
    phase_values: np.ndarray,
    probabilities: np.ndarray,
    save_path: str = "interference_pattern.png",
) -> None:
    """
    Plot the interference pattern showing probability vs phase shift.

    This visualization demonstrates how constructive and destructive interference
    affect the output distribution as the phase shift is varied.

    Args:
        phase_values: Array of phase shift values (in radians)
        probabilities: Array of output probabilities corresponding to each phase
        save_path: Path to save the plot image
    """
    plt.figure(figsize=(10, 6))
    plt.plot(
        phase_values, probabilities, linewidth=2, label="Output Mode 0 Probability"
    )

    plt.xlabel("Phase Shift (radians)", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.title("Mach-Zehnder Interferometer: Quantum Interference Pattern", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.ylim([0, 1])
    plt.legend(fontsize=10)

    # Add shading to show constructive/destructive regions
    plt.axhline(
        y=1.0, color="g", linestyle="--", alpha=0.3, label="Constructive Interference"
    )
    plt.axhline(
        y=0.0, color="r", linestyle="--", alpha=0.3, label="Destructive Interference"
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Interference pattern saved to {save_path}")
    plt.close()


def plot_output_distribution(
    output_states: dict, save_path: str = "output_distribution.png"
) -> None:
    """
    Plot the output state distribution for a given phase shift.

    Args:
        output_states: Dictionary mapping output states to probabilities
        save_path: Path to save the plot image
    """
    states = [str(state) for state in output_states.keys()]
    probabilities = list(output_states.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(states, probabilities, color=["#1f77b4", "#ff7f0e"])

    plt.xlabel("Output State (n0, n1)", fontsize=12)
    plt.ylabel("Probability", fontsize=12)
    plt.title("Output State Distribution", fontsize=14)
    plt.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Output distribution saved to {save_path}")
    plt.close()


def plot_detailed_analysis(
    phase_values: np.ndarray,
    probabilities: np.ndarray,
    save_path: str = "detailed_analysis.png",
) -> None:
    """
    Create a detailed analysis plot with theoretical predictions.

    Args:
        phase_values: Array of phase shift values (in radians)
        probabilities: Array of output probabilities
        save_path: Path to save the plot image
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # Plot 1: Experimental results
    axes[0].plot(
        phase_values,
        probabilities,
        "o-",
        linewidth=2,
        markersize=6,
        label="Simulation Results",
    )
    axes[0].set_ylabel("Probability (Output Mode 0)", fontsize=11)
    axes[0].set_title("Mach-Zehnder Interferometer Simulation", fontsize=13)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim([0, 1])
    axes[0].legend(fontsize=10)

    # Plot 2: Theoretical interference pattern
    theoretical = 0.5 * (1 + np.cos(phase_values))
    axes[1].plot(
        phase_values,
        theoretical,
        "s-",
        color="green",
        linewidth=2,
        markersize=6,
        label="Theoretical (cos²)",
    )
    axes[1].set_xlabel("Phase Shift (radians)", fontsize=11)
    axes[1].set_ylabel("Probability (Output Mode 0)", fontsize=11)
    axes[1].set_title("Theoretical Interference Pattern", fontsize=13)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, 1])
    axes[1].legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Detailed analysis saved to {save_path}")
    plt.close()
