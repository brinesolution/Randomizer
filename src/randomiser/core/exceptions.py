class RandomiserError(Exception):
    """Base project exception."""


class ConfigError(RandomiserError):
    """Raised when config loading or validation fails."""


class SourceCollectionError(RandomiserError):
    """Raised when a source cannot be collected."""


class HealthGateError(RandomiserError):
    """Raised when health gating cannot complete."""


class ExperimentStorageError(RandomiserError):
    """Raised when experiment data cannot be saved."""
