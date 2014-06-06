def python_2_unicode_compatible(klass):
    """
    Borrowed from django.utils.encoding for supporting Django<1.4

    TODO: remove when we drop support for Django<1.4
    """
    import sys
    if sys.version_info < (3,):
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass
