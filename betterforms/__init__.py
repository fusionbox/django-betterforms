try:
    from importlib.metadata import version
except ImportError:  # For Python <3.8 with backport
    from importlib_metadata import version

__version__ = version("django-betterforms")
