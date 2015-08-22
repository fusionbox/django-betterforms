#!/usr/bin/env python3

from tox._config import parseconfig

travis = open('.travis.yml', 'w')
travis.write("language: python\n")
travis.write("python: 2.7\n")
travis.write("env:\n")
for env in parseconfig(None, 'tox').envlist:
    travis.write("  - TOX_ENV=%s\n" % env)
travis.write("install:\n")
travis.write("  - pip install tox\n")
travis.write("  - pip install coveralls\n")
travis.write("script:\n")
travis.write("  - tox -e $TOX_ENV\n")
travis.write("after_success: cd tests && coveralls\n")
