#!python3
"""This file is designed to provide decorators for other files."""
# pylint: disable=useless-object-inheritance; aiming for py2 and py3 compatability
# pylint: disable=too-few-public-methods; inheritance not accounted for


import argparse
import inspect
import logging
import os
import shlex
import sys

from functools import wraps


#
#   Function Decorators
#

def args2keywords(function):
    """
    Wrap a function such that is converts given NameSpace objects into keywords.

    :param function: the decorated function that requires keywords
    :return: a wrapped function that accepts args
    """
    @wraps(function)
    def wrapper(args, **kwargs):
        kwargs.update(**vars(args))
        return function(**kwargs)
    return wrapper


#
#   Argument Intercept Decorators
#

class ArgumentIntercept(object):
    """Parse the arguments given to the decorated function and pass the resulting NameSpace."""

    # overwrite this in children
    main_class = False

    # Main Decorators require this for verbosity tuple injection
    verbosity_tuple = (
        ['-v', '--verbosity'],
        {
            'action': 'count',
            'default': 0,
            'dest': 'verbosity',
            'help': 'Configure how verbose the logger should be.'
        }
    )

    def __init__(self):
        """Assign the tuples to self, to be passed in upon calling."""
        self.parser = argparse.ArgumentParser()

    def __call__(self, function):
        """Intercept the given arguments and pass them to the parser."""
        @wraps(function)
        def wrapper(arguments):

            if (arguments is None) or isinstance(arguments, list):
                args = self.parser.parse_args(arguments)

            elif isinstance(arguments, (str, unicode)):
                args = self.parser.parse_args(shlex.split(arguments))

            else:
                raise RuntimeError('Unhandled arguments type: "{}"'.format(type(arguments)))

            # logging should be configured if this is a main class and we are inside '__main__'.
            if self.main_class:

                level = logging.WARNING - (10 * args.verbosity)
                logging.basicConfig(
                    format='%(asctime)s [%(levelname)9s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=level
                )
                logging.debug('Logging level set to: %d', level)

            return function(args)

        # if the parent frame's __name__ is not __main__, this is not a "main" class
        if inspect.currentframe().f_back.f_globals['__name__'] != '__main__':
            self.main_class = False

        # return the function if this is not a main class
        if not self.main_class:
            return wrapper

        # call the decorated function and exit with the system code if possible.
        result = wrapper(None)
        if isinstance(result, int):
            sys.exit(result)
        sys.exit(0)


class Parse(ArgumentIntercept):
    """Parse the given arguments with CreateParser."""

    main_class = False

    def __init__(self, *tuples):
        """Add all of the arguments to the parser."""
        super(Parse, self).__init__()
        for args, kwargs in tuples:
            self.parser.add_argument(*args, **kwargs)


class ParseCommands(ArgumentIntercept):
    """Parse the given arguments with CreateParserCommands."""

    main_class = False

    def __init__(self, *command_tuples):
        """Add all of the subparsers to the parser."""
        super(ParseCommands, self).__init__()
        subparsers = self.parser.add_subparsers(dest='command')
        for cmd_name, cmd_help, tuples in command_tuples:
            option = subparsers.add_parser(cmd_name, help=cmd_help)
            for args, kwargs in tuples:
                option.add_argument(*args, **kwargs)


#
#   Main Decorators
#

class Main(Parse):
    """Parse and call the decorated function."""

    main_class = True

    def __init__(self, *tuples):
        """Inject the verbosity tuple into the (args, kwargs) tuples."""
        super(Main, self).__init__(self.verbosity_tuple, *tuples)


class MainCommands(ParseCommands):
    """ParseCommands and call the decorated function."""

    main_class = True

    def __init__(self, *command_tuples):
        """Inject the verbosity tuple into the command tuples."""
        super(MainCommands, self).__init__(*[
            (cmd_name, cmd_help, tuple(list(tuples) + [self.verbosity_tuple]))
            for cmd_name, cmd_help, tuples in command_tuples
        ])


#
#   Require Class Decorators
#

