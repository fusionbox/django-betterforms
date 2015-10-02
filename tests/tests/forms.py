try:
    from collections import OrderedDict
except ImportError:  # Python 2.6, Django < 1.7
    from django.utils.datastructures import SortedDict as OrderedDict  # NOQA

from django import forms
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


class BadgeMultiForm(MultiModelForm):
    form_classes = {
        'badge1': BadgeForm,
        'badge2': BadgeForm,
    }


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


class OptionalFileForm(forms.Form):
    myfile = forms.FileField(required=False)


class Step1Form(MultiModelForm):
    # This is required because the WizardView introspects it, but we don't have
    # a way of determining this dynamically, so just set it to an empty
    # dictionary.
    base_fields = {}

    form_classes = {
        'myfile': OptionalFileForm,
        'profile': ProfileForm,
    }


class Step2Form(forms.Form):
    confirm = forms.BooleanField(required=True)


class RaisesErrorCustomCleanMultiform(UserProfileMultiForm):
    def clean(self):
        cleaned_data = super(UserProfileMultiForm, self).clean()
        raise ValidationError('It broke')
        return cleaned_data


class ModifiesDataCustomCleanMultiform(UserProfileMultiForm):
    def clean(self):
        cleaned_data = super(UserProfileMultiForm, self).clean()
        cleaned_data['profile']['display_name'] = "cleaned name"
        return cleaned_data
