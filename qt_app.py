#!/usr/bin/env python3
"""
Mach-Zehnder Interferometer - Interactive PyQt5 Application

A desktop application with real-time interactive sliders and live plot updates
for exploring quantum interference in a photonic Mach-Zehnder interferometer.

Features:
  - Real-time phase control
  - Caching for faster repeated simulations
  - Interactive cursor (crosshair) on plots
  - History tracking with show/hide option
  - Theoretical (dotted) vs simulation (points) visualization
"""

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox, QPushButton, QStatusBar, QGroupBox,
    QCheckBox, QStyleOptionSlider, QStyle
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

from quantum_sim import MachZehnderInterferometer


class SnapSlider(QSlider):
    """QSlider with colored dot markers at snap positions below the groove."""

    def __init__(self, orientation, snap_points=None, parent=None):
        super().__init__(orientation, parent)
        self.snap_points = snap_points or [0, 90, 180, 270, 360]

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.snap_points:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )
        if groove.isNull() or groove.width() < 2:
            painter.end()
            return
        mn, mx = self.minimum(), self.maximum()
        painter.setBrush(QColor("#0078D7"))
        painter.setPen(Qt.NoPen)
        for snap in self.snap_points:
            px = QStyle.sliderPositionFromValue(mn, mx, snap, groove.width())
            x = groove.x() + px
            y = groove.bottom() + 8
            painter.drawEllipse(int(x) - 3, int(y) - 3, 6, 6)
        painter.end()


