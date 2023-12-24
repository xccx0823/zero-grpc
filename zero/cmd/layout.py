ENUM_CONFIG_TYPES = ('ini', 'yaml')


def project_code_layout():
    name: str = input("project name: ").strip()
    port: str = input("port: ").strip()
    workers: int = int(input("workers ( default 10 ): ").strip() or 10)
    config_file_type: str = input("config file type ( yaml | ini ): ").strip()
    if config_file_type and config_file_type not in ENUM_CONFIG_TYPES:
        raise TypeError("The configuration file type is invalid.")
