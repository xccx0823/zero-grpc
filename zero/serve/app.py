import logging
import warnings
from concurrent import futures
from typing import Optional

import grpc  # noqa

from zero.setting.main import Setting


class current:  # noqa
    """When a project uses a structured directory, use global objects that are easy to use within the project."""
    app: Optional['GrpcApp'] = None


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
        self.setting = Setting()
        self.pb2_mapper: dict = {}
        self.alias_func_mappper: dict = {}


def create_logger() -> logging.Logger:
    logger = logging.getLogger('zero-grpc')
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    return logger


class Serve:

    def __init__(self,
                 address: str = 'localhost:8080',
                 workers: int = 10,
                 run_timeout: Optional[int] = None,
                 debug: bool = True):
        self.address = address
        self.run_timeout = run_timeout
        self.workers = workers
        self.debug = debug
        app = GrpcApp(workers)
        current.app = app
        self.app = current.app
        self.log = create_logger()

    def run(self):
        self._create_and_register_pb2_class()
        self.app.server.add_insecure_port(self.address)
        self.app.server.start()
        self.output_start_message()
        self.app.server.wait_for_termination(self.run_timeout)

    def add_pb2(self, pb2, pb2_grpc, alias: str):
        self.app.pb2_mapper[alias] = _PB2(pb2, pb2_grpc)

    def route(self, alias, name):
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
            self.log.debug(f"* Worker {self.workers}\n")
            for pb2_name, funcions in self.app.alias_func_mappper.items():
                self.log.debug(f"* Proto alias: {pb2_name}")
                for function in funcions.keys():
                    self.log.debug(f"* -----------> {function}")
            self.log.debug('\n\033[93mPress CTRL+C to quit\033[0m')