class MZIInterferometer(QMainWindow):
    """PyQt5 Application for Mach-Zehnder Interferometer"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mach-Zehnder Interferometer - Interactive Simulator")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize simulator
        self.mzi = MachZehnderInterferometer()
        self.current_phase = np.pi
        self.current_samples = 5000

        # Caching: Store simulation results to avoid redundant calculations
        self.simulation_cache = {}  # {(phase, samples): results}
        self.history = []  # List of (phase, prob_mode_0, samples) tuples
        self.sweep_phases = None
        self.sweep_probs = None

        # Debounce timer for slider
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.update_plots)

        # Create UI
        self.init_ui()

        # Set initial plot
        self.update_plots()

    def init_ui(self):
        """Initialize the user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Left column: Controls + Schematic + Distribution plot
        left_column = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.create_control_panel())
        left_layout.addWidget(self.create_schematic_panel())
        left_layout.addWidget(self.create_distribution_panel())
        left_column.setLayout(left_layout)
        main_layout.addWidget(left_column, 0)

        # Right panel: Interference pattern plot
        right_panel = self.create_plot_panel()
        main_layout.addWidget(right_panel, 1)

        main_widget.setLayout(main_layout)

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_control_panel(self):
        """Create the control panel with sliders"""
        group = QGroupBox("Controls")
        layout = QVBoxLayout()

        # Title
        title = QLabel("Phase Control")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(20)

        # Phase slider
        layout.addWidget(QLabel("Phase Shift (0° to 360°):"))
        self.phase_slider = SnapSlider(Qt.Horizontal)
        self.phase_slider.setMinimum(0)
        self.phase_slider.setMaximum(360)
        self.phase_slider.setValue(180)
        self.phase_slider.setTickPosition(QSlider.TicksBelow)
        self.phase_slider.setTickInterval(90)
        self.phase_slider.setSingleStep(5)
        self.phase_slider.sliderMoved.connect(self.on_phase_changed)
        self.phase_slider.valueChanged.connect(self.on_phase_changed)
        self.phase_slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.phase_slider)

        # Phase value display
        self.phase_label = QLabel(f"Phase: 180° ({np.pi:.4f} rad)")
        phase_font = QFont()
        phase_font.setPointSize(11)
        phase_font.setBold(True)
        self.phase_label.setFont(phase_font)
        layout.addWidget(self.phase_label)

        layout.addSpacing(30)

        # Samples control
        layout.addWidget(QLabel("Number of Samples:"))
        self.samples_spinbox = QSpinBox()
        self.samples_spinbox.setMinimum(1000)
        self.samples_spinbox.setMaximum(5000)
        self.samples_spinbox.setValue(1000)
        self.samples_spinbox.setSingleStep(500)
        self.samples_spinbox.valueChanged.connect(self.on_samples_changed)
        layout.addWidget(self.samples_spinbox)

        layout.addSpacing(30)

        # Info box
        info_title = QLabel("Quantum Interference")
        info_font = QFont()
        info_font.setPointSize(11)
        info_font.setBold(True)
        info_title.setFont(info_font)
        layout.addWidget(info_title)

        self.info_label = QLabel(
            "Phase: 0.0000 rad\n"
            "Mode 0: 0.0000\n"
            "Mode 1: 0.0000\n"
            "Theory: 0.0000"
        )
        info_font = QFont("Courier")
        info_font.setPointSize(10)
        self.info_label.setFont(info_font)
        layout.addWidget(self.info_label)

        layout.addSpacing(20)

        # History checkbox
        self.history_checkbox = QCheckBox("Show History (Previous Runs)")
        self.history_checkbox.setChecked(True)
        self.history_checkbox.stateChanged.connect(self.on_history_toggled)
        history_font = QFont()
        history_font.setPointSize(10)
        self.history_checkbox.setFont(history_font)
        layout.addWidget(self.history_checkbox)

        layout.addSpacing(10)

        # Cache info
        self.cache_label = QLabel("Cache: 0 entries")
        cache_font = QFont()
        cache_font.setPointSize(9)
        cache_font.setItalic(True)
        self.cache_label.setFont(cache_font)
        layout.addWidget(self.cache_label)

        # Sweep button
        self.sweep_button = QPushButton("Full Phase Sweep (0°–360°)")
        self.sweep_button.setMinimumHeight(36)
        sweep_btn_font = QFont()
        sweep_btn_font.setPointSize(10)
        sweep_btn_font.setBold(True)
        self.sweep_button.setFont(sweep_btn_font)
        self.sweep_button.clicked.connect(self.on_sweep)
        layout.addWidget(self.sweep_button)

        layout.addSpacing(20)

        # Help text
        help_label = QLabel(
            "Drag the slider to control the phase shift.\n"
            "Watch the output distribution and interference pattern update in real-time.\n\n"
            "Physics:\n"
            "• Phase = 0: Constructive interference\n"
            "• Phase = π: Destructive interference\n"
            "• Phase = 2π: Back to constructive"
        )
        help_font = QFont()
        help_font.setPointSize(9)
        help_label.setFont(help_font)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def create_schematic_panel(self):
        """Create a simplified MZI block diagram"""
        group = QGroupBox("Interferometer Schematic")
        layout = QVBoxLayout()

        self.schem_fig = Figure(figsize=(4, 2.5), dpi=100)
        self.schem_canvas = FigureCanvas(self.schem_fig)
        ax = self.schem_fig.add_subplot(1, 1, 1)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        def draw_bs(cx, cy, label):
            w, h = 0.08, 0.2
            rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                                  boxstyle="round,pad=0.02",
                                  facecolor='#e0e0e0', edgecolor='black', lw=1.5)
            ax.add_patch(rect)
            ax.text(cx, cy, label, ha='center', va='center', fontsize=7, fontweight='bold')

        # Input arrow
        ax.annotate('', xy=(0.08, 0.45), xytext=(0, 0.45),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
        ax.text(0.04, 0.52, 'Input', ha='center', fontsize=6.5, style='italic')

        # BS1
        draw_bs(0.18, 0.45, 'BS1')

        # Top path
        ax.plot([0.22, 0.58], [0.57, 0.57], 'k-', lw=1.5)

        # Bottom path with phase shifter
        ax.plot([0.22, 0.35], [0.33, 0.33], 'k-', lw=1.5)
        phi_circle = Circle((0.42, 0.33), 0.045, facecolor='#fff3cd',
                            edgecolor='red', lw=2, zorder=5)
        ax.add_patch(phi_circle)
        ax.text(0.42, 0.33, 'φ', ha='center', va='center', fontsize=9,
                fontweight='bold', color='red')
        ax.plot([0.465, 0.58], [0.33, 0.33], 'k-', lw=1.5)

        # BS2
        draw_bs(0.68, 0.45, 'BS2')

        # Output arrows
        ax.annotate('', xy=(0.78, 0.57), xytext=(0.88, 0.57),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#1f77b4'))
        ax.text(0.83, 0.64, 'Mode 0', ha='center', fontsize=6.5,
                fontweight='bold', color='#1f77b4')

        ax.annotate('', xy=(0.78, 0.33), xytext=(0.88, 0.33),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='darkorange'))
        ax.text(0.83, 0.26, 'Mode 1', ha='center', fontsize=6.5,
                fontweight='bold', color='darkorange')

        # Mirror indicators
        for x, y in [(0.22, 0.57), (0.58, 0.57), (0.22, 0.33), (0.58, 0.33)]:
            ax.plot(x, y, marker='s', color='#666', markersize=4, zorder=3)

        layout.addWidget(self.schem_canvas)
        group.setLayout(layout)

        self.schem_fig.tight_layout(pad=0.2)
        self.schem_canvas.draw()
        return group

    def create_distribution_panel(self):
        """Create the output distribution plot panel (small, below controls)"""
        group = QGroupBox("Output Distribution")
        layout = QVBoxLayout()

        self.dist_fig = Figure(figsize=(4, 3), dpi=100)
        self.dist_canvas = FigureCanvas(self.dist_fig)

        layout.addWidget(self.dist_canvas)
        group.setLayout(layout)
        return group

    def create_plot_panel(self):
        """Create the interference pattern plot panel (primary space)"""
        group = QGroupBox("Quantum Interference Pattern")
        layout = QVBoxLayout()

        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.fig)

        layout.addWidget(self.canvas)
        group.setLayout(layout)
        return group

    def on_phase_changed(self):
        """Handle phase slider changes"""
        phase_deg = self.phase_slider.value()
        self.current_phase = phase_deg * np.pi / 180.0

        # Update phase label (degrees primary)
        self.phase_label.setText(
            f"Phase: {phase_deg}° ({self.current_phase:.4f} rad)"
        )

        # Update phase indicator lines instantly (no debounce)
        try:
            self.phase_line_0.set_xdata([self.current_phase, self.current_phase])
            self.phase_line_1.set_xdata([self.current_phase, self.current_phase])
            self.canvas.draw_idle()
        except (AttributeError, RuntimeError):
            pass

        # Restart debounce timer
        self.debounce_timer.start(150)

    def on_slider_released(self):
        val = self.phase_slider.value()
        for snap in [0, 90, 180, 270, 360]:
            if abs(val - snap) <= 10:
                self.phase_slider.setValue(snap)
                break

    def on_samples_changed(self):
        """Handle samples spinbox changes"""
        self.current_samples = self.samples_spinbox.value()
        self.update_plots()

    def on_history_toggled(self):
        """Handle history checkbox toggle"""
        self.update_plots()

    def on_sweep(self):
        """Run a full phase sweep (0 to 2π)"""
        self.sweep_button.setEnabled(False)
        self.sweep_button.setText("Sweeping...")
        self.statusBar().showMessage("Running full phase sweep...")
        QApplication.processEvents()

        try:
            phase_range = np.linspace(0, 2 * np.pi, 30)
            phases, probs = self.mzi.sweep_phase(phase_range, num_samples=self.current_samples)
            self.sweep_phases = phases
            self.sweep_probs = probs
            self.update_plots()
            self.statusBar().showMessage(f"Sweep complete — {len(phase_range)} points")
        except Exception as e:
            self.statusBar().showMessage(f"Sweep error: {str(e)}")
            print(f"Error in sweep: {e}")

        self.sweep_button.setText("Full Phase Sweep (0°–360°)")
        self.sweep_button.setEnabled(True)

    def update_plots(self):
        """Update plots with current parameters"""
        self.statusBar().showMessage("Running simulation...")
        QApplication.processEvents()  # Update UI

        try:
            # Check cache first (avoid redundant simulations)
            cache_key = (round(self.current_phase, 4), self.current_samples)
            if cache_key in self.simulation_cache:
                results = self.simulation_cache[cache_key]
                cache_hit = True
            else:
                # Run simulation and cache result
                self.mzi.set_phase(self.current_phase)
                results = self.mzi.run_simulation(num_samples=self.current_samples)
                self.simulation_cache[cache_key] = results
                cache_hit = False

            # Update cache label
            self.cache_label.setText(f"Cache: {len(self.simulation_cache)} entries")

            # Extract probabilities
            prob_mode_0 = results.get((1, 0), 0)
            prob_mode_1 = results.get((0, 1), 0)
            theory = 0.5 * (1 - np.cos(self.current_phase))

            # Add to history
            self.history.append((self.current_phase, prob_mode_0, self.current_samples))

            # Update info label
            phase_deg = np.degrees(self.current_phase)
            self.info_label.setText(
                f"Phase: {phase_deg:.2f}° ({self.current_phase:.4f} rad)\n"
                f"Mode 0: {prob_mode_0:.4f}\n"
                f"Mode 1: {prob_mode_1:.4f}\n"
                f"Theory: {theory:.4f}"
            )

            # Clear previous plots
            self.dist_fig.clear()
            self.fig.clear()

            # Plot 1: Output distribution (on left panel)
            ax1 = self.dist_fig.add_subplot(1, 1, 1)
            states = [str(state) for state in results.keys()]
            probs = list(results.values())
            colors = ['#1f77b4', '#ff7f0e']

            bars = ax1.bar(states, probs, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            ax1.set_ylabel('Probability', fontsize=10, fontweight='bold')
            ax1.set_xlabel('Output State', fontsize=10, fontweight='bold')
            ax1.set_title(f'Phase = {phase_deg:.1f}°', fontsize=11, fontweight='bold')
            ax1.set_ylim([0, 1])
            ax1.grid(True, alpha=0.3, axis='y')

            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold'
                )

            # Plot 2 & 3: Interference patterns (main figure, right panel)
            phase_range = np.linspace(0, 2 * np.pi, 100)
            theory_0 = 0.5 * (1 - np.cos(phase_range))
            theory_1 = 0.5 * (1 + np.cos(phase_range))

            # --- Mode 0 subplot (top) ---
            ax2 = self.fig.add_subplot(2, 1, 1)
            ax2.plot(phase_range, theory_0, 'g--', linewidth=2.5, label='Theory',
                     alpha=0.2, dash_capstyle='round')

            h_phases = [h[0] for h in self.history[:-1]] if self.history_checkbox.isChecked() and len(self.history) > 1 else []
            if self.history_checkbox.isChecked() and len(self.history) > 1:
                h_probs_0 = [h[1] for h in self.history[:-1]]
                ax2.scatter(h_phases, h_probs_0, marker='s', s=80, alpha=0.3,
                            color='gray', label='History', edgecolors='darkgray', linewidth=0.5)

            if self.sweep_phases is not None and self.sweep_probs is not None:
                ax2.scatter(self.sweep_phases, self.sweep_probs, marker='o', s=30,
                            color='blue', alpha=0.6, label='Sweep', zorder=3)

            ax2.scatter(self.current_phase, prob_mode_0, marker='D', s=200, label='Current',
                        color='red', edgecolors='darkred', linewidth=2, zorder=5)

            ax2.axhspan(0.9, 1.0, alpha=0.1, color='green')
            ax2.axhspan(0.0, 0.1, alpha=0.1, color='red')
            ax2.axvline(0, color='gray', linestyle='--', alpha=0.3)
            ax2.axvline(np.pi, color='gray', linestyle='--', alpha=0.3)
            ax2.axvline(2 * np.pi, color='gray', linestyle='--', alpha=0.3)

            ax2.set_ylabel('Probability', fontsize=11, fontweight='bold')
            ax2.set_title('Output Mode 0', fontsize=12, fontweight='bold')
            ax2.set_ylim([-0.05, 1.05])
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=9, loc='upper right')
            # Intensity indicator
            g0 = prob_mode_0
            ax2.add_patch(Rectangle((0.01, 0.88), 0.06, 0.06, transform=ax2.transAxes,
                                    facecolor=(g0, g0, g0), edgecolor='#333', lw=0.8, zorder=10))
            ax2.text(0.04, 0.96, 'I', transform=ax2.transAxes, ha='center', va='bottom',
                     fontsize=7, fontweight='bold', color='#333')
            ax2.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
            ax2.set_xticklabels([])
            cursor2 = Cursor(ax2, useblit=True, color='red', linewidth=1.5, alpha=0.7)
            self.phase_line_0 = ax2.axvline(x=self.current_phase, color='red', linewidth=1,
                                            linestyle='-', alpha=0.8, zorder=6)

            # --- Mode 1 subplot (bottom) ---
            ax3 = self.fig.add_subplot(2, 1, 2)
            ax3.plot(phase_range, theory_1, '--', color='darkorange', linewidth=2.5, label='Theory',
                     alpha=0.2, dash_capstyle='round')

            if self.history_checkbox.isChecked() and len(self.history) > 1:
                h_probs_1 = [1 - h[1] for h in self.history[:-1]]
                ax3.scatter(h_phases, h_probs_1, marker='s', s=80, alpha=0.3,
                            color='gray', label='History', edgecolors='darkgray', linewidth=0.5)

            if self.sweep_phases is not None and self.sweep_probs is not None:
                ax3.scatter(self.sweep_phases, 1 - self.sweep_probs, marker='o', s=30,
                            color='darkorange', alpha=0.6, label='Sweep', zorder=3)

            ax3.scatter(self.current_phase, prob_mode_1, marker='s', s=180, label='Current',
                        color='purple', edgecolors='darkviolet', linewidth=2, zorder=5)

            ax3.axhspan(0.9, 1.0, alpha=0.1, color='green')
            ax3.axhspan(0.0, 0.1, alpha=0.1, color='red')
            ax3.axvline(0, color='gray', linestyle='--', alpha=0.3)
            ax3.axvline(np.pi, color='gray', linestyle='--', alpha=0.3)
            ax3.axvline(2 * np.pi, color='gray', linestyle='--', alpha=0.3)

            ax3.set_xlabel('Phase Shift (degrees)', fontsize=11, fontweight='bold')
            ax3.set_ylabel('Probability', fontsize=11, fontweight='bold')
            ax3.set_title('Output Mode 1', fontsize=12, fontweight='bold')
            ax3.set_ylim([-0.05, 1.05])
            ax3.grid(True, alpha=0.3)
            ax3.legend(fontsize=9, loc='upper right')
            # Intensity indicator
            g1 = prob_mode_1
            ax3.add_patch(Rectangle((0.01, 0.88), 0.06, 0.06, transform=ax3.transAxes,
                                    facecolor=(g1, g1, g1), edgecolor='#333', lw=0.8, zorder=10))
            ax3.text(0.04, 0.96, 'I', transform=ax3.transAxes, ha='center', va='bottom',
                     fontsize=7, fontweight='bold', color='#333')
            ax3.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi])
            ax3.set_xticklabels(['0°', '90°', '180°', '270°', '360°'])
            cursor3 = Cursor(ax3, useblit=True, color='red', linewidth=1.5, alpha=0.7)
            self.phase_line_1 = ax3.axvline(x=self.current_phase, color='red', linewidth=1,
                                            linestyle='-', alpha=0.8, zorder=6)

            # Adjust layout and draw both canvases
            self.dist_fig.tight_layout(pad=2.0)
            self.dist_canvas.draw()
            self.fig.tight_layout(pad=2.0, h_pad=3.0)
            self.canvas.draw()

            cache_status = "(cached)" if cache_hit else "(computed)"
            phase_deg = np.degrees(self.current_phase)
            self.statusBar().showMessage(
                f"Ready | Phase: {phase_deg:.2f}° ({self.current_phase:.4f} rad) | "
                f"Mode 0: {prob_mode_0:.4f} | Samples: {self.current_samples} {cache_status} | "
                f"History: {len(self.history)} entries"
            )

        except Exception as e:
            self.statusBar().showMessage(f"Error: {str(e)}")
            print(f"Error in update_plots: {e}")


def main():
    """Main entry point"""
    print("=" * 70)
    print("Mach-Zehnder Interferometer - Interactive Qt Application")
    print("=" * 70)
    print()
    print("Features:")
    print("  • Real-time phase control with slider")
    print("  • Live plot updates as you adjust the phase")
    print("  • Output distribution visualization")
    print("  • Quantum interference pattern display")
    print("  • Theory vs simulation comparison")
    print()

    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = MZIInterferometer()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
