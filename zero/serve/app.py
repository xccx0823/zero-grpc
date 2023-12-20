from concurrent import futures
from typing import Optional

import grpc  # noqa

from zero.setting.main import Setting


class _PB2:

    def __init__(self, pb2):
        self.pb2 = pb2
        self.add_func = None
        self.stub = None
        self.servicer = None
        for name in pb2.__dict__.keys():
            if name.endswith('Stub'):
                self.stub = pb2.__dict__[name]
            if name.endswith('Servicer'):
                self.servicer = pb2.__dict__[name]
            if name.startswith('add_') and name.endswith('_to_server'):
                self.servicer = pb2.__dict__[name]


class _Serve:

    def __init__(self, address: str = 'localhost:8080', max_workers: int = 10, run_timeout: Optional[int] = None):
        self.address = str(address)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=int(max_workers)))
        self.run_timeout = run_timeout

        self.setting = Setting()
        self.pb2_mapper: dict = {}

    def add_pb2(self, pb2, alias: str):
        self.pb2_mapper[alias] = _PB2(pb2)


class Serve(_Serve):

    def run(self, *, address: Optional[str] = None, timeout: Optional[int] = None):
        self.server.add_insecure_port(address or self.address)
        self.server.start()
        self.server.wait_for_termination(timeout or self.run_timeout)
