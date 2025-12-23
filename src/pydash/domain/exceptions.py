class PlayerDied(Exception):
    """Raised by the domain when the player hits a hazard and must restart."""


class LevelCompleted(Exception):
    """Raised when the player reaches the end of the level."""
