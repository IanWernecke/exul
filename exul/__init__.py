"""This library handles various function calls to an X window server."""


from .utilities import DISPLAY
from .window import Window


def find_window(window_id=None, window_name=None, class_type=None, class_name=None):
    """
    Find a window by a piece(s) of given information.

    :param window_id:
    :param window_name:
    :param class_type:
    :param class_name:
    :return: a reference to a window
    """
    # ensure at least one value is present
    if [window_id, window_name, class_type, class_name].count(None) == 4:
        raise Exception('Something must be given to find.')

    # append all given values to a list for comparison in the loop below
    match_attributes = []
    if window_id is not None:
        match_attributes.append((window_id, 'id'))
    if window_name is not None:
        match_attributes.append((window_name, 'name'))
    if class_type is not None:
        match_attributes.append((class_type, 'class_type'))
    if class_name is not None:
        match_attributes.append((class_name, 'class_name'))

    # search for a window that matches all given attributes
    for window, _ in windows():

        # iterate each of the given values and attempt to disqualify the window
        for match_value, attribute_name in match_attributes:
            if match_value != getattr(window, attribute_name):
                break
        else:
            return window

    return None


def windows():
    """
    Walk each available window running on the system, depth first.
    :yield: ((window), (int)) yield a window object and the level at which the window resides
    """
    # hold the window and the level as each item in the list
    all_windows = [(Window(DISPLAY.screen().root), 0)]
    while all_windows:

        window, level = all_windows.pop(0)
        yield window, level

        # insert each child in reverse so the normal order is preserved
        # for child in window.query_tree().children[::-1]:
        for child in window.children[::-1]:
            all_windows.insert(0, (Window(child), level + 1))
