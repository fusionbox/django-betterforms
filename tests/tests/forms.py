try:
    from collections import OrderedDict
except ImportError:  # Python 2.6, Django < 1.7
    from django.utils.datastructures import SortedDict as OrderedDict  # NOQA

from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.contrib.admin import widgets as admin_widgets
from django.core.exceptions import ValidationError

from betterforms.multiform import MultiForm, MultiModelForm

from .models import User, Profile, Badge, Author


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name',)


class ProfileForm(forms.ModelForm):
    name = forms.CharField(label='Namespace Clash')

    class Meta:
        model = Profile
        fields = ('name', 'display_name',)


class UserProfileMultiForm(MultiModelForm):
    form_classes = OrderedDict((
        ('user', UserForm),
        ('profile', ProfileForm),
    ))


class RaisesErrorForm(forms.Form):
    name = forms.CharField()
    hidden = forms.CharField(widget=forms.HiddenInput)

    class Media:
        js = ('test.js',)

    def clean(self):
        raise ValidationError('It broke')


class ErrorMultiForm(MultiForm):
    form_classes = {
        'errors': RaisesErrorForm,
        'errors2': RaisesErrorForm,
    }


class FileForm(forms.Form):
    # we use this widget to test the media property
    date = forms.DateTimeField(widget=admin_widgets.AdminSplitDateTime)
    image = forms.ImageField()
    hidden = forms.CharField(widget=forms.HiddenInput)


class NeedsFileField(MultiForm):
    form_classes = OrderedDict((
        ('file', FileForm),
        ('errors', RaisesErrorForm),
    ))


class BadgeForm(forms.ModelForm):

    class Meta:
        model = Badge
        fields = ('name', 'color',)

    # self.label_suffix has to be declared with form instantiation per Django 1.6
    def __init__(self, *args, **kwargs):
        super(BadgeForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''


class BadgeMultiForm(MultiModelForm):
    form_classes = {
        'badge1': BadgeForm,
        'badge2': BadgeForm,
    }

BadgeFormSet = formset_factory(BadgeForm, extra=2)

BadgeDeleteFormSet = formset_factory(BadgeForm, can_delete=True, extra=2)

BadgeOrderFormSet = formset_factory(BadgeForm, can_order=True, extra=2)

try:
    BadgeModelFormSet = modelformset_factory(Badge, form=BadgeForm, extra=2)
except PendingDeprecationWarning:
    BadgeModelFormSet = modelformset_factory(Badge, form=BadgeForm, fields='__all__', extra=2)


class NonModelForm(forms.Form):
    field1 = forms.CharField()


class MixedForm(MultiModelForm):
    form_classes = {
        'badge': BadgeForm,
        'non_model': NonModelForm,
    }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('name', 'books',)


class ManyToManyMultiForm(MultiModelForm):
    form_classes = {
        'badge': BadgeForm,
        'author': AuthorForm,
    }
