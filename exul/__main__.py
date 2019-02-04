"""Execute common exul commands."""


import logging


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
    ('screenshot', 'Obtain the screen of a particular window and save it as a file.', FIND_WINDOW_ARGS + [
        (['location'], {'help': 'The location to write the screenshot.'})
    ]),
    ('subimage', 'Obtain a portion of a particular window as a file.', FIND_WINDOW_ARGS + [
        (['x'], {'type': int, 'help': 'The number of pixels across the screen to begin the image.'}),
        (['y'], {'type': int, 'help': 'The number of pixels down the screen to begin the image.'}),
        (['width'], {'type': int, 'help': 'The width of the subimage to obtain.'}),
        (['height'], {'type': int, 'help': 'The height of the subimage to obtain.'}),
        (['location'], {
            'default': None,
            'nargs': '?',
            'help': 'The location to write the screenshot.'
        })
    ])
)
def main(args):
    """Perform some function for the user, depending upon the command given."""
    # dump information about windows on the system
    if args.command == 'enumerate':
        for window, level in windows():
            print('  ' * level, window)
        return 0

    # find the window; all following commands should require a window
    window = find_window(
        window_id=args.window_id,
        window_name=args.window_name,
        class_type=args.class_type,
        class_name=args.class_name
    )

    # window not found
    if window is None:
        msg = 'Unable to find window with arguments: {0}'.format(args)
        logging.exception(msg)
        raise RuntimeError(msg)

    # attempt to find a particular window
    if args.command == 'find':
        print(window)
        return 0

    # save the image of a window to a file
    if args.command == 'screenshot':
        window.get_screenshot().save(args.location)
        return 0

    # obtain a portion of the window's image and show/display it
    if args.command == 'subimage':
        img = window.get_image(
            args.x,
            args.y,
            args.width,
            args.height
        )
        if args.location is None:
            img.show()
        else
            img.save(args.location)
        return 0

    return 0
