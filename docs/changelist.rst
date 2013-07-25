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

   TODO

.. class:: SortForm

   TODO

Working With Changelists
------------------------

.. currentmodule:: betterforms.views

.. class:: BrowseView

   Class-based view for working with changelists.
