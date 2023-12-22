import time
from datetime import datetime

import grpc  # noqa


def setup_logger_interceptor(app):
    """
    Request log blocker in debug mode.
    """

    class DebugRequestLogInterceptor(grpc.ServerInterceptor):
        def intercept_service(self, continuation, handler_call_details):
            begin_time = time.time()
            response = continuation(handler_call_details)
            app.log.info(f"{datetime.now()} INFO {handler_call_details.method} {time.time() - begin_time}s")
            return response

    return DebugRequestLogInterceptor
