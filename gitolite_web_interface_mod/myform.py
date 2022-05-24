"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

# pylint: disable=missing-docstring


def _generate_form_checkbox(all_users, user, key):
    content = ''
    content += '<fieldset>'
    for otheruser in all_users:
        if user == otheruser:
            content += '<input type="checkbox" name="%s" value="%s" id="%s" checked>' % (
                key, otheruser, otheruser)
        else:
            content += '<input type="checkbox" name="%s" value="%s" id="%s">' % (
                key, otheruser, otheruser)
        content += '<label for="%s">%s</label></br>' % (otheruser, otheruser)
    content += '</fieldset>'
    return content


def _generate_form_select(all_users, user, key):
    content = ''
    content += '<select name="%s" size="5" multiple>' % key
    for otheruser in all_users:
        if user == otheruser:
            content += '<option selected>%s</option>' % (otheruser)
        else:
            content += '<option>%s</option>' % (otheruser)
    content += '</select>'
    return content


def generate_form_select_list(creategroup_format, all_users, user, key):
    if (((creategroup_format == 'auto') and (len(all_users) <= 5)) or
            (creategroup_format == 'checkbox')):
        return _generate_form_checkbox(all_users, user, key)
    # else:
    return _generate_form_select(all_users, user, key)


def extract_set_from_form(form, key, default=tuple()):
    data = set(default)
    if key in form:
        if isinstance(form[key], list):
            for item in form[key]:
                data.add(item.value)
        else:
            data.add(form[key].value)
    data = list(data)
    data.sort()
    return data
