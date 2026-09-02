# Makefile for GitClonePro

.PHONY: help install dev-install test lint format clean build publish

help:
	@echo "GitClonePro Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  install      Install package"
	@echo "  dev-install  Install with development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Check code style"
	@echo "  format       Format code"
	@echo "  clean        Clean artifacts"
	@echo "  build        Build package"
	@echo "  publish      Publish to PyPI"

install:
	pip install -e .

dev-install:
	pip install