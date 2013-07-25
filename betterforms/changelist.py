import copy
import urllib

from django import forms
from django.forms.forms import pretty_name
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.datastructures import SortedDict

from .forms import BetterForm


def construct_querystring(data, **kwargs):
    params = copy.copy(data)
    params.update(kwargs)
    return urllib.urlencode(params)


class IterDict(SortedDict):
    """
    Extension of djangos built in sorted dictionary class which iterates
    through the values rather than keys.
    """
    def __iter__(self):
        for key in super(IterDict, self).__iter__():
            yield self[key]


class BaseChangeListForm(BetterForm):
    """
    Base class for all ``ChangeListForms``.
    """
    def __init__(self, *args, **kwargs):
        """
        Takes an option named argument ``queryset`` as the base queryset used in
        the ``get_queryset`` method.
        """
        try:
            self.base_queryset = kwargs.pop('queryset', None)
            if self.base_queryset is None:
                self.base_queryset = self.model.objects.all()
        except AttributeError:
            raise AttributeError('`ChangeListForm`s must be instantiated with a\
                                 queryset, or have a `model` attribute set on\
                                 them')
        super(BaseChangeListForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        If the form was initialized with a queryset, this method returns that
        queryset.  Otherwise it returns ``Model.objects.all()`` for whatever
        model was defined for the form.
        """
        return self.base_queryset

    def full_clean(self, *args, **kwargs):
        super(BaseChangeListForm, self).full_clean()
        if self.is_valid():
            self.queryset = self.get_queryset()


class SearchForm(BaseChangeListForm):
    SEARCH_FIELDS = tuple()
    CASE_SENSITIVE = False
    q = forms.CharField(label="Search", required=False)

    def get_queryset(self):
        """
        Constructs an '__contains' or '__icontains' filter across all of the
        fields listed in ``SEARCH_FIELDS``.
        """
        qs = super(SearchForm, self).get_queryset()

        # Do Searching
        q = self.cleaned_data.get('q', '').strip()
        if q:
            args = []
            for field in self.SEARCH_FIELDS:
                if self.CASE_SENSITIVE:
                    kwarg = {field + '__contains': q}
                else:
                    kwarg = {field + '__icontains': q}
                args.append(Q(**kwarg))
            if len(args) > 1:
                qs = qs.filter(reduce(lambda x, y: x | y, args))
            elif len(args) == 1:
                qs = qs.filter(args[0])

        return qs


class ThingSet(object):
    ThingClass = None

    def __init__(self, form, headers):
        if self.ThingClass is None:
            raise AttributeError('ThingSet must have a ThingClass attribute')
        self.form = form
        self.headers = SortedDict()
        for header in headers:
            self.headers[header.name] = header

    def __iter__(self):
        for header in self.headers.values():
            yield self.ThingClass(self.form, header)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.ThingClass(self.form, self.headers.values()[key])
        else:
            return self.ThingClass(self.form, self.headers[key])


class Header(object):
    def __init__(self, name, label=None, column_name=False, is_sortable=True):
        self.name = name
        self.label = label or pretty_name(name)
        self.column_name = column_name or name
        self.is_sortable = is_sortable


class BoundHeader(object):
    def __init__(self, form, header):
        self.name = header.name
        self.label = header.label
        self.column_name = header.column_name
        self.is_sortable = header.is_sortable
        self.form = form
        self.sorts = getattr(form, 'cleaned_data', {}).get('sorts', [])
        self.header = header
        self.param = "{0}-sorts".format(form.prefix or '').strip('-')

    @property
    def index(self):
        return self.form.HEADERS.index(self.header)

    @property
    def sort_index(self):
        return self.index + 1

    @property
    def is_ascending(self):
        return self.is_active and self.sort_index in self.sorts

    @property
    def is_descending(self):
        return self.is_active and self.sort_index not in self.sorts

    @property
    def css_classes(self):
        classes = []
        if self.is_active:
            classes.append('active')
            if self.sort_index in self.sorts:
                classes.append('ascending')
            else:
                classes.append('descending')
        return ' '.join(classes)

    def get_sorts_with_header(self):
        if not self.sorts:
            return [self.sort_index]
        elif abs(self.sorts[0]) == self.sort_index:
            return [-1 * self.sorts[0]] + self.sorts[1:]
        else:
            return [self.sort_index] + filter(lambda x: x != self.sort_index, self.sorts)

    @property
    def priority(self):
        if self.is_active:
            return map(abs, self.sorts).index(self.sort_index) + 1

    @property
    def is_active(self):
        return self.sort_index in map(abs, self.sorts)

    @property
    def querystring(self):
        return construct_querystring(self.form.data, **{self.param: '.'.join(map(str, self.get_sorts_with_header()))})

    @property
    def singular_queryset(self):
        return construct_querystring(self.form.data, **{self.param: str(self.sort_index)})

    @property
    def remove_queryset(self):
        return construct_querystring(self.form.data, **{self.param: '.'.join(map(str, self.get_sorts_with_header()[1:]))})


class HeaderSet(ThingSet):
    ThingClass = BoundHeader


class SortForm(BaseChangeListForm):
    Header = Header  # Easy access when defining SortForms
    error_messages = {
        'unknown_header': 'Invalid sort parameter',
        'unsortable_header': 'Invalid sort parameter',
    }
    HEADERS = tuple()
    sorts = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(SortForm, self).__init__(*args, **kwargs)
        if not len(set(h.name for h in self.HEADERS)) == len(self.HEADERS):
            raise AttributeError('Duplicate `name` in HEADERS')
        self.headers = HeaderSet(self, self.HEADERS)

    def clean_sorts(self):
        cleaned_data = self.cleaned_data
        sorts = filter(bool, cleaned_data.get('sorts', '').split('.'))
        if not sorts:
            return []
        # Ensure that the sort parameter does not contain non-numeric sort indexes
        if not all([sort.strip('-').isdigit() for sort in sorts]):
            raise ValidationError(self.error_messages['unknown_header'])
        sorts = [int(sort) for sort in sorts]
        # Ensure that all of our sort parameters are in range of our header values
        if any([abs(sort) > len(self.HEADERS) for sort in sorts]):
            raise ValidationError(self.error_messages['unknown_header'])
        # Ensure not un-sortable fields are being sorted by
        if not all(self.HEADERS[abs(i) - 1].is_sortable for i in sorts):
            raise ValidationError(self.error_messages['unsortable_header'])

        return sorts

    def get_order_by(self):
        # Do Sorting
        sorts = self.cleaned_data.get('sorts', [])
        order_by = []
        for sort in sorts:
            param = self.headers[abs(sort) - 1].column_name
            if sort < 0:
                param = '-' + param
            order_by.append(param)
        return order_by

    def get_queryset(self):
        """
        Returns an ordered queryset, sorted based on the values submitted in
        the sort parameter.
        """
        qs = super(SortForm, self).get_queryset()

        order_by = self.get_order_by()
        if order_by:
            qs = qs.order_by(*order_by)

        return qs
