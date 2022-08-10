SETTINGS=tests.sqlite_test_settings
COVERAGE_ARGS=

test: test-builtin

test-builtin:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) py.test $(COVERAGE_ARGS)

coverage:
	+make test COVERAGE_ARGS='--cov-config .coveragerc --cov-report html --cov-report= --cov=betterforms'

docs:
	cd docs && $(MAKE) html

.PHONY: test test-builtin coverage docs
