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

.. class:: Header

Headers are the the mechanism through which :class:`SortForm` shines.  They
provide querystrings for operations related to sorting by whatever query
parameter that header is tied to.


Working With Changelists
------------------------

.. currentmodule:: betterforms.views

.. class:: BrowseView

   Class-based view for working with changelists.
