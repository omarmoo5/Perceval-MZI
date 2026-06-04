"""
Mach-Zehnder interferometer simulation using Perceval framework.

This module implements a photonic quantum circuit consisting of:
- Two beam splitters (50-50 splitting)
- One phase shifter in one arm
- Single-photon input state
"""

import numpy as np
from perceval import Circuit, Processor, BasicState
from perceval.components import BS, PS
from perceval.algorithm import Sampler
from typing import Tuple, Dict


class MachZehnderInterferometer:
    """A photonic Mach-Zehnder interferometer circuit simulator."""

    def __init__(self):
        """Initialize the Mach-Zehnder interferometer circuit."""
        self.circuit = self._build_circuit()

    def _build_circuit(self, phase: float = 0) -> Circuit:
        # In Perceval, BS(theta=π/2) gives 50:50 splitting.
        bs1 = Circuit(2)
        bs1.add(0, BS(theta=np.pi / 2))

        ps = Circuit(2)
        ps.add(1, PS(phi=phase))

        bs2 = Circuit(2)
        bs2.add(0, BS(theta=np.pi / 2))

        # Sequential layers are composed with the // operator.
        return bs1 // ps // bs2

    def set_phase(self, phase: float) -> None:
        """Set the phase shift in the interferometer."""
        self.circuit = self._build_circuit(phase)

    def run_simulation(self, num_samples: int = 10000) -> Dict[Tuple[int, int], float]:
        processor = Processor("SLAP", self.circuit)
        processor.with_input(BasicState([1, 0])) # Single photon in mode 0, vacuum in mode 1
        
        sampler = Sampler(processor)
        sampler_results = sampler.sample_count(num_samples)
        results = sampler_results["results"]

        # Convert to probability dictionary
        probabilities = {}
        for state, count in results.items():
            # Parse state string to tuple format
            state_str = str(state).replace("|", "").replace(">", "")
            state_tuple = tuple(map(int, state_str.split(",")))
            probabilities[state_tuple] = count / num_samples

        return probabilities

    def sweep_phase(
        self, phase_range: np.ndarray, num_samples: int = 5000
    ) -> Tuple[np.ndarray, np.ndarray]:
        output_probs = []

        for phase in phase_range:
            self.set_phase(phase)
            results = self.run_simulation(num_samples)

            # Calculate probability of photon being in output mode 0
            # States are represented as (n0, n1) tuples
            prob_mode_0 = sum(p for state, p in results.items() if state[0] == 1)
            output_probs.append(prob_mode_0)

        return phase_range, np.array(output_probs)
