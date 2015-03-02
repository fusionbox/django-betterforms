MultiForm and MultiModelForm
============================

.. currentmodule:: betterforms.multiform

A container that allows you to treat multiple forms as one form.  This is great
for using more than one form on a page that share the same submit button.
:class:`MultiForm` imitates the Form API so that it is invisible to anybody
else (for example, generic views) that you are using a :class:`MultiForm`.

There are a couple of differences, though.  One lies in how you initialize the
form.  See this example::

    class UserProfileMultiForm(MultiForm):
        form_classes = {
            'user': UserForm,
            'profile': ProfileForm,
        }

    UserProfileMultiForm(initial={
        'user': {
            # User's initial data
        },
        'profile': {
            # Profile's initial data
        },
    })

The initial data argument has to be a nested dictionary so that we can
associate the right initial data with the right form class.

The other major difference is that there is no direct field access because this
could lead to namespace clashes.  You have to access the fields from their
forms.  All forms are available using the key provided in
:attr:`~MultiForm.form_classes`::

    form = UserProfileMultiForm()
    # get the Field object
    form['user'].fields['name']
    # get the BoundField object
    form['user']['name']

:class:`MultiForm`, however, does all you to iterate over all the fields of all
the forms.

.. code-block:: html

    {% for field in form %}
      {{ field }}
    {% endfor %}

If you are relying on the fields to come out in a consistent order, you should
use an OrderedDict to define the :attr:`~MultiForm.form_classes`. ::

    from collections import OrderedDict

    class UserProfileMultiForm(MultiForm):
        form_classes = OrderedDict((
            ('user', UserForm),
            ('profile', ProfileForm),
        ))


Working with ModelForms
-----------------------

MultiModelForm adds ModelForm support on top of MultiForm.  That simply means
that it includes support for the instance parameter in initialization and adds
a save method. ::

    class UserProfileMultiForm(MultiModelForm):
        form_classes = {
            'user': UserForm,
            'profile': ProfileForm,
        }

    user = User.objects.get(pk=123)
    UserProfileMultiForm(instance={
        'user': user,
        'profile': user.profile,
    })


Working with CreateView
-----------------------

It is pretty easy to use MultiModelForms with Django's
:class:`~django:django.views.generic.edit.CreateView`, usually you will have to
override the :meth:`~django:django.views.generic.edit.FormMixin.form_valid`
method to do some specific saving functionality.  For example, you could have a
signup form that created a user and a user profile object all in one::

    # forms.py
    from django import forms
    from authtools.forms import UserCreationForm
    from betterforms.multiform import MultiModelForm
    from .models import UserProfile

    class UserProfileForm(forms.ModelForm):
        class Meta:
            fields = ('favorite_color',)

    class UserCreationMultiForm(MultiModelForm):
        form_classes = {
            'user': UserCreationForm,
            'profile': UserProfileForm,
        }

    # views.py
    from django.views.generic import CreateView
    from django.core.urlresolvers import reverse_lazy
    from django.shortcuts import redirect
    from .forms import UserCreationMultiForm

    class UserSignupView(CreateView):
        form_class = UserCreationMultiForm
        success_url = reverse_lazy('home')

        def form_valid(self, form):
            # Save the user first, because the profile needs a user before it
            # can be saved.
            user = form['user'].save()
            profile = form['profile'].save(commit=False)
            profile.user = user
            profile.save()
            return redirect(self.get_success_url())

.. note::

    In this example, we used the ``UserCreationForm`` from the django-authtools
    package just for the purposes of brevity.  You could of course use any
    ModelForm that you wanted to.

Of course, we could put the save logic in the ``UserCreationMultiForm`` itself
by overriding the :meth:`MultiModelForm.save` method. ::

    class UserCreationMultiForm(MultiModelForm):
        form_classes = {
            'user': UserCreationForm,
            'profile': UserProfileForm,
        }

        def save(self, commit=True):
            objects = super(UserCreationMultiForm, self).save(commit=False)

            if commit:
                user = objects['user']
                user.save()
                profile = objects['profile']
                profile.user = user
                profile.save()

            return objects

If we do that, we can simplify our view to this::

    class UserSignupView(CreateView):
        form_class = UserCreationMultiForm
        success_url = reverse_lazy('home')


Working with UpdateView
-----------------------

Working with :class:`~django:django.views.generic.edit.UpdateView` likewise is
quite easy, but you most likely will have to override the
:class:`~django:django.views.generic.edit.FormMixin.get_form_kwargs` method in
order to pass in the instances that you want to work on.  If we keep with the
user/profile example, it would look something like this::

    # forms.py
    from django import forms
    from django.contrib.auth import get_user_model
    from betterforms.multiform import MultiModelForm
    from .models import UserProfile

    User = get_user_model()

    class UserEditForm(forms.ModelForm):
        class Meta:
            fields = ('email',)

    class UserProfileForm(forms.ModelForm):
        class Meta:
            fields = ('favorite_color',)

    class UserEditMultiForm(MultiModelForm):
        form_classes = {
            'user': UserEditForm,
            'profile': UserProfileForm,
        }

    # views.py
    from django.views.generic import UpdateView
    from django.core.urlresolvers import reverse_lazy
    from django.shortcuts import redirect
    from django.contrib.auth import get_user_model
    from .forms import UserEditMultiForm

    User = get_user_model()

    class UserSignupView(UpdateView):
        model = User
        form_class = UserEditMultiForm
        success_url = reverse_lazy('home')

        def get_form_kwargs(self):
            kwargs = super(UserSignupView, self).get_form_kwargs()
            kwargs.update(instance={
                'user': self.object,
                'profile': self.object.profile,
            })
            return kwargs


Working with WizardView
-----------------------

