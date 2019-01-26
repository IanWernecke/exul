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
    ('enumeratex', 'Enumerate extended information about windows on the system.', []),
    ('find', 'Find a particular window by the given information.', FIND_WINDOW_ARGS),
    ('geometry', 'Find the geometry of a particular window.', FIND_WINDOW_ARGS)
)
def main(args):
    """

    """
    # dump information about windows on the system
    if args.command in ('enumerate', 'enumeratex'):
        for window, level in windows():

            # initialize the list of information
            parts = []
            if level > 0:
                parts.append(level * '  ')

            # append window id and name
            parts.append((
                '--window-id={0} '
                '--window-name="{1}"'
            ).format(window.id, window.get_wm_name()))

            # attempt to append window class information
            window_class = window.get_wm_class()
            if window_class is not None:
                parts.append((
                    '--class-type="{0}" --class-name="{1}"'
                ).format(window_class[0], window_class[1]))

            # append geometry information if the command is enumeratex
            if args.command == 'enumeratex':
                geos = window.get_geometry()
                parts.append('--x {0} --y {1} --width {2} --height {3}'.format(
                    geos.x, geos.y, geos.width, geos.height
                ))

            print(' '.join(parts))

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
