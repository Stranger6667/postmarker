# coding: utf-8
from .exceptions import ConfigError


def chunks(container, n):
    """
    Split a container into n-sized chunks.
    """
    for i in range(0, len(container), n):
        yield container[i: i + n]


class ManageableMeta(type):

    def __new__(mcs, name, bases, members):
        new_class = super(ManageableMeta, mcs).__new__(mcs, name, bases, members)
        mcs.check_managers(new_class)
        return new_class

    @staticmethod
    def check_managers(new_class):
        """
        `_managers` attribute should not contains:

         - Managers with same names
         - Managers with names that clashes with client's attributes
        """
        managers_names = [manager.name for manager in new_class._managers]
        if len(managers_names) != len(set(managers_names)):
            raise ConfigError('Defined managers names are not unique')
        if any(hasattr(new_class, manager_name) for manager_name in managers_names):
            raise ConfigError('Defined managers names override client\'s members')
