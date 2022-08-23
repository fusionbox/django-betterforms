Introduction
============

``django-betterforms`` provides a suite of tools to make working with forms in
Django easier.

Installation
------------

1.  Install the package::

        $ pip install django-betterforms

    Or you can install it from source::

        $ pip install -e git://github.com/fusionbox/django-betterforms@master#egg=django-betterforms-dev

2.  Add ``betterforms`` to your ``INSTALLED_APPS``.


Quick Start
-----------
Getting started with ``betterforms`` is easy.  If you are using the build in
form base classes provided by django, its as simple as switching to the form
base classes provided by ``betterforms``.

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

And then in your template.

.. code-block:: html

    <form method="post">
         {% include 'betterforms/form_as_fieldsets.html' %}
    </form>

Which will render the following.

.. code-block:: html

    <fieldset class="formFieldset info">
            <div class="required username formField">
                    <label for="id_username">Username</label>
                    <input id="id_username" name="username" type="text" />
            </div>
            <div class="required email formField">
                    <label for="id_email">Email</label>
                    <input id="id_email" name="email" type="text" />
            </div>
    </fieldset>
    <fieldset class="formFieldset location">
            <div class="required address formField">
                    <label for="id_address">Address</label>
                    <input id="id_address" name="address" type="text" />
            </div>
            <fieldset class="formFieldset location_1">
                    <div class="required city formField">
                            <label for="id_city">City</label>
                            <input id="id_city" name="city" type="text" />
                    </div>
                    <div class="required state formField">
                            <label for="id_state">State</label>
                            <input id="id_state" name="state" type="text" />
                    </div>
                    <div class="required zip formField">
                            <label for="id_zip">Zip</label>
                            <input id="id_zip" name="zip" type="text" />
                    </div>
            </fieldset>
    </fieldset>
    <fieldset class="formFieldset password">
            <div class="required password1 formField">
                    <label for="id_password1">Password</label>
                    <input id="id_password1" name="password1" type="password" />
            </div>
            <div class="required password2 formField">
                    <label for="id_password2">Confirm Password</label>
                    <input id="id_password2" name="password2" type="password" />
            </div>
    </fieldset>
