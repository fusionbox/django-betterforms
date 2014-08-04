TESTS=tests betterforms
SETTINGS=tests.sqlite_test_settings
COVERAGE_COMMAND=


test: test-builtin

test-builtin:
	cd tests && DJANGO_SETTINGS_MODULE=$(SETTINGS) $(COVERAGE_COMMAND) ./manage.py test --traceback $(TESTS) --verbosity=2

coverage:
	+make test COVERAGE_COMMAND='coverage run --source=betterforms --omit="*tests*" --branch --parallel-mode'
	cd tests && coverage combine && coverage html

docs:
	cd docs && $(MAKE) html

.PHONY: test test-builtin coverage docs
