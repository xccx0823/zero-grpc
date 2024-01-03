import inspect
import logging
import warnings
from concurrent import futures
from typing import Optional, Union

import grpc  # noqa
from grpc._interceptor import service_pipeline  # noqa

from zero.serve.interceptor import setup_logger_interceptor
from zero.serve.setting import Setting
from zero.utils import camel_to_snake, snake_to_camel, dynamic_import

try:
    from zero.pkg.scheduler.scheduler import Apscheduler
except (ImportError, ModuleNotFoundError):
    pass


class current:  # noqa
    """
    When a project uses a structured directory, use global objects that are easy to use within the project.
    """
    app: Optional['GrpcApp'] = None
    setting: Optional['Setting'] = None

    # pkg
    apscheduler: Optional['Apscheduler'] = None


class Service:

    def __init__(self, pb2, pb2_grpc, servicer_name):
        self.pb2 = pb2
        self.pb2_grpc = pb2_grpc
        self.servicer_name = servicer_name
        self.add_to_server = None
        self.stub = None
        self.servicer = None

        self.stub = getattr(self.pb2_grpc, f'{self.servicer_name}Stub', None)
        assert_msg = "The pb2_grpc structure is abnormal. The *Stub class cannot be found."
        assert self.stub, assert_msg

        self.servicer = getattr(self.pb2_grpc, f'{self.servicer_name}Servicer', None)
        assert_msg = "The pb2_grpc structure is abnormal. The *Servicer class cannot be found."
        assert self.servicer, assert_msg

        self.add_to_server = getattr(self.pb2_grpc, f'add_{self.servicer_name}Servicer_to_server', None)
        assert_msg = "The pb2_grpc structure is abnormal and the add * to server registration function cannot be found."
        assert self.servicer, assert_msg

        self.funcs = dict(inspect.getmembers(self.servicer, predicate=inspect.isfunction)).keys()

    def tool_cls(self):
        return type('Service', (object,), {'srv': self.pb2})


class GrpcApp:

    def __init__(self, workers: int = 10):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

        self.service_mapper: dict = {}
        self.service_func_mapper: dict = {}
        self.needed_func_mapper: dict = {}


def create_logger(import_name) -> logging.Logger:
    """
    Provides a simple terminal log print object for use only in debug mode.
    """
    logger = logging.getLogger(import_name)
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    return logger


