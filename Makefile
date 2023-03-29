# RagRelay Makefile — compile, test and demo targets

PY ?= python
FIXTURE ?= examples/profiles.json

.PHONY: all build build-py build-go test demo route simulate manifest score clean

all: build

