import collections

from django import forms
from django.forms.util import ErrorList, ErrorDict
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict


class CSSClassMixin(object):
    """
    Sane defaults for error and css classes.
    """
    error_css_class = 'error'
    required_css_class = 'required'


class NonBraindamagedErrorMixin(object):
    """
    Form mixin for easier field based error messages.
    """
    def field_error(self, name, error):
        self._errors = self._errors or ErrorDict()
        self._errors.setdefault(name, ErrorList())
        self._errors[name].append(error)


def process_fieldset_row(fields, fieldset_class, base_name):
    for index, row in enumerate(fields):
        if not isinstance(row, (basestring, Fieldset)):
            if len(row) == 2 and isinstance(row[0], basestring) and isinstance(row[1], dict):
                row = fieldset_class(row[0], **row[1])
            else:
                row = fieldset_class("{0}_{1}".format(base_name, index), fields=row)
        yield row


def flatten(elements):
    """
    Flattens a mixed list of strings and iterables of strings into a single
    iterable of strings.
    """
    for element in elements:
        if isinstance(element, collections.Iterable) and not isinstance(element, basestring):
            for sub_element in flatten(element):
                yield sub_element
        else:
            yield element

flatten_to_tuple = lambda x: tuple(flatten(x))


class Fieldset(CSSClassMixin):
    FIELDSET_CSS_CLASS = 'formFieldset'
    css_classes = None
    template_name = None

    def __init__(self, name, fields=[], **kwargs):
        self.name = name
        self.base_fields = tuple(process_fieldset_row(fields, type(self), name))

        # Check for duplicate names.
        names = [str(thing) for thing in self.base_fields]
        duplicates = [x for x, y in collections.Counter(names).items() if y > 1]
        if duplicates:
            raise AttributeError('Name Conflict in fieldset `{0}`.  The name(s) `{1}` appear multiple times.'.format(self.name, duplicates))
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __iter__(self):
        return iter(self.base_fields)

    def __nonzero__(self):
        return bool(self.base_fields)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name

    @property
    def fields(self):
        return flatten_to_tuple(self)


class BoundFieldset(object):
    is_fieldset = True

    def __init__(self, form, fieldset, name):
        self.form = form
        self.name = name
        self.fieldset = fieldset
        self.rows = SortedDict()
        for row in fieldset:
            self.rows[unicode(row)] = row

    def __getitem__(self, key):
        """
        >>> fieldset[1]
        # returns the item at index-1 in the fieldset
        >>> fieldset['name']
        # returns the item in the fieldset under the key 'name'
        """
        if isinstance(key, int) and not key in self.rows:
            return self[self.rows.keyOrder[key]]
        value = self.rows[key]
        if isinstance(value, basestring):
            return self.form[value]
        else:
            return type(self)(self.form, value, key)

    def __str__(self):
        env = {
            'fieldset': self,
            'form': self.form,
            'fieldset_template_name': 'partials/fieldset_as_divs.html',
        }
        # TODO: don't hardcode the default template name.
        return render_to_string(self.template_name or 'partials/fieldset_as_divs.html', env)

    def __iter__(self):
        for name in self.rows.keys():
            yield self[name]

    @property
    def template_name(self):
        return self.fieldset.template_name

    @property
    def errors(self):
        return self.form.errors.get(self.name, self.form.error_class())

    @property
    def css_classes(self):
        css_classes = set((self.fieldset.FIELDSET_CSS_CLASS, self.name))
        css_classes.update(self.fieldset.css_classes or [])
        if self.errors:
            css_classes.add(self.fieldset.error_css_class)
        return ' '.join(css_classes)


class FieldsetMixin(NonBraindamagedErrorMixin):
    template_name = None
    fieldset_class = Fieldset
    bound_fieldset_class = BoundFieldset
    base_fieldsets = tuple()

    @property
    def fieldsets(self):
        return self.bound_fieldset_class(self, self.base_fieldsets, self.base_fieldsets.name)

    def __getitem__(self, key):
        try:
            return super(FieldsetMixin, self).__getitem__(key)
        except KeyError:
            return self.fieldsets[key]

    def __iter__(self):
        return iter(self.fieldsets)

    # These methods need to be implemented to render the fieldsets and fields
    # in a similar structure as `BaseForm`
    def __str__(self):
        return self.as_table()

    def as_table(self):
        raise NotImplementedError('To be implemented')

    def as_ul(self):
        raise NotImplementedError('To be implemented')

    def as_p(self):
        raise NotImplementedError('To be implemented')



def get_fieldsets(bases, attrs):
    try:
        return attrs['Meta'].fieldsets
    except (KeyError, AttributeError):
        for base in bases:
            fieldsets = getattr(base, 'base_fieldsets', None)
            if fieldsets is not None:
                return fieldsets or []
    return []


def get_fieldset_class(bases, attrs):
    if 'fieldset_class' in attrs:
        return attrs['fieldset_class']
    else:
        for base in bases:
            try:
                return base.fieldset_class
            except AttributeError:
                continue
        return Fieldset


class BetterModelFormMetaclass(forms.models.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        base_fieldsets = get_fieldsets(bases, attrs)
        if base_fieldsets:
            FieldsetClass = get_fieldset_class(bases, attrs)
            base_fieldsets = FieldsetClass('__base_fieldset__', fields=base_fieldsets)
            attrs['base_fieldsets'] = base_fieldsets
            Meta = attrs.get('Meta')
            if Meta and Meta.__dict__.get('fields') is None and Meta.__dict__.get('exclude') is None:
                attrs['Meta'].fields = flatten_to_tuple(base_fieldsets)
        attrs['base_fieldsets'] = base_fieldsets
        return super(BetterModelFormMetaclass, cls).__new__(cls, name, bases, attrs)


class BetterModelForm(FieldsetMixin, CSSClassMixin, forms.ModelForm):
    __metaclass__ = BetterModelFormMetaclass
    pass


class BetterFormMetaClass(forms.forms.DeclarativeFieldsMetaclass):
    def __new__(cls, name, bases, attrs):
        FieldsetClass = get_fieldset_class(bases, attrs)
        base_fieldsets = get_fieldsets(bases, attrs)
        attrs['base_fieldsets'] = FieldsetClass('__base_fieldset__', fields=base_fieldsets)
        return super(BetterFormMetaClass, cls).__new__(cls, name, bases, attrs)


class BetterForm(FieldsetMixin, CSSClassMixin, forms.forms.BaseForm):
    """
    A 'Better' base Form class.
    """
    __metaclass__ = BetterFormMetaClass
    pass