class Zero:
    """
    grpc server
    """

    def __init__(
            self,
            import_name,
            *,
            address: str = 'localhost:8080',
            workers: int = 10,
            run_timeout: Optional[int] = None,
            debug: bool = True,
            config: Union[str, dict, None] = None):

        self.import_name = import_name

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

        self.log = create_logger(import_name)

    def run(self):
        if self.debug:
            self.set_logger_interceptor()
        self._create_and_register_service_class()
        self.app.server.add_insecure_port(self.address)
        self.app.server.start()
        self._output_start_message()
        self.app.server.wait_for_termination(self.run_timeout)

    def add_service(self, pb2, pb2_grpc):
        """
        Add python code files generated with the grpc tool.
        """
        services = self._generate_services(pb2, pb2_grpc)
        for service in services:
            self.app.service_mapper[service.servicer_name] = service
            self.app.needed_func_mapper[service.servicer_name] = service.funcs

    @staticmethod
    def _generate_services(pb2, pb2_grpc):
        module_attributes = dir(pb2_grpc)
        service_classes = [getattr(pb2_grpc, attr) for attr in module_attributes if 'Servicer' in attr]
        grpc_service_classes = [cls for cls in service_classes if inspect.isclass(cls)]
        services = []
        for cls in grpc_service_classes:
            cls_name: str = cls.__name__
            servicer_name = cls_name[:-len('Servicer')]
            service = Service(pb2, pb2_grpc, servicer_name)
            services.append(service)
        return services

    def rpc(self, name: Optional[str] = None):
        """
        Function registration decorator for grpc's proto function.
        """
        if '/' in name:
            _, service_name, rpc_name = name.split('/')
        else:
            service_name = name
            rpc_name = None

        def decorator(f):
            if service_name not in self.app.needed_func_mapper:
                raise KeyError(f'There is no service registered with the name {service_name}')

            if rpc_name is not None:
                self._set_to_service_func_mapper(service_name, rpc_name, f)
            else:
                func_name = f.__name__
                needed_funcs = self.app.needed_func_mapper[service_name]
                if func_name in needed_funcs:
                    self._set_to_service_func_mapper(service_name, func_name, f)
                elif snake_to_camel(func_name) in needed_funcs:
                    self._set_to_service_func_mapper(service_name, snake_to_camel(func_name), f)
                else:
                    raise KeyError(f"The current function '{func_name}' cannot be "
                                   f"added to the proto service {service_name}")
            return f

        return decorator

    def server(self, name: str):
        """
        Class registration decorator for prototype functions for grpc.
        """

        def decorator(c):
            cls_funcs = dict(inspect.getmembers(c, predicate=inspect.isfunction))
            if name not in self.app.needed_func_mapper:
                raise KeyError(f'Current service {name} not added.')
            needed_funcs = self.app.needed_func_mapper[name]
            for needed_func_name in needed_funcs:
                if needed_func_name in cls_funcs:
                    f = cls_funcs[needed_func_name]
                    self._set_to_service_func_mapper(name, needed_func_name, f)
                elif camel_to_snake(needed_func_name) in cls_funcs:
                    f = cls_funcs[camel_to_snake(needed_func_name)]
                    self._set_to_service_func_mapper(name, needed_func_name, f)
            return c

        return decorator

    def register_func(self, func: str, *, name: Optional[str] = None):
        self.rpc(name)(dynamic_import(func))

    def register_view(self, func: str, *, alias: str):
        self.server(alias)(dynamic_import(func))

    def use(self, interceptor):
        """
        Register the global interceptor.
        """
        interceptor_pipeline = self.app.server._state.__dict__['interceptor_pipeline']  # noqa
        if interceptor_pipeline is None:
            self.app.server._state.__dict__['interceptor_pipeline'] = service_pipeline([interceptor()])  # noqa
        else:
            self.app.server._state.__dict__['interceptor_pipeline'] = service_pipeline(  # noqa
                list(self.app.server._state.__dict__['interceptor_pipeline'].interceptors) + [interceptor()]  # noqa
            )

    def _set_to_service_func_mapper(self, service_name: str, func_name: str, func):
        if service_name not in self.app.service_func_mapper:
            self.app.service_func_mapper[service_name] = {func_name: func}
        else:
            func_mapper = self.app.service_func_mapper[service_name]
            # If you have already registered, the second registration will not take effect and there will be a warning.
            if func_name in func_mapper:
                warn_msg = f'The required function {func_name} in service {service_name} has been registered.'
                warnings.warn(warn_msg)
            else:
                self.app.service_func_mapper[service_name].update({func_name: func})

    def _create_and_register_service_class(self):
        """
        Various registration methods eventually generate dynamic classes that conform to the proto file definition.
        """
        if not self.app.service_func_mapper:
            return
        for alias, funcs in self.app.service_func_mapper.items():
            service = self.app.service_mapper.get(alias)
            if not service:
                warnings.warn(f'Current service {service} not added.')
                continue
            instance = type(alias, (service.servicer, service.tool_cls()), funcs)
            service.add_to_server(instance(), self.app.server)

    def _output_start_message(self):
        """
        Terminal information in debug mode.
        """
        if self.debug:
            self.log.warning('WARNING: The current debug mode is true, please do not use it in production '
                             'environment.')
            self.log.debug(f"* Serving Zero grpc app '{self.import_name}'")
            self.log.debug(f"* Listening on grpc://{self.address}")
            self.log.debug(f"* The number of workers is {self.workers}\n")
            for service_name, functions in self.app.service_func_mapper.items():
                self.log.debug(f"* Service: {service_name}")
                for function in self.app.needed_func_mapper[service_name]:
                    if function in functions.keys():
                        self.log.debug(f"* -----------> {function} " + "\033[92m√\033[0m")
                    else:
                        self.log.debug(f"* -----------> {function} " + "\033[93m×\033[0m")
            self.log.debug('\n\033[93mPress CTRL+C to quit\033[0m\n')

    def set_logger_interceptor(self):
        """
        Set the log blocker.
        """
        logger_interceptor = setup_logger_interceptor(self)
        self.use(logger_interceptor)
