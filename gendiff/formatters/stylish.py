"""Json-like format with - for deleted elements and + for added."""

from gendiff.formatters.format_utilities import converted, sort
from gendiff.gendiff_engine import ADDED, KEPT, NESTED, REMOVED

LEVEL_TAB = '    '
DICT_TEMPLATE = '{0}{1}: {2}\n'
RECURSION_TEMPLATE = '{0}    {1}: '
KEEPING = '{0}    {1}: {2}\n'
REMOVAL = '{0}  - {1}: {2}\n'
ADDING = '{0}  + {1}: {2}\n'


def format_dict(element, level):
    """Check wheteher an element of a diff is dict and format it.

    Args:
        element: the element of a diff to be checked.
        level: current level of nesting.

    Returns:
        Formatted dict as a string.
    """
    level += 1

    def walk(element, difference, level):
        for key in sorted(element.keys()):
            if isinstance(element[key], dict):
                level += 1
                difference += DICT_TEMPLATE.format(
                    (LEVEL_TAB * level), key, walk(element[key], '{\n', level),
                )
                level -= 1
            else:
                level += 1
                difference += DICT_TEMPLATE.format(
                    (LEVEL_TAB * level), key, element[key],
                )
                level -= 1
        return difference + '{0}}}'.format((LEVEL_TAB * level))
    if isinstance(element, dict):
        return walk(element, '{\n', level)
    return converted(element)


def stylished(diff):
    """Convert diff to a CLI notion.

    Args:
        diff: generated difference between two files.

    Returns:
        Difference formated into string with necessary syntax.
    """
    def walk(sequence, difference, level):
        for node in sequence:
            key, status, value = node
            if status == NESTED:
                difference += RECURSION_TEMPLATE.format(
                    (LEVEL_TAB * level), key,
                )
                level += 1
                difference += '{0}\n'.format(
                    walk(value, '{\n', level),
                )
                level -= 1
            elif status == KEPT:
                difference += KEEPING.format(
                    (LEVEL_TAB * level), key, format_dict(value, level),
                )
            elif status is REMOVED:
                difference += REMOVAL.format(
                    (LEVEL_TAB * level), key, format_dict(value, level),
                )
            elif status is ADDED:
                difference += ADDING.format(
                    (LEVEL_TAB * level), key, format_dict(value, level),
                )
            else:
                old, new = value
                difference += REMOVAL.format(
                    (LEVEL_TAB * level), key, format_dict(old, level),
                )
                difference += ADDING.format(
                    (LEVEL_TAB * level), key, format_dict(new, level),
                )
        return difference + '{0}}}'.format((LEVEL_TAB * level))
    return walk(sort(diff), '{\n', 0)
