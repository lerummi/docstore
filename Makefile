#include .mk/bumpversion.mk

MAKEFLAGS += --warn-undefined-variables --no-print-directory
.SHELLFLAGS := -eu -o pipefail -c

all: help
.PHONY: all

# Use bash for inline if-statements
SHELL:=bash

# Application settings
export APP_NAME=docstore

# Branch specific
export BRANCH_NAME ?= $(shell git branch --show-current)
ifeq ($(BRANCH_NAME),main)
	APP_SUFFIX :=
else
	APP_SUFFIX := -$(BRANCH_NAME)
endif
export APP_SUFFIX

# Enable BuildKit for Docker build
export IMAGE_TAG:=$(shell echo $(BRANCH_NAME) | sed 's/\//-/')

##@ Helpers
help: ## display this help
	@echo "$(APP_NAME)"
	@echo "============================="
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m"} /^[a-zA-Z0-9_%\/-]+:.*?##/ { printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@printf "\n"


build: DARGS?=
build: ## build pas contrainer
	docker compose -f docker-compose.yaml build $(DARGS)

run: PORT?=8888
run: ## run a foreground container for a stack locally
	@printf "\n"
	@echo "You may access the notebook server from the browser using http://127.0.0.1:$(PORT)"
	@printf "\n"
	PORT=$(PORT) docker compose -f docker-compose.yaml up 

##@ Pre-commit Hooks
pre-commit-all: ## run pre-commit hook on all files
	@pre-commit run --all-files || (printf "\n\n\n" && git --no-pager diff --color=always)
pre-commit-install: ## set up the git hook scripts
	@pre-commit --version
	@pre-commit install
