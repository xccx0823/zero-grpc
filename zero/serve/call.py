from functools import wraps


def rpc(name):
    def wrapper(func):
        @wraps(func)
        def inner(self, request, context):
            setattr(self, name, func)
            return func(self, request, context)

        return inner

    return wrapper
