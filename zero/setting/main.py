class Setting:

    def load_yaml_config(self, path: str):
        pass

    def load_dict_config(self, mapper: dict):
        """加载字典形式的配置"""
        for config_key, config_value in mapper.items():
            self.__dict__[config_key.upper()] = config_value

    def load_ini_config(self, path: str):
        pass
