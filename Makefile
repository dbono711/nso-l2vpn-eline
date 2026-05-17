.ONESHELL:

.SILENT:

build-package:
	echo '------- COMPILING PACKAGE: l2vpn-eline'
	$(MAKE) -s -C l2vpn-eline/src all

clean-package:
	echo '------- CLEAN PACKAGE: l2vpn-eline'
	$(MAKE) -s -C l2vpn-eline/src clean

test-package:
	[ -d "tests/.venv" ] || python3 -m venv tests/.venv
	tests/.venv/bin/python -m pip install --upgrade pip > /dev/null
	tests/.venv/bin/pip install -r tests/requirements.txt > /dev/null
	tests/.venv/bin/pytest tests/ -v
	PYTEST_EXIT_CODE=$$?
	rm -rf tests/.venv
	exit $$PYTEST_EXIT_CODE

all: build-package
clean: clean-package
test: test-package
