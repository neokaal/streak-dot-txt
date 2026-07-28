PYTHON ?= .env/bin/python
NPM ?= npm
CARGO ?= cargo
TAURI_DIR := desktop/src-tauri

.DEFAULT_GOAL := help

.PHONY: help install install-runtime install-dev install-build install-desktop \
	run-api run-cli run-desktop test test-python test-rust check coverage \
	build build-sidecar benchmark-startup release release-app distribute \
	desktop-app desktop-dist clean

help:
	@echo "Setup"
	@echo "  install          Install locked development, build, and desktop dependencies"
	@echo "  install-runtime  Install only application runtime dependencies"
	@echo "  install-dev      Install runtime and automated-test dependencies"
	@echo "  install-build    Install runtime and PyInstaller dependencies"
	@echo "  install-desktop  Install locked npm dependencies with npm ci"
	@echo ""
	@echo "Run"
	@echo "  run-cli          Show CLI help"
	@echo "  run-api          Start the local web/API server"
	@echo "  run-desktop      Start API and Tauri development window together"
	@echo ""
	@echo "Verify"
	@echo "  test             Run Python and Rust tests"
	@echo "  check            Run tests plus compile and dependency checks"
	@echo "  coverage         Generate Python coverage reports"
	@echo "  benchmark-startup Build and measure the sidecar using temporary streak data"
	@echo ""
	@echo "Package"
	@echo "  build            Compile Python and the release-mode Rust shell"
	@echo "  build-sidecar    Build the directory-based Python sidecar"
	@echo "  release          Verify and build all native bundles configured for this OS"
	@echo "  release-app      Verify and build the macOS .app without Finder automation"
	@echo "  distribute       Alias for release"

install: install-dev install-build install-desktop

install-runtime:
	$(PYTHON) -m pip install -c requirements.lock -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -c requirements.lock -r requirements-dev.txt

install-build:
	$(PYTHON) -m pip install -c requirements.lock -r requirements-build.txt

install-desktop:
	cd desktop && $(NPM) ci

run-cli:
	$(PYTHON) streakdottxt.py --help

run-api:
	$(PYTHON) run_api.py

run-desktop:
	$(PYTHON) desktop/run_local.py

test: test-python test-rust

test-python:
	$(PYTHON) -m pytest -q

test-rust:
	cd $(TAURI_DIR) && $(CARGO) test

check: test
	$(PYTHON) -m compileall -q streak_core streak_api desktop scripts tests streakdottxt.py streaksgui.py
	$(PYTHON) -m pip check
	cd desktop && $(NPM) ls --depth=0
	cd $(TAURI_DIR) && $(CARGO) fmt --check
	cd $(TAURI_DIR) && $(CARGO) check --release

coverage:
	$(PYTHON) -m coverage run -m pytest
	$(PYTHON) -m coverage report
	$(PYTHON) -m coverage html

build:
	$(PYTHON) -m compileall -q streak_core streak_api desktop streakdottxt.py
	cd $(TAURI_DIR) && $(CARGO) build --release

build-sidecar:
	$(PYTHON) desktop/package_sidecar.py

benchmark-startup: build-sidecar
	$(PYTHON) desktop/measure_startup.py

release: check
	$(PYTHON) desktop/package_release.py

release-app: check
	$(PYTHON) desktop/package_release.py --bundles app

distribute: release

desktop-app: release-app

desktop-dist: distribute

clean:
	$(PYTHON) scripts/clean.py