class RequirePaths(object):
    """A decorator that raises a RuntimeError if any of the given args are not True."""

    def __init__(self, *paths):
        """Ensure each argument given to this decorator evaluates to True with the function."""
        self.paths = paths

    def __call__(self, decorated):
        """Return the same function as was decorated."""
        @wraps(decorated)
        def require_paths_wrapper(*args, **kwargs):
            for path in self.paths:
                if not os.path.exists(path):
                    raise RuntimeError('Path not found: "{0}"'.format(path))
            return decorated(*args, **kwargs)
        return require_paths_wrapper


class RequireDirs(RequirePaths):
    """A decorator that raises a RuntimeError if any of the given args are not directories."""

    def __call__(self, decorated):
        """Ensure the given paths (directories) are found each time the given function is called."""
        @wraps(decorated)
        def require_dirs_wrapper(*args, **kwargs):
            for path in self.paths:
                if not os.path.isdir(path):
                    raise RuntimeError('Directory not found: "{0}"'.format(path))
            return decorated(*args, **kwargs)
        return require_dirs_wrapper


class RequireFiles(RequirePaths):
    """A decorator that raises a RuntimeError if any of the given args are not files."""

    def __call__(self, decorated):
        """Ensure the given paths (files) are found each time the given function is called."""
        @wraps(decorated)
        def require_files_wrapper(*args, **kwargs):
            for path in self.paths:
                if not os.path.isfile(path):
                    raise RuntimeError('File not found: "{0}"'.format(path))
            return decorated(*args, **kwargs)
        return require_files_wrapper


#
#   Logging Class Decorators
#

class LogLevelContainer(object):
    """A class object to hold a logging level, for use when inherited."""

    def __init__(self, level=logging.NOTSET):
        """Store a log level."""
        self.level = level


class LogSteps(LogLevelContainer):
    """A class object to hold a logging level and report when a function is entered and exited."""

    def __call__(self, function):
        """Report when a function enters and exits."""
        @wraps(function)
        def steps_wrapper(*args, **kwargs):
            logging.log(self.level, 'Function: %s, Enter', function.__name__)
            result = function(*args, **kwargs)
            logging.log(self.level, 'Function: %s, Exit', function.__name__)
            return result
        return steps_wrapper


class LogArguments(LogLevelContainer):
    """A class object to hold a logging level and report the args and kwargs of a decorated function."""

    def __call__(self, function):
        """Log the args and kwargs of the decorated function."""
        @wraps(function)
        def arguments_wrapper(*args, **kwargs):
            for arg in args:
                logging.log(self.level, 'Function: %s, Arg: %r', function.__name__, arg)
            for key in kwargs:
                logging.log(self.level, 'Function: %s, Key: %r, Value: %r', function.__name__, key, kwargs[key])
            return function(*args, **kwargs)
        return arguments_wrapper


class LogResult(LogLevelContainer):
    """A class object to hold a logging level and report the result of a function at that level."""

    def __call__(self, function):
        """Log the result of a decorated function."""
        @wraps(function)
        def result_wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            logging.log(self.level, 'Function: %s, Result: %r', function.__name__, result)
            return result
        return result_wrapper


class LogAll(LogLevelContainer):
    """A class object to log entry, args, kwargs, result, and exit of a function."""

    def __call__(self, function):
        """Wrap a bunch of decorators around the given function so information is logged."""
        @LogSteps(self.level)
        @LogArguments(self.level)
        @LogResult(self.level)
        @wraps(function)
        def all_wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        return all_wrapper


class LogDecoratorContainer(object):
    """An object to be created that houses decorator functions."""

    def __init__(self, level=logging.NOTSET):
        """Assign the decorations to self."""
        self.steps = LogSteps(level)
        self.args = LogArguments(level)
        self.result = LogResult(level)
        self.all = LogAll(level)


# define some convenient decorator containers
# pylint: disable=invalid-name; these are fine decorator names
notset = LogDecoratorContainer(logging.NOTSET)
debug = LogDecoratorContainer(logging.DEBUG)
info = LogDecoratorContainer(logging.INFO)
warning = LogDecoratorContainer(logging.WARNING)
error = LogDecoratorContainer(logging.ERROR)
critical = LogDecoratorContainer(logging.CRITICAL)
