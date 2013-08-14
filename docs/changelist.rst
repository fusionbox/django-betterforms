Changlist Forms
===============

.. currentmodule:: betterforms.changelist

**Changlist Forms** are designed to facilitate easy searching, sorting and
filtering on django models, along with providing a framework for building other
functionality that deals with operations on lists of model instances.


.. class:: ChangeListForm

    Base form class for all **Changlist** forms.

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
                context['queryset'] = form.queryset
            return render_to_response(context, ...)


.. class:: SortForm

    Form which facilitates the sorting instances of a model.  This form adds a a
    field ``sorts`` to the model which is used to dictate the columns which
    should be sorted on and in what order.


   .. attribute:: HEADERS

      The list of :class:`Header` objects for sorting.

   .. attribute:: Header

      Shortcut to ::class:`Header`

   .. method:: get_order_by

      Returns a list of column names that are used in the ``order_by`` call on
      the returned queryset.

.. class:: Header

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


.. currentmodule:: betterforms.views

.. class:: BrowseView

   Class-based view for working with changelists.
