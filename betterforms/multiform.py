from itertools import chain
from operator import add

try:
    from collections import OrderedDict
except ImportError:  # Python 2.6, Django < 1.7
    from django.utils.datastructures import SortedDict as OrderedDict  # NOQA

from django.forms import BaseForm

try:
    from django.forms.utils import ErrorDict, ErrorList
except ImportError:  # Django < 1.7
    from django.forms.util import ErrorDict, ErrorList  # NOQA

from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.six.moves import reduce


@python_2_unicode_compatible
class WhitelistedBaseForm(object):
    def __init__(self, auto_id='id_%s', prefix=None, error_class=ErrorList,
                 label_suffix=':', *args, **kwargs):
        self.auto_id = auto_id
        self.prefix = prefix
        self.error_class = error_class
        self.label_suffix = label_suffix

    def __str__(self):
        return self.as_table()

    if '__repr__' in BaseForm.__dict__:
        __repr__ = BaseForm.__dict__['__repr__']
    __iter__ = BaseForm.__dict__['__iter__']
    add_prefix = BaseForm.__dict__['add_prefix']
    add_initial_prefix = BaseForm.__dict__['add_initial_prefix']
    _html_output = BaseForm.__dict__['_html_output']
    as_table = BaseForm.__dict__['as_table']
    as_ul = BaseForm.__dict__['as_ul']
    as_p = BaseForm.__dict__['as_p']


class MultiForm(WhitelistedBaseForm):
    """
    A container that allows you to treat multiple forms as one form.  This is
    great for using more than one form on a page that share the same submit
    button.  MultiForm imitates the Form API so that it is invisible to anybody
    else that you are using a MultiForm.
    """
    form_classes = {}
    field_order = None

    def __init__(self, data=None, files=None, *args, **kwargs):
        # Some things, such as the WizardView expect these to exist.
        self.data, self.files = data, files
        kwargs.update(
            data=data,
            files=files,
        )

        super(MultiForm, self).__init__(*args, **kwargs)

        self.initials = kwargs.pop('initial', None)
        if self.initials is None:
            self.initials = {}
        self.forms = OrderedDict()

        for key, form_class in self.form_classes.items():
            fargs, fkwargs = self.get_form_args_kwargs(key, args, kwargs)
            self.forms[key] = form_class(*fargs, **fkwargs)

        self.fields = OrderedDict()
        for key, form in self.forms.items():
            for name, field in form.fields.items():
                full_name = '__{0}__{1}'.format(key, name)
                self.fields[full_name] = field

        self.order_fields(self.field_order)

    def order_fields(self, field_order):
        if field_order is None:
            return
        fields = OrderedDict()

        def add_field(key, name):
            full_name = '__{0}__{1}'.format(key, name)
            try:
                fields[full_name] = self.fields.pop(full_name)
            except KeyError:  # ignore unknown fields
                print("unknown field", full_name)

        for key, name in field_order:
            if name == '__all__':
                for name in self[key].fields:
                    add_field(key, name)
            else:
                add_field(key, name)
        fields.update(self.fields)  # add remaining fields in original order
        self.fields = fields

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

    def __getitem__(self, key):
        if key.startswith('__'):
            key, name = key[2:].split('__', 1)
            return self.forms[key][name]
        else:
            return self.forms[key]

    @property
    def is_bound(self):
        return any(form.is_bound for form in self.forms.values())

    def is_valid(self):
        return all(form.is_valid() for form in self.forms.values())

    def non_field_errors(self):
        return ErrorList(chain.from_iterable(
            form.non_field_errors() for form in self.forms.values()
        ))

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
