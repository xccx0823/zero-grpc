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


class Serve:

    def __init__(self, address: str = 'localhost:8080', max_workers: int = 10, run_timeout: Optional[int] = None):
        self.address = address
        self.run_timeout = run_timeout
        app = GrpcApp(max_workers)
        current.app = app
        self.app = current.app

    def run(self, *, address: Optional[str] = None, timeout: Optional[int] = None):
        self.app.server.add_insecure_port(address or self.address)
        self.app.server.start()
        self.app.server.wait_for_termination(timeout or self.run_timeout)

    def add_pb2(self, pb2, alias: str):
        self.app.pb2_mapper[alias] = _PB2(pb2)
