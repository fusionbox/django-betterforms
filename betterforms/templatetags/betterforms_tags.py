from django import forms
from django import template

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(field):
    """
    Boolean filter for form fields to determine if a field is using a checkbox
    widget.
    """
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def label_tag(self, contents=None, attrs=None, label_suffix=None):
    """
    Backported version of the Django 1.8 behaviour of field.label_tag() -
    modified to act as template filter
    """
    from django.utils.html import format_html
    from django.utils.html import conditional_escape
    from django.forms.utils import flatatt
    from django.utils.safestring import mark_safe
    from django.utils.translation import ugettext as _

    contents = contents or self.label
    if label_suffix is None:
        label_suffix = (self.field.label_suffix if getattr(self.field, 'label_suffix', None) is not None
                        else self.form.label_suffix)
    # Only add the suffix if the label does not end in punctuation.
    # Translators: If found as last label character, these punctuation
    # characters will prevent the default label_suffix to be appended to the label
    if label_suffix and contents and contents[-1] not in _(':?.!'):
        contents = format_html('{}{}', contents, label_suffix)
    widget = self.field.widget
    id_ = widget.attrs.get('id') or self.auto_id
    if id_:
        id_for_label = widget.id_for_label(id_)
        if id_for_label:
            attrs = dict(attrs or {}, **{'for': id_for_label})
        if self.field.required and hasattr(self.form, 'required_css_class'):
            attrs = attrs or {}
            if 'class' in attrs:
                attrs['class'] += ' ' + self.form.required_css_class
            else:
                attrs['class'] = self.form.required_css_class
        attrs = flatatt(attrs) if attrs else ''
        contents = format_html('<label{}>{}</label>', attrs, contents)
    else:
        contents = conditional_escape(contents)
    return mark_safe(contents)
