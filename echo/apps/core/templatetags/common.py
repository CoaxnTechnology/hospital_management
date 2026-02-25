from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.simple_tag
def is_in_models_list(*args):
    if args[1] is None:
        return False
    for item in args[1]:
        #print('Item', item)
        if isinstance(item, int):
            return False
        if item.id == args[0]:
            return True
    return False


@register.filter
def params_to_url(get_params):
    ret = "?"
    for key, value in get_params:
        if len(ret) == 1:
            ret = ret + f"{key}={value}"
        else:
            ret = ret + f"&{key}={value}"
    return ret


@register.filter
def money_format(number, decimal_places=3, decimal=','):
    result = intcomma(number)
    result += decimal if decimal not in result else ''
    while len(result.split(decimal)[1]) != decimal_places:
        result += '0'
    return result


@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    #value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    value = value[:limit]

    # Break into words and remove the last
    words = value.split(' ')[:-1]

    # Join the words and return
    return ' '.join(words) + '...'