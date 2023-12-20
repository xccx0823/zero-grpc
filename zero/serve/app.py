import warnings
from concurrent import futures
from typing import Optional

import grpc  # noqa

from zero.setting.main import Setting


class current:  # noqa
    """When a project uses a structured directory, use global objects that are easy to use within the project."""
    app: Optional['GrpcApp'] = None


class _PB2:

    def __init__(self, pb2):
        self.pb2 = pb2
        self.add_to_server = None
        self.stub = None
        self.servicer = None
        for name in pb2.__dict__.keys():
            if name.endswith('Stub'):
                self.stub = pb2.__dict__[name]
            if name.endswith('Servicer'):
                self.servicer = pb2.__dict__[name]
            if name.startswith('add_') and name.endswith('_to_server'):
                self.add_to_server = pb2.__dict__[name]

        assert self.stub, "The pb2 structure is abnormal. The *Stub class cannot be found."
        assert self.add_to_server, ("The pb2 structure is abnormal and the "
                                    "add * to server registration function cannot be found.")
        assert self.servicer, "The pb2 structure is abnormal. The *Servicer class cannot be found."


class GrpcApp:

    def __init__(self, max_workers: int = 10):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self.setting = Setting()
        self.pb2_mapper: dict = {}
        self.alias_func_mapper: dict = {}


class Serve:

    def __init__(self,
                 address: str = 'localhost:8080',
                 max_workers: int = 10,
                 run_timeout: Optional[int] = None,
                 debug: bool = True):
        self.address = address
        self.run_timeout = run_timeout
        self.debug = debug
        app = GrpcApp(max_workers)
        current.app = app
        self.app = current.app

    def run(self):
        self._create_and_register_pb2_class()
        self.app.server.add_insecure_port(self.address)
        self.app.server.start()
        self.output_start_message()
        self.app.server.wait_for_termination(self.run_timeout)

    def add_pb2(self, pb2, alias: str):
        self.app.pb2_mapper[alias] = _PB2(pb2)

    def route(self, alias, name):
        def decorator(f):
            self.app.alias_func_mapper.setdefault(alias, {}).update({name: f})
            return f

        return decorator

    def _create_and_register_pb2_class(self):
        if not self.app.alias_func_mapper:
            return
        for alias, funcs in self.app.alias_func_mapper.items():
            pb2: _PB2 = self.app.pb2_mapper.get(alias)
            if not pb2:
                warnings.warn(f"No pb2 object alias {alias} was added.")
                continue
            instance = type(alias, (pb2.servicer,), funcs)
            pb2.add_to_server(instance(), self.app.server)

    def output_start_message(self):
        if self.debug:
            warnings.warn('The current debug is True.')
            print(f'[ZERO-DEBUG] listening on grpc://{self.address}')
