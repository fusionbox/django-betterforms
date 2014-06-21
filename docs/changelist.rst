Changelist Forms
================

.. currentmodule:: betterforms.changelist

**Changelist Forms** are designed to facilitate easy searching and sorting on
django models, along with providing a framework for building other
functionality that deals with operations on lists of model instances.


.. class:: ChangeListForm

    Base form class for all **Changelist** forms.

    * setting the queryset:

      All changelist forms need to *know* what queryset to begin with.  You can
      do this by either passing a named keyword parameter into the contructor of
      the form, or by defining a model attribute on the class.


.. class:: SearchForm

    Form class which facilitates searching across a set of specified fields for
    a model.  This form adds a field to the model ``q`` for the search query.

   .. attribute:: SEARCH_FIELDS
    
     The list of fields that will be searched against.

   .. attribute:: CASE_SENSITIVE

     Whether the search should be case sensitive.


    Here is a simple :class:`SearchForm` example for searching across users.

    .. code-block:: python

       # my_app/forms.py
       from django.contrib.auth.models import get_user_model
       from betterforms.forms import SearchForm

       class UserSearchForm(SearchForm):
           SEARCH_FIELDS = ('username', 'email', 'name')
           model = get_user_model()

        # my_app.views.py
        from my_app.forms import UserSearchForm

        def user_list_view(request):
            form = UserSearchForm(request.GET)
            context = {'form': form}
            if form.is_valid:
                context['queryset'] = form.get_queryset()
            return render_to_response(context, ...)

    :class:`SearchForm` checks to see if the query value is present in any of
    the fields declared in ``SEARCH_FIELDS`` by or-ing together ``Q`` objects
    using ``__contains`` or ``__icontains`` queries on those fields.


.. class:: SortForm

    Form which facilitates the sorting instances of a model.  This form adds a
    hidden field ``sorts`` to the model which is used to dictate the columns
    which should be sorted on and in what order.


   .. attribute:: HEADERS

      The list of :class:`Header` objects for sorting.

      Headers can be declared in multiple ways.

      * As instantiated :class:`Header` objects.:

          .. code-block:: python

             # my_app/forms.py
             from betterforms.forms import SortForm, Header

             class UserSortForm(SortForm):
                 HEADERS = (
                     Header('username', ..),
                     Header('email', ..),
                     Header('name', ..),
                 )
                 model = User

      * As a string:

          .. code-block:: python

             # my_app/forms.py
             from betterforms.forms import SortForm

             class UserSortForm(SortForm):
                 HEADERS = (
                     'username',
                     'email',
                     'name',
                 )
                 model = User

      * As an iterable of ``*args`` which will be used to instantiate the
        :class:`Header` object.:

          .. code-block:: python

             # my_app/forms.py
             from betterforms.forms import SortForm

             class UserSortForm(SortForm):
                 HEADERS = (
                     ('username', ..),
                     ('email', ..),
                     ('name', ..),
                 )
                 model = User

      * As a two-tuple of **header name** and ``**kwargs``.  The name and
        provided ``**kwargs`` will be used to instantiate the :class:`Header`
        objects.

          .. code-block:: python

             # my_app/forms.py
             from betterforms.forms import SortForm

             class UserSortForm(SortForm):
                 HEADERS = (
                     ('username', {..}),
                     ('email', {..}),
                     ('name', {..}),
                 )
                 model = User

      All of these examples are roughly equivilent, resulting in the form
      haveing three sortable headers, ``('username', 'email', 'name')``, which
      will map to those named fields on the ``User`` model.

      See documentation on the :class:`Header` class for more information on
      how sort headers can be configured.

   .. method:: get_order_by

      Returns a list of column names that are used in the ``order_by`` call on
      the returned queryset.

   During instantiation, all declared headers on ``form.HEADERS`` are converted
   to :class:`Header` objects and are accessible from ``form.headers``.

      .. code-block:: python

         >>> [header for header in form.headers]  # Iterate over all headers.
         >>> form.headers[2]  #  Get the header at index-2
         >>> form.headers['username']  #  Get the header named 'username'

.. class:: Header(name, label=None, column_name=None, is_sortable=True)

    Headers are the the mechanism through which :class:`SortForm` shines.  They
    provide querystrings for operations related to sorting by whatever query
    parameter that header is tied to, as well as other values that are helpful
    during rendering.

    .. attribute:: name

    The name of the header.

    .. attribute:: label

    The human readable name of the header.

    .. attribute:: is_active

    ``Boolean`` as to whether this header is currently being used to sort.

    .. attribute:: is_ascending

    ``Boolean`` as to whether this header is being used to sort the data in
    ascending order.

    .. attribute:: is_descending

    ``Boolean`` as to whether this header is being used to sort the data in
    descending order.

    .. attribute:: css_classes

    Space separated list of css classes, suitable for output in the template as
    an HTML element's css class attribute.

    .. attribute:: priority

    1-indexed number as to the priority this header is at in the list of sorts.
    Returns ``None`` if the header is not active.

    .. attribute:: querystring

    The querystring that will sort by this header as the primary sort, moving
    all other active sorts in their current order after this one.  Preserves
    all other query parameters.

    .. attribute:: remove_querystring

    The querystring that will remove this header from the sorts.  Preserves all
    other query parameters.

    .. attribute:: singular_querystring

    The querystring that will sort by this header, and deactivate all other
    active sorts.  Preserves all other query parameters.

Working With Changelists
------------------------

Outputting sort form headers can be done using a provided template partial
located at ``betterforms/sort_form_header.html``

.. code-block:: html

    <th class="{{ header.css_classes }}">
      {% if header.is_sortable %}
        <a href="?{{ header.querystring }}">{{ header.label }}</a>
        {% if header.is_active %}
          {% if header.is_ascending %}
            ▾
          {% elif header.is_descending %}
            ▴
          {% endif %}
          <a href="" data-sort_by="title" data-direction="up"></a>
          <span class="filterActive"><span>{{ header.priority }}</span> <a href="?{{ header.remove_querystring }}">x</a></span>
        {% endif %}
      {% else %}
        {{ header.label }}
      {% endif %}
    </th>

This example assumes that you are using a table to output your data.  It should
be trivial to modify this to suite your needs.

.. currentmodule:: betterforms.views

.. class:: BrowseView

   Class-based view for working with changelists.  It is a combination of
   ``FormView`` and ``ListView`` in that it handles form submissions and
   providing a optionally paginated queryset for rendering in the template.

   Works similarly to the standard ``FormView`` class provided by django,
   except that the form is instantiated using ``request.GET``, and the
   ``object_list`` passed into the template context comes from
   ``form.get_queryset()``.
