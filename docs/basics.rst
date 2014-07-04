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

      from betterforms.forms import BetterForm

      class RegistrationForm(BetterForm):
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

      from betterforms.forms import BetterForm

      class RegistrationForm(BetterForm):
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

      from betterforms.forms import BetterForm, Fieldset

      class RegistrationForm(BetterForm):
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

A :class:`Fieldset` can also optionally be declared with a legend kwarg,
which will then be made available as a property to the associated
:class:`BoundFieldset`.

  .. code-block:: python

      Fieldset('location', ('address', ('city', 'state', 'zip')), legend='Place of Residence')

Should you choose to render the form using the betterform templates detailed below,
each fieldset with a legend will be rendered with an added legend tag in the template.

Rendering
---------

To render a form, use the provided template partial.

.. code-block:: html

    <form method="post">
         {% include 'betterforms/form_as_fieldsets.html' %}
    </form>

This partial assumes there is a variable ``form`` available in its context.
This template does the following things.

* outputs the ``csrf_token``.
* outputs a hidden field named ``next`` if there is a ``next`` value available
  in the template context.
* outputs the form media
* loops over ``form.fieldsets``.
    * for each fieldsets, renders the fieldset using the template
      ``betterforms/fieldset_as_div.html``

       * for each item in the fieldset, if it is a fieldset, it is rendered using
         the same template, and if it is a field, renders it using the field
         template.

    * for each field, renders the field using the template
      ``betterforms/field_as_div.html``

If you want to output the form without the CSRF token (for example on a GET
form), you can do so by passing in the csrf_exempt variable.

.. code-block:: html

    <form method="post">
         {% include 'betterforms/form_as_fieldsets.html' csrf_exempt=True %}
    </form>

If you wish to override the label suffix, ``django-betterforms`` provides a
convenient class attribute on the :class:`BetterForm` and
:class:`BetterModelForm` classes. ::


    class MyForm(forms.BetterForm):
        # ... fields

        label_suffix = '->'

.. warning::

    Due to a bug in dealing with the label suffix in Django < 1.6, the
    ``label_suffix`` will not appear in any forms rendered using the
    betterforms templates.  For more information, refer to the `Django bug
    #18134`_.

.. _Django bug #18134: https://code.djangoproject.com/ticket/18134
