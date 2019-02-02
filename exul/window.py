"""A file for holding the Window class, which wraps utility methods."""


from .utilities import MOUSE_LEFT, click, click_left, click_right, get_image, get_screenshot, \
    get_window_pid, mouse_down, mouse_move, mouse_up, scroll_down, scroll_up, send_key, send_keys


class Window(object):  # pylint: disable=useless-object-inheritance; trying for py2 and py3 compatability
    """A class for passing around a window reference to common utility methods."""

    def __init__(self, window):
        """Save the reference to the window."""
        self._window = window

        # determine information about the window class
        wm_class = window.get_wm_class()
        if wm_class is None:
            self.class_type, self.class_name = None, None
        else:
            self.class_type, self.class_name = wm_class

    def __str__(self):
        """Create a string-version of the window."""
        geos = self.get_geometry()
        return (
            '<Window id="{0}" name="{1}" class_type="{2}" class_name="{3}" '
            'x={4} y={5} width={6} height={7}>'
        ).format(
            self.id, self.name, self.class_type, self.class_name,
            geos.x, geos.y, geos.width, geos.height
        )

    #
    #   class properties
    #

    @property
    def children(self):
        """Return the children of this window."""
        return self._window.query_tree().children

    @property
    def id(self):
        """Return the window ID."""
        return self._window.id

    @property
    def name(self):
        """Return the window name."""
        return self._window.get_wm_name()

    #
    #   class methods
    #

    def click(self, x, y, code=MOUSE_LEFT):
        """Click a mouse button."""
        return click(self._window, x, y, code)

    def click_left(self, x, y):
        """Click the left mouse button."""
        return click_left(self._window, x, y)

    def click_right(self, x, y):
        """Click the right mouse button."""
        return click_right(self._window, x, y)

    def get_geometry(self):
        """Obtain the window geometry."""
        return self._window.get_geometry()

    def get_image(self, x, y, width, height):
        """Get a part of the window as an image."""
        return get_image(self._window, x, y, width, height)

    def get_pid(self):
        """Obtain the process ID associated with the window."""
        return get_window_pid(self._window)

    def get_screenshot(self):
        """Get the entire window as an image."""
        return get_screenshot(self._window)

    def mouse_down(self, x, y, code):
        """Press a mouse button down."""
        return mouse_down(self._window, x, y, code)

    def mouse_move(self, x, y):
        """Move the mouse in a window."""
        return mouse_move(self._window, x, y)

    def mouse_up(self, x, y, code):
        """Release a pressed mouse button."""
        return mouse_up(self._window, x, y, code)

    def scroll_down(self, x, y, repeat=1):
        """Send the scroll down mouse event."""
        return scroll_down(self._window, x, y, repeat)

    def scroll_up(self, x, y, repeat=1):
        """Send the scroll up mouse event."""
        return scroll_up(self._window, x, y, repeat)

    def send_key(self, key, repeat=1, modifiers=0):
        """Send a key to a window."""
        return send_key(self._window, key, repeat, modifiers)

    def send_keys(self, keys):
        """Send keys to a window."""
        return send_keys(self._window, keys)
