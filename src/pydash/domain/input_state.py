from dataclasses import dataclass


@dataclass(frozen=True)
class InputState:
    jump_pressed: bool  # true only on the frame the key is pressed