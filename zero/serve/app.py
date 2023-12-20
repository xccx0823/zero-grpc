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

    def __init__(self, max_workers: int = 10):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self.setting = Setting()
        self.pb2_mapper: dict = {}
        self.alias_func_mappper: dict = {}


class Serve:

    def __init__(self, address: str = 'localhost:8080', max_workers: int = 10, run_timeout: Optional[int] = None):
        self.address = address
        self.run_timeout = run_timeout
        app = GrpcApp(max_workers)
        current.app = app
        self.app = current.app

    def run(self, *, address: Optional[str] = None, timeout: Optional[int] = None):
        self._create_and_register_pb2_class()
        self.app.server.add_insecure_port(address or self.address)
        self.app.server.start()
        self.app.server.wait_for_termination(timeout or self.run_timeout)

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
