from typing import Optional


class Setting:
    """Global Configuration"""

    # Default configuration variables.
    # service listening address.
    ADDRESS: Optional[str] = None
    # number of threads started by the service.
    WORKERS: Optional[int] = None
    # specify a time to listen for shutdown events in the loop.
    # the parameters required for the 'wait_for_termination' method of the grpc object
    RUN_TIMEOUT: Optional[int] = None
    # debug mode.
    DEBUG: Optional[bool] = None

    def yaml_config(self, path: str):
        """Load yaml file configuration."""

    def config(self, mapper: dict):
        """Load dictionary form configuration."""
        for config_key, config_value in mapper.items():
            self.__dict__[config_key.upper()] = config_value

    def ini_config(self, path: str):
        """Load ini file configuration."""
