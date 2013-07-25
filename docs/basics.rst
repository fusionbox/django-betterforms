Forms
=====

.. currentmodule:: betterforms.forms

``django-betterforms`` provides two new form base classes to use in place of
:class:`django:django.forms.Form`. and :class:`django:django.forms.ModelForm`.


.. class:: BetterForm

   Base form class for non-model forms.

.. class:: BetterModelForm

   Base form class for model forms.

Errors
------

Adding errors in ``betterforms`` is easy:

    >>> form = BlogEntryForm(request.POST)
    >>> form.is_valid()
    True
    >>> form.field_error('title', 'This title is already taken')
    >>> form.is_valid()
    False
    >>> form.errors
    {'title': ['This title is already taken']}

You can also add global errors:

    >>> form = BlogEntryForm(request.POST)
    >>> form.form_error('Not accepting new entries at this time')
    >>> form.is_valid()
    False
    >>> form.errors
    {'__all__': ['Not accepting new entries at this time']}

`form_error` is simply a wrapper around `field_error` that uses the key
`__all__` for the field name.

Fieldsets
---------

One of the most powerful features in ``betterforms`` is the ability to declare
field groupings.  Both :class:`BetterForm` and :class:`BetterModelForm` provide
a common interface for working with fieldsets.

Fieldsets can be declared in any of three formats, or any mix of the three
formats.

* As Two Tuples

  Similar to :ref:`admin fieldsets <django:built-in-auth-views>`, as a list of
  two tuples.  The two tuples should be in the format ``(name,
  fieldset_options)`` where ``name`` is a string representing the title of the
  fieldset and ``fieldset_options`` is a dictionary which will be passed as
  ``kwargs`` to the constructor of the fieldset.

  .. code-block:: python

      from betterforms.forms import BaseForm

      class RegistrationForm(BaseForm):
          ...
          class Meta:
              fieldsets = (
                  ('info', {'fields': ('username', 'email')}),
                  ('location', {'fields': ('address', ('city', 'state', 'zip'))}),
                  ('password', {'password1', 'password2'}),
              )

* As a list of field names

  Fieldsets can be declared as a list of field names.

  .. code-block:: python

      from betterforms.forms import BaseForm

      class RegistrationForm(BaseForm):
          ...
          class Meta:
              fieldsets = (
                  ('username', 'email'),
                  ('address', ('city', 'state', 'zip')),
                  ('password1', 'password2'),
              )

* As instantiated :class:`Fieldset` instances or subclasses of :class:`Fieldset`.

  Fieldsets can be declared as a list of field names.

  .. code-block:: python

      from betterforms.forms import BaseForm, Fieldset

      class RegistrationForm(BaseForm):
          ...
          class Meta:
              fieldsets = (
                  Fieldset('info', fields=('username', 'email')),
                  Fieldset('location', ('address', ('city', 'state', 'zip'))),
                  Fieldset('password', ('password1', 'password2')),
              )

All three of these examples will have *appoximately* the same output.  All of
these formats can be mixed and matched and nested within each other.  And
Unlike django-admin, you may nest fieldsets as deep as you would like.

Rendering
---------

Rendering in ``betterforms`` is currently in flux but will attempt to remain
*mostly* inline with the established standard created by django forms.

Currently, the proper way to render a form is to use the provided template
partial.

.. code-block:: html

    <form method="post">
         {% include 'partials/form_as_fieldsets.html' %}
    </form>

This partial assumes there is a variable ``form`` available in its context.
This template does the following things.

* outputs the ``csrf_token``.
* outputs a hidden field named ``next`` if there is a ``next`` value available
  in the template context.
* outputs the form media
* loops over ``form.fieldsets``.
  * for each fieldsets, renders the fieldset using the template ``partials/fieldset_as_div.html``
    * for each item in the fieldset, if it is a fieldset, it is rendered using
      the same template, and if it is a field, renders it using the field
      template.
  * for each field, renders the field using the template
    ``partials/field_as_div.html``
