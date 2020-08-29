try:
    from inspect import signature

    def get_args(cls):
        return list(signature(cls).parameters)


except ImportError:

    def get_args(cls):
        from inspect import getargspec

        return getargspec(cls.__init__).args[1:]
