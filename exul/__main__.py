"""Execute common exul commands."""


from . import find_window, windows
from .decorators import MainCommands


FIND_WINDOW_ARGS = [
    (['--wid', '--window-id'], {
        'default': None,
        'dest': 'window_id',
        'help': 'The window ID to obtain.'
    }), (['--win', '--window-name'], {
        'default': None,
        'dest': 'window_name',
        'help': 'The window name to obtain.'
    }), (['--clt', '--class-type'], {
        'default': None,
        'dest': 'class_type',
        'help': 'The window class type to obtain.'
    }), (['--cln', '--class-name'], {
        'default': None,
        'dest': 'class_name',
        'help': 'The window class name to obtain.'
    })
]


@MainCommands(
    ('enumerate', 'Enumerate all windows on the system.', []),
    ('find', 'Find a particular window by the given information.', FIND_WINDOW_ARGS),
    ('geometry', 'Find the geometry of a particular window.', FIND_WINDOW_ARGS)
)
def main(args):
    """

    """
    # dump information about windows on the system
    if args.command == 'enumerate':
        for window, level in windows():
            print('  ' * level, window)
        return 0

    # dump information about a particular window
    if args.command in ('find', 'geometry'):
        window = find_window(
            window_id=args.window_id,
            window_name=args.window_name,
            class_type=args.class_type,
            class_name=args.class_name
        )
        if args.command == 'find':
            print(window)
        elif args.command == 'geometry':
            print(window.get_geometry())

        return 0

    # TODO: MOAR

    return 0
