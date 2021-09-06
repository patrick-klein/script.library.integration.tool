#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Collection of log functions."""

import xbmc

from resources import ADDON_NAME
from resources import ADDON_VERSION
from resources import IN_DEVELOPMENT
from resources import DEFAULT_LOG_LEVEL


def log_msg(msg, loglevel=DEFAULT_LOG_LEVEL):
    """Log message with addon name and version to kodi log."""
    xbmc.log("{0} v{1} --> {2}".format(ADDON_NAME,
             ADDON_VERSION, msg), level=loglevel)


def logged_function(func):
    """Decorator for logging function call and return values (at default log level)."""
    # TODO: option to have "pre-" and "post-" logging
    def wrapper(*args, **kwargs):
        """function wrapper."""
        # Call the function and get the return value
        ret = func(*args, **kwargs)
        # Only log if IN_DEVELOPMENT is set
        if IN_DEVELOPMENT:
            # Define the string for the function call (include class name for methods)
            is_method = args and hasattr(args[0].__class__, func.__name__)
            parent = args[0].__class__.__name__ if is_method else func.__module__.replace(
                'resources.lib.', ''
            )
            func_str = '{0}.{1}'.format(parent, func.__name__)
            # Pretty formating for argument string
            arg_list = list()
            for arg in args[1 if is_method else 0:]:
                arg_list.append("'{0}'".format(arg))
            for key, val in kwargs.items():
                arg_list.append(
                    '{0}={1}'.format(key, "'{0}'".format(val)))
            arg_str = '({0})'.format(', '.join(arg_list))
            # Add line breaks and limit output if ret value is iterable
            if isinstance(ret, str):
                ret_str = "'{0}'".format(ret)
            else:
                try:
                    ret_list = ['\n' + str(x) for x in ret[:5]]
                    if len(ret) > 5:
                        ret_list += [
                            '\n+{0} more items...'.format(len(ret) - 5)]
                    ret_str = str().join(ret_list)
                except TypeError:
                    ret_str = str(ret)
            # Log message at default loglevel
            message = '{0}{1}: {2}'.format(func_str, arg_str, ret_str)
            log_msg(message)
        # Return ret value from wrapper
        return ret
    return wrapper
