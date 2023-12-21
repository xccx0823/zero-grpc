class Setting:
    """Global Configuration"""

    # Default configuration variables.
    # service listening address.
    ADDRESS: str = 'localhost:8080'
    # number of threads started by the service.
    WORKERS: int = 10
    # specify a time to listen for shutdown events in the loop.
    # the parameters required for the 'wait_for_termination' method of the grpc object
    RUN_TIMEOUT: int = 60 * 60 * 24
    # debug mode, default enabled.
    DEBUG: bool

    def load_yaml_config(self, path: str):
        """Load yaml file configuration."""

    def load_dict_config(self, mapper: dict):
        """Load dictionary form configuration."""
        for config_key, config_value in mapper.items():
            self.__dict__[config_key.upper()] = config_value

    def load_ini_config(self, path: str):
        """Load ini file configuration."""
