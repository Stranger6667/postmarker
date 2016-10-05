# coding=utf-8


class PostmarkerException(BaseException):
    """
    Base class for all exceptions in Postmarker.
    """


class ConfigError(PostmarkerException):
    """
    Indicates that some entities have invalid configuration.
    """
