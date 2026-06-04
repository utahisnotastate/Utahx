"""
Navier-Stokes inspired traffic-fluid metrics for Utahx.

Maps TCP connection flow to Reynolds-number turbulence monitoring,
aligned with utahisnotastate Millennium Prize fluid-dynamic models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

# Laminar-to-turbulent transition for normalized network Reynolds (dimensionless)
REYNOLDS_CRITICAL = 1.0
KINEMATIC_VISCOSITY_BASE = 1.0


@dataclass(frozen=True, slots=True)
class FlowState:
    """Instantaneous fluid state of the connection stream."""

    flow_rate: float
    max_flow_rate: float
    reynolds: float
    turbulence_index: float
    is_turbulent: bool


def reynolds_number(
    flow_rate: float,
    max_flow_rate: float,
    characteristic_length: float = 1.0,
    kinematic_viscosity: float = KINEMATIC_VISCOSITY_BASE,
) -> float:
    """
    Network Reynolds number Re = (U * L) / nu.

    U: inertial term (current requests per second)
    L: characteristic length (measurement window, seconds)
    nu: kinematic viscosity (baseline system resistance)
    """
    if kinematic_viscosity <= 0:
        return 0.0
    return (flow_rate * characteristic_length) / kinematic_viscosity


def turbulence_index(flow_rate: float, max_flow_rate: float) -> float:
    """
    Normalized excess inertial force vs capacity boundary (0 = laminar, >0 = turbulent).
    """
    if max_flow_rate <= 0:
        return 0.0
    return max(0.0, (flow_rate - max_flow_rate) / max_flow_rate)


def navier_stokes_viscosity_delay(
    flow_rate: float,
    max_flow_rate: float,
    *,
    damping_factor: float = 0.05,
    max_delay: float = 5.0,
) -> float:
    """
    Viscosity engine: smooths traffic waves when Re exceeds laminar regime.

    Under laminar flow, delay is zero. Under turbulence, delay scales with
    excess flow (equivalent to thickening the river from water to honey).
    """
    if flow_rate <= max_flow_rate:
        return 0.0
    excess_flow = flow_rate - max_flow_rate
    return min(excess_flow * damping_factor, max_delay)


def measure_flow(
    timestamps: Sequence[float],
    current_time: float,
    max_flow_rate: float,
    window_seconds: float = 1.0,
) -> FlowState:
    """Compute flow rate and fluid state from connection arrival timestamps."""
    recent = [t for t in timestamps if current_time - t <= window_seconds]
    flow_rate = float(len(recent))
    re = reynolds_number(flow_rate, max(max_flow_rate, 1e-9))
    turb = turbulence_index(flow_rate, max_flow_rate)
    return FlowState(
        flow_rate=flow_rate,
        max_flow_rate=max_flow_rate,
        reynolds=re,
        turbulence_index=turb,
        is_turbulent=re > REYNOLDS_CRITICAL * max_flow_rate
        or flow_rate > max_flow_rate,
    )


def reynolds_from_timestamps(
    timestamps: Sequence[float],
    current_time: float,
    max_flow_rate: int,
    window_seconds: float = 1.0,
) -> float:
    """Convenience: Reynolds number from raw timestamp buffer."""
    state = measure_flow(timestamps, current_time, float(max_flow_rate), window_seconds)
    return state.reynolds
