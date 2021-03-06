"""This library handles various function calls to an X window server."""


# standard imports
from time import sleep


# installed imports
from PIL import Image


# installed Xlib resources
from Xlib import X
from Xlib.display import Display
from Xlib.protocol import event
from Xlib.protocol.request import InternAtom
from Xlib.XK import string_to_keysym


# global display object
DISPLAY = Display()


# 24 ms
KEY_EVENT_INTERVAL = 0.024
MOUSE_HELD_DURATION = 0.024

MOUSE_LEFT = 1
MOUSE_RIGHT = 2
MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5


# a simple class to simulate holding down a key while other things occur
class KeyPressed(object):  # pylint: disable=useless-object-inheritance; aiming for py2 and py3 compatability
    """Holds down a key while other events are happening and then automatically sends a key_release when done."""

    def __init__(self, window, key):
        """Save a reference to the window and the keycode of the given key."""
        self.window = window
        self.code = get_key_code(key)

    def __enter__(self):
        """Upon entering, press the key."""
        key_press(self.window, self.code)

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Upon exiting, release the key."""
        key_release(self.window, self.code)


#
#   send_event: the primary window event issuer
#

def send_event(
        window,
        event_class,
        event_type,
        keycode,
        x=0,
        y=0,
        modifiers=0
    ):  # pylint: disable=too-many-arguments; complex function
    """
    Send an event to a given window.

    Examples of event classes:
        Xlib.protocol.event.ButtonPress
        Xlib.protocol.event.ButtonRelease

    :return: None
    """
    # Event: send_event?
    # This attribute is normally 0, meaning that the event was generated by the
    # X server. It is set to 1 if this event was instead sent from another
    # client.
    # window.send_event(event)

    window.send_event(event_class(

        # Stores the X type code of this event. Type codes are integers in the
        # range 2-127, and are defined with symbolic names in Xlib.X. The
        # symbolic names are the same as the event class names, except for the
        # special event AnyEvent.
        type=event_type,

        # For KeyPress and KeyRelease, this is the keycode of the event key.
        # For ButtonPress and ButtonRelease, this is the button of the event.
        # For MotionNotify, this is either X.NotifyNormal or X.NotifyHint.
        detail=keycode,
        # detail=1,

        # The server X time when this event was generated.
        # WARNING: CurrentTime apparently creates strange race conditions (stackoverflow)
        time=X.CurrentTime,

        # The root window which the source window is an inferior of.
        root=X.NONE,

        # The window the event is reported on.
        window=window,

        # If the source window is an inferior of window, child is set to the
        # child of window that is the ancestor of (or is) the source window.
        # Otherwise it is set to X.NONE.
        child=X.NONE,

        # The pointer coordinates at the time of the event, relative to the
        # root window.
        root_x=0,
        root_y=0,

        # The pointer coordinates at the time of the event, relative to window.
        # If window is not on the same screen as root, these are set to 0.
        event_x=x,
        event_y=y,

        # The logical state of the button and modifier keys just before the
        # event.
        state=modifiers,

        same_screen=1

    ))

    # TODO: does this work?
    # window.display.sync()
    window.display.flush()


#
#   general mouse functions
#

def mouse_down(window, x, y, code):
    """
    Send a ButtonPress event to a window at the given coordinates.

    :param window: a handle to a window
    :param x:
    :param y:
    :param code: the mouse button to press
    :return: None
    """
    send_event(
        window=window,
        event_class=event.ButtonPress,
        event_type=X.ButtonPress,
        keycode=code,
        x=x,
        y=y
    )


def mouse_move(window, x, y):
    """
    Send a MotionNotify event to a window at the given coordinates.

    :param window: a handle to a window
    :param x:
    :param y:
    :param code:
    :return: None
    """
    send_event(
        window=window,
        event_class=event.MotionNotify,
        event_type=X.MotionNotify,
        keycode=X.NotifyNormal,
        x=x,
        y=y
    )


def mouse_up(window, x, y, code):
    """
    Send a ButtonRelease event to a window at the given coordinates.

    :param window: a handle to a window
    :param x:
    :param y:
    :param code: the mouse button to release
    :return: None
    """
    send_event(
        window=window,
        event_class=event.ButtonRelease,
        event_type=X.ButtonRelease,
        keycode=code,
        x=x,
        y=y
    )


#
#   basic click functions that use the mouse functions
#

def click(window, x, y, code=MOUSE_LEFT):
    """
    Create an event that appears to be a mouse click at the given coordinates of a window.

    :param window: a reference to a window
    :param x: distance in pixels across a window
    :param y: distance in pixels down a window
    :param code: the event code to send at the coordinates
    :return: None
    """
    mouse_move(window, x, y)
    mouse_down(window, x, y, code)
    sleep(MOUSE_HELD_DURATION)
    mouse_up(window, x, y, code)

    return code


def click_left(window, x, y):
    """
    Send a 'click' with the left mouse button.

    :param window: a reference to a window
    :param x: distance in pixels across a window
    :param y: distanc ein pixels down a window
    :return:
    """
    return click(window, x, y, MOUSE_LEFT)


def click_right(window, x, y):
    """
    Send a 'click' with the right mouse button.

    :param window: a reference to a window
    :param x: distance in pixels across a window
    :param y: distanc ein pixels down a window
    :return:
    """
    return click(window, x, y, MOUSE_RIGHT)


def scroll_down(window, x, y, repeat=1):
    """
    Send a 'click' with the downward mouse wheel.

    :param window: a reference to a window
    :param x: distance in pixels across a window
    :param y: distanc ein pixels down a window
    :param repeat: number of times to send the event
    :return:
    """
    mouse_move(window, x, y)
    for _ in range(repeat):
        click(window, x, y, code=MOUSE_SCROLL_DOWN)
    return repeat


def scroll_up(window, x, y, repeat=1):
    """
    Send a 'click' with the upward mouse wheel.

    :param window: a reference to a window
    :param x: distance in pixels across a window
    :param y: distanc ein pixels down a window
    :param repeat: number of times to send the event
    :return:
    """
    mouse_move(window, x, y)
    for _ in range(repeat):
        click(window, x, y, code=MOUSE_SCROLL_UP)
    return repeat


#
#   key functions
#

def get_key_code(character):
    """
    Given a character (string), convert the value into one that can be used in events.

    :param c: a character (string)
    :return: a key code (int)
    """
    # future use: (according to xlib/display)
    #   keycode_to_keysym(keycode, index)
    #   index: 0 == unshifted, 1 == shifted, 2 == alt, 3==shift+alt

    # some convenient conversions
    if character == 'Ctrl':
        character = 'Control'
    elif character == 'Enter':
        character = 'Return'

    sym = string_to_keysym(character)
    if sym == 0:
        raise Exception('NoSymbol found for character: {}'.format(character))

    code = DISPLAY.keysym_to_keycode(sym)

    return code


def key_press(window, keycode, modifiers=0):
    """
    Send a KeyPress event to a window.

    :param window: a reference to a window
    :param keycode: the keycode to send to the window
    :param modifiers:
    :return: None
    """
    send_event(
        window=window,
        event_class=event.KeyPress,
        event_type=X.KeyPress,
        keycode=keycode,
        modifiers=modifiers
    )


def key_release(window, keycode, modifiers=0):
    """
    Send a KeyRelease event to a window.

    :param window: a reference to a window
    :param keycode: the keycode to send to the window
    :param modifiers:
    :return: None
    """
    send_event(
        window=window,
        event_class=event.KeyRelease,
        event_type=X.KeyRelease,
        keycode=keycode,
        modifiers=modifiers
    )


def _parse_key_string(key):
    """
    Parse a given string into keycodes.

    :param key:
    :return:
    """
    if ('+' not in key) or (key == '+'):
        return [get_key_code(key)], []

    # primaries was designed this way so it could hypothetically accept
    # something like 'shift+j+l', that would hold shift and then
    # repeat [j, l] the specified number of times
    primaries, mods = [], []
    for part in key.split('+'):
        if part in ('alt', 'control', 'shift'):
            mods.append(get_key_code('{}_L'.format(part.capitalize())))
        else:
            primaries.append(get_key_code(part))

    return primaries, mods


def send_key(window, key, repeat=1, modifiers=0):
    """
    Send a key to a window.

    :param window: a reference to a window
    :param key: the key to be parsed
    :param repeat: number of times to send the non-special characters
    :param modifiers:
    :return: None
    """
    primaries, mods = _parse_key_string(key)

    # hold down modifiers
    for keycode in mods:
        key_press(window, keycode, modifiers)
        sleep(KEY_EVENT_INTERVAL)

    # while modifiers are down, press the primaries the number of repeat times
    for _ in range(repeat):
        for keycode in primaries:
            key_press(window, keycode, modifiers)
            sleep(KEY_EVENT_INTERVAL)
            key_release(window, keycode, modifiers)
            sleep(KEY_EVENT_INTERVAL)

    # release the modifiers
    for keycode in reversed(mods):
        key_release(window, keycode, modifiers)
        sleep(KEY_EVENT_INTERVAL)


def send_keys(window, keys):
    """
    Send keys to a window.

    :param window: a reference to a window
    :param keys: the strings to be sent to send_key
    :return: the length of the keys sent
    """
    for key in keys:
        send_key(window, key)

    # return something that could be of use
    return len(keys)


#
#   x image functions
#

def get_image(window, x, y, width, height):
    """
    Obtain a python Image object from a window.

    :param window: a reference to a window
    :param x: the left-most pixel
    :param y: the top-most pixel
    :param width: the width of the requested image
    :param height: the height of the requested image
    :return: an RGB image from the window
    """
    # image formats: X.XYPixmap, X.ZPixmap
    pixmap = window.get_image(
        x, y, width, height, X.ZPixmap, 0xffffffff
    )
    return Image.frombytes("RGB", (width, height), pixmap.data, "raw", "BGRX")


def get_screenshot(window):
    """
    Obtain an entire image of the given window.

    :param window: a reference to a window
    :return: an entire image of the window
    """
    geo = window.get_geometry()
    return get_image(window, 0, 0, geo.width, geo.height)


#
#   other
#

# obtain the coordinates of the pointer
def get_pointer_coordinates():
    """
    Obtain the current pointer coordinates.

    * note: this is an ugly function that should not be called, realistically

    :return: the coordinates of the pointer
    """
    return getattr(DISPLAY.screen().root.query_pointer(), '_data')


# ugly hacked code from nullege
def get_window_pid(window):
    """
    Obtain the process id of a given window.

    * note: ugly hacked code from nullege

    :param window: a reference to a window
    :return: the pid of the window
    """
    atom = InternAtom(
        display=window.display,
        name="_NET_WM_PID",
        only_if_exists=1
    )
    pid = window.get_property(atom.atom, X.AnyPropertyType, 0, 10)
    return int(pid.value.tolist()[0])
