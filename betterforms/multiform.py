from itertools import chain
from operator import add

try:
    from collections import OrderedDict
except ImportError:  # Python 2.6, Django < 1.7
    from django.utils.datastructures import SortedDict as OrderedDict  # NOQA

try:
    from django.forms.utils import ErrorDict, ErrorList
except ImportError:  # Django < 1.7
    from django.forms.util import ErrorDict, ErrorList  # NOQA

try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:  # Django < 1.4
    from betterforms.compat import python_2_unicode_compatible


@python_2_unicode_compatible
class MultiForm(object):
    """
    A container that allows you to treat multiple forms as one form.  This is
    great for using more than one form on a page that share the same submit
    button.  MultiForm imitates the Form API so that it is invisible to anybody
    else that you are using a MultiForm.
    """
    form_classes = {}

    def __init__(self, *args, **kwargs):
        self.initials = kwargs.pop('initial', {})
        self.forms = OrderedDict()

        for key, form_class in self.form_classes.items():
            fargs, fkwargs = self.get_form_args_kwargs(key, args, kwargs)
            self.forms[key] = form_class(*fargs, **fkwargs)

    def get_form_args_kwargs(self, key, args, kwargs):
        """
        Returns the args and kwargs for initializing one of our form children.
        """
        fkwargs = kwargs.copy()
        prefix = kwargs.get('prefix')
        if prefix is None:
            prefix = key
        else:
            prefix = '{0}__{1}'.format(key, prefix)
        fkwargs.update(
            initial=self.initials.get(key),
            prefix=prefix,
        )
        return args, fkwargs

    def __str__(self):
        return self.as_table()

    def __getitem__(self, key):
        return self.forms[key]

    def __iter__(self):
        # TODO: Should the order of the fields be controllable from here?
        return chain.from_iterable(self.forms.values())

    @property
    def is_bound(self):
        return any(form.is_bound for form in self.forms.values())

    def is_valid(self):
        return all(form.is_valid() for form in self.forms.values())

    def non_field_errors(self):
        return ErrorList(chain.from_iterable(
            form.non_field_errors() for form in self.forms.values()
        ))

    def as_table(self):
        return ''.join(form.as_table() for form in self.forms.values())

    def as_ul(self):
        return ''.join(form.as_ul() for form in self.forms.values())

    def as_p(self):
        return ''.join(form.as_p() for form in self.forms.values())

    def is_multipart(self):
        return any(form.is_multipart() for form in self.forms.values())

    @property
    def media(self):
        return reduce(add, (form.media for form in self.forms.values()))

    def hidden_fields(self):
        # copy implementation instead of delegating in case we ever
        # want to override the field ordering.
        return [field for field in self if field.is_hidden]

    def visible_fields(self):
        return [field for field in self if not field.is_hidden]

    @property
    def cleaned_data(self):
        return OrderedDict(
            (key, form.cleaned_data)
            for key, form in self.forms.items()
        )


class MultiModelForm(MultiForm):
    """
    MultiModelForm adds ModelForm support on top of MultiForm.  That simply
    means that it includes support for the instance parameter in initialization
    and adds a save method.
    """
    def __init__(self, *args, **kwargs):
        self.instances = kwargs.pop('instance', None)
        if self.instances is None:
            self.instances = {}
        super(MultiModelForm, self).__init__(*args, **kwargs)

    def get_form_args_kwargs(self, key, args, kwargs):
        fargs, fkwargs = super(MultiModelForm, self).get_form_args_kwargs(key, args, kwargs)
        try:
            # If we only pass instance when there was one specified, we make it
            # possible to use non-ModelForms together with ModelForms.
            fkwargs['instance'] = self.instances[key]
        except KeyError:
            pass
        return fargs, fkwargs

    def save(self, commit=True):
        objects = OrderedDict(
            (key, form.save(commit))
            for key, form in self.forms.items()
        )

        if any(hasattr(form, 'save_m2m') for form in self.forms.values()):
            def save_m2m():
                for form in self.forms.values():
                    if hasattr(form, 'save_m2m'):
                        form.save_m2m()
            self.save_m2m = save_m2m

        return objects
