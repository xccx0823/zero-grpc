import logging
import warnings
from concurrent import futures
from typing import Optional, Union

import grpc  # noqa

from zero.setting.main import Setting


class current:  # noqa
    """When a project uses a structured directory, use global objects that are easy to use within the project."""
    app: Optional['GrpcApp'] = None
    setting: Optional['Setting'] = None


class _PB2:

    def __init__(self, pb2, pb2_grpc):
        self.pb2 = pb2
        self.pb2_grpc = pb2_grpc
        self.add_to_server = None
        self.stub = None
        self.servicer = None
        for name in pb2_grpc.__dict__.keys():
            if name.endswith('Stub'):
                self.stub = pb2_grpc.__dict__[name]
            if name.endswith('Servicer'):
                self.servicer = pb2_grpc.__dict__[name]
            if name.startswith('add_') and name.endswith('_to_server'):
                self.add_to_server = pb2_grpc.__dict__[name]

        assert self.stub, "The pb2_grpc structure is abnormal. The *Stub class cannot be found."
        assert self.add_to_server, ("The pb2_grpc structure is abnormal and the "
                                    "add * to server registration function cannot be found.")
        assert self.servicer, "The pb2_grpc structure is abnormal. The *Servicer class cannot be found."

    def tool_cls(self):
        return type('PB2', (object,), {'pb2': self.pb2})


class GrpcApp:

    def __init__(self, workers: int = 10):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
        self.pb2_mapper: dict = {}
        self.alias_func_mappper: dict = {}


def create_logger() -> logging.Logger:
    """Provides a simple terminal log print object for use only in debug mode."""
    logger = logging.getLogger('zero-grpc')
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    return logger


class Serve:
    """grpc server"""

    def __init__(self, *,
                 address: str = 'localhost:8080',
                 workers: int = 10,
                 run_timeout: Optional[int] = None,
                 debug: bool = True,
                 config: Union[str, dict, None] = None):

        # load configuration
        self.setting = Setting()
        current.setting = self.setting
        if config and isinstance(config, dict):
            self.setting.config(config)
        elif config and isinstance(config, str) and config.endswith('.ini'):
            self.setting.ini_config(config)
        elif config and isinstance(config, str) and (config.endswith('.yaml') or config.endswith('.yml')):
            self.setting.yaml_config(config)

        # The configuration of the configuration file takes
        # precedence over the parameter configuration of the function.
        self.address = address if self.setting.ADDRESS is None else self.setting.ADDRESS
        self.run_timeout = run_timeout if self.setting.RUN_TIMEOUT is None else self.setting.RUN_TIMEOUT
        self.workers = workers if self.setting.WORKERS is None else self.setting.WORKERS
        self.debug = debug if self.setting.DEBUG is None else self.setting.DEBUG

        self.app = GrpcApp(self.workers)
        current.app = self.app

        self.log = create_logger()

    def run(self):
        self._create_and_register_pb2_class()
        self.app.server.add_insecure_port(self.address)
        self.app.server.start()
        self.output_start_message()
        self.app.server.wait_for_termination(self.run_timeout)

    def add_pb2(self, pb2, pb2_grpc, alias: str):
        """Add python code files generated with the grpc tool."""
        self.app.pb2_mapper[alias] = _PB2(pb2, pb2_grpc)

    def route(self, alias, name):
        """Function registration decorator for grpc's proto function."""

        def decorator(f):
            self.app.alias_func_mappper.setdefault(alias, {}).update({name: f})
            return f

        return decorator

    def _create_and_register_pb2_class(self):
        if not self.app.alias_func_mappper:
            return
        for alias, funcs in self.app.alias_func_mappper.items():
            pb2: _PB2 = self.app.pb2_mapper.get(alias)
            if not pb2:
                warnings.warn(f"No pb2 object alias {alias} was added.")
                continue
            instance = type(alias, (pb2.servicer, pb2.tool_cls()), funcs)
            pb2.add_to_server(instance(), self.app.server)

    def output_start_message(self):
        if self.debug:
            self.log.warning('WARNING: The current debug mode is true, please do not use it in production '
                             'environment.')
            self.log.debug(f"* Listening on grpc://{self.address}")
            self.log.debug(f"* The number of workers is {self.workers}\n")
            for pb2_name, funcions in self.app.alias_func_mappper.items():
                self.log.debug(f"* Proto alias: {pb2_name}")
                for function in funcions.keys():
                    self.log.debug(f"* -----------> {function}")
            self.log.debug('\n\033[93mPress CTRL+C to quit\033[0m')