:class:`MultiForms <MultiForm>` also support the ``WizardView`` classes
provided by django-formtools_ (or Django before 1.8), however you must set a
``base_fields`` attribute on your form class. ::

    # forms.py
    from django import forms
    from betterforms.multiform import MultiForm

    class Step1Form(MultiModelForm):
        # We have to set base_fields to a dictionary because the WizardView
        # tries to introspect it.
        base_fields = {}

        form_classes = {
            'user': UserEditForm,
            'profile': UserProfileForm,
        }

Then you can use it like normal. ::

    # views.py
    try:
        from django.contrib.formtools.wizard.views import SessionWizardView
    except ImportError:  # Django >= 1.8
        from formtools.wizard.views import SessionWizardView

    from .forms import Step1Form, Step2Form

    class MyWizardView(SessionWizardView):
        def done(self, form_list, form_dict, **kwargs):
            step1form = form_dict['1']
            # You can get the data for the user form like this:
            user = step1form['user'].save()
            # ...

    wizard_view = MyWizardView.as_view([Step1Form, Step2Form])

The reason we have to set ``base_fields`` to a dictionary is that the
``WizardView`` does some introspection to determine if any of the forms accept
files and then it makes sure that the ``WizardView`` has a ``file_storage`` on
it. By setting ``base_fields`` to an empty dictionary, we can bypass this check.

.. warning::

    If you have have any forms that accept Files, you must configure the
    ``file_storage`` attribute for your WizardView.

.. _django-formtools: http://django-formtools.readthedocs.org/en/latest/wizard.html


API Reference
-------------

.. class:: MultiForm

    The main interface for customizing :class:`MultiForms <MultiForm>` is
    through overriding the :attr:`~MultiForm.form_classes` class attribute.

    Once a MultiForm is instantiated, you can access the child form instances
    with their names like this::

        >>> class MyMultiForm(MultiForm):
                form_classes = {
                    'foo': FooForm,
                    'bar': BarForm,
                }
        >>> forms = MyMultiForm()
        >>> foo_form = forms['foo']

    You may also iterate over a multiform to get all of the fields for each
    child instance.

    .. rubric:: MultiForm API

    The following attributes and methods are made available for customizing the
    instantiation of multiforms.

    .. method:: __init__(*args, **kwargs)

        The :meth:`~MultiForm.__init__` is basically just a pass-through to the
        children form classes' initialization methods, the only thing that it
        does is provide special handling for the ``initial`` parameter.
        Instead of being a dictionary of initial values, ``initial`` is now a
        dictionary of form name, initial data pairs. ::

            UserProfileMultiForm(initial={
                'user': {
                    # User's initial data
                },
                'profile': {
                    # Profile's initial data
                },
            })

    .. attribute:: form_classes

        This is a dictionary of form name, form class pairs.  If the order of
        the forms is important (for example for output), you can use an
        OrderedDict instead of a plain dictionary.

    .. method:: get_form_args_kwargs(key, args, kwargs)

        This method is available for customizing the instantiation of each form
        instance.  It should return a two-tuple of args and kwargs that will
        get passed to the child form class that corresponds with the key that
        is passed in.  The default implementation just adds a prefix to each
        class to prevent field value clashes.

    .. rubric:: Form API

    The following attributes and methods are made available for mimicking the
    :class:`~django:django.forms.Form` API.

    .. attribute:: media

    .. attribute:: is_bound

    .. attribute:: cleaned_data

        Returns an OrderedDict of the ``cleaned_data`` for each of the child
        forms.

    .. method:: is_valid

    .. method:: non_field_errors

    .. method:: as_table

    .. method:: as_ul

    .. method:: as_p

    .. method:: is_multipart

    .. method:: hidden_fields

    .. method:: visible_fields


.. class:: MultiModelForm

    :class:`MultiModelForm` differs from :class:`MultiForm` only in that adds
    special handling for the ``instance`` parameter for initialization and has
    a :meth:`~MultiModelForm.save` method.

    .. method:: __init__(*args, **kwargs)

        :class:`MultiModelForm's <MultiModelForm>` initialization method
        provides special handling for the ``instance`` parameter.  Instead of
        being one object, the ``instance`` parameter is expected to be a
        dictionary of form name, instance object pairs. ::

            UserProfileMultiForm(instance={
                'user': user,
                'profile': user.profile,
            })

    .. method:: save(commit=True)

        The :meth:`~MultiModelForm.save` method will iterate through the child
        classes and call save on each of them.  It returns an OrderedDict of
        form name, object pairs, where the object is what is returned by the
        save method of the child form class.  Like the :meth:`ModelForm.save
        <django:django.forms.models.ModelForm.save>` method, if ``commit`` is
        ``False``, :meth:`MultiModelForm.save` will add a ``save_m2m`` method
        to the :class:`MultiModelForm` instance to aid in saving the
        many-to-many relations later.


Addendum About django-multiform
-------------------------------

There is another Django app that provides a similar wrapper called
django-multiform that provides essentially the same features as betterform's
:class:`MultiForm`. I searched for an app that did this feature when I started
work on betterform's version, but couldn't find one. I have looked at
django-multiform now and I think that while they are pretty similar, but there
are some differences which I think should be noted:

1.  django-multiform's ``MultiForm`` class actually inherits from Django's Form
    class. I don't think it is very clear if this is a benefit or a
    disadvantage, but to me it seems that it means that there is Form API that
    exposed by django-multiform's ``MultiForm`` that doesn't actually delegate
    to the child classes.

2.  I think that django-multiform's method of dispatching the different values
    for instance and initial to the child classes is more complicated that it
    needs to be.  Instead of just accepting a dictionary like betterform's
    :class:`MultiForm` does, with django-multiform, you have to write a
    `dispatch_init_initial` method.
