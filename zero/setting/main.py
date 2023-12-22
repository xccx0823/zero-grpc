from typing import Optional


class Setting:
    """
    Global Configuration
    """

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
        """
        Load yaml file configuration.
        """
        import yaml  # noqa
        with open(path, 'r') as file:
            config_dict = yaml.safe_load(file)
        for config_key, config_value in config_dict.items():
            self.__dict__[config_key.upper()] = config_value

    def config(self, config_dict: dict):
        """
        Load dictionary form configuration.
        """
        for config_key, config_value in config_dict.items():
            self.__dict__[config_key.upper()] = config_value

    def ini_config(self, path: str):
        """
        Load ini file configuration.
        """
        import configparser
        config = configparser.ConfigParser()
        config.read(path)
        config_dict = {section: dict(config.items(section)) for section in config.sections()}
        for config_key, config_value in config_dict.items():
            self.__dict__[config_key.upper()] = config_value
