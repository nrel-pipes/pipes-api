-include env_make

BASE_IMAGE_TAG ?= py312bookworm

PROJECT_NAME=pipes-api

ifdef AWS_ACCOUNT_ID
  REGISTRY-IDS=$(AWS_ACCOUNT_ID)
else
  $(error AWS_ACCOUNT_ID is not set)
endif

REPO = $(REGISTRY-IDS).dkr.ecr.us-west-2.amazonaws.com/nrel-$(PROJECT_NAME)

ifdef RELEASE_SHA2
  HEAD_VER=$(RELEASE_SHA2)
else ifdef RELEASE_SHA1
  HEAD_VER=$(RELEASE_SHA1)
else
	HEAD_VER=$(shell git log -1 --pretty=tformat:%h)
endif

$(info HEAD_VER="$(HEAD_VER)")

ifdef BRANCH_NAME2
	BRANCH_NAME=$(BRANCH_NAME2)
else ifdef BRANCH_NAME1
	BRANCH_NAME=$(BRANCH_NAME1)
else
	BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD)
endif

$(info BRANCH_NAME="$(BRANCH_NAME)")

# git release version - use for rollbacks

TAG ?= $(CODEBUILD_BUILD_NUMBER)-$(BASE_IMAGE_TAG)-$(BRANCH_NAME)-$(HEAD_VER)

.PHONY: build push

build:
	docker build -t $(REPO):$(TAG) \
		--build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG) \
		--build-arg AWS_ACCOUNT_ID=$(REGISTRY-IDS) \
	 	-f deployment/Dockerfile \
		./

push:
	docker push $(REPO):$(TAG)
