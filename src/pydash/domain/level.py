from __future__ import annotations

from dataclasses import dataclass
from pydash.domain.rng import RandomSource


@dataclass(frozen=True)
class Level:
    length_cells: int  # fixed at 50 for now
    spike_cells: tuple[int, ...]  # indices in [0, length_cells-1] where a spike exists


def generate_level(rng: RandomSource, *, length_cells: int = 50) -> Level:
    # Simple random: independent spike per cell with a probability.
    # Keep early cells empty to avoid immediate unavoidable deaths.
    spike_prob = 0.18
    safe_prefix = 3

    spikes: list[int] = []
    for i in range(length_cells):
        if i < safe_prefix:
            continue
        if rng.random() < spike_prob:
            spikes.append(i)

    # Optional: ensure at least one spike sometimes (so levels aren't empty)
    if not spikes and length_cells > safe_prefix + 1 and rng.random() < 0.7:
        spikes.append(safe_prefix + 1)

    return Level(length_cells=length_cells, spike_cells=tuple(spikes))
