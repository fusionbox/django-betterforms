#!/usr/bin/env python
import os
import sys
import warnings


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    from django.core.management import execute_from_command_line

    # Python 3.4 raises deprecation warnings on import for django 1.5-1.7.
    # We can ignore those by not setting the filter until after import.
    warnings.simplefilter('error')

    execute_from_command_line(sys.argv)
