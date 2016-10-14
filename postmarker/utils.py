# coding: utf-8


def chunks(container, n):
    """
    Split a container into n-sized chunks.
    """
    for i in range(0, len(container), n):
        yield container[i: i + n]
