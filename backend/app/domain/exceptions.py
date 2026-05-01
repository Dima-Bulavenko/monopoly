class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidActionError(DomainError):
    """Raised when a command is not valid in the current game state."""


class NotYourTurnError(DomainError):
    """Raised when a player attempts an action outside their turn."""


class InsufficientFundsError(DomainError):
    """Raised when a player cannot afford a required payment."""


class PropertyNotOwnedError(DomainError):
    """Raised when an action requires property ownership that doesn't exist."""


class BuildingRuleViolationError(DomainError):
    """Raised when a building placement violates Monopoly building rules."""


class GameNotInProgressError(DomainError):
    """Raised when a game action is attempted on a game that isn't running."""
