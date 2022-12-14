DEV_IMAGE_NAME    = dev-env
TERRAFORM_VERSION = $(shell cat .terraform-version)

docker-build-dev-image: IMAGE=$(DEV_IMAGE_NAME)
docker-build-dev-image: IMAGE_VERSION=latest
docker-build-dev-image:
	docker build . -t $(IMAGE):$(IMAGE_VERSION)

_docker-run: PROJECT_DIR=$(shell pwd)
_docker-run: PROJECT_MOUNT_DIR=/project
_docker-run: IMAGE_ENV=PRE_COMMIT_HOME=/project/.cache/pre-commit
_docker-run:
	test -n "$(ENTRYPOINT)"
	test -n "$(IMAGE)"
	test -n "$(IMAGE_VERSION)"
	test -n "$(IMAGE_WORKDIR)"
	test -n "$(IMAGE_ARGS)"
	docker run --rm \
		--entrypoint $(ENTRYPOINT) \
		-v "$(PROJECT_DIR):$(PROJECT_MOUNT_DIR)" \
		-w $(IMAGE_WORKDIR) \
		-e "$(IMAGE_ENV)" \
	$(IMAGE):$(IMAGE_VERSION) $(IMAGE_ARGS)

_docker-run-dev-image: IMAGE=$(DEV_IMAGE_NAME)
_docker-run-dev-image: IMAGE_VERSION=latest
_docker-run-dev-image: IMAGE_WORKDIR=/project
_docker-run-dev-image: _docker-run

pre-commit-run: ENTRYPOINT=pre-commit
pre-commit-run: IMAGE_ARGS=run --all-files
pre-commit-run: _docker-run-dev-image

pre-commit-install-hooks: ENTRYPOINT=pre-commit
pre-commit-install-hooks: IMAGE_ARGS=install-hooks
pre-commit-install-hooks: _docker-run-dev-image

python-black: ENTRYPOINT=black
python-black: IMAGE_ARGS=.
python-black: _docker-run-dev-image

python-pytest: ENTRYPOINT=pytest
python-pytest: IMAGE_ARGS=.
python-pytest: _docker-run-dev-image

_docker-run-terraform: ENTRYPOINT=terraform
_docker-run-terraform: IMAGE=hashicorp/terraform
_docker-run-terraform: IMAGE_VERSION=$(TERRAFORM_VERSION)
_docker-run-terraform: _docker-run

terraform-fmt: IMAGE_WORKDIR=/project/terraform
terraform-fmt: IMAGE_ARGS=fmt -recursive .
terraform-fmt: _docker-run-terraform

_docker-run-terraform-dev: IMAGE_WORKDIR=/project/terraform/envs/dev
_docker-run-terraform-dev: _docker-run-terraform

terraform-init-dev: IMAGE_ARGS=init -backend-config config.tfbackend
terraform-init-dev: _docker-run-terraform-dev

terraform-plan-dev: IMAGE_ARGS=plan -var-file config.tfvars
terraform-plan-dev: _docker-run-terraform-dev

terraform-apply-dev: IMAGE_ARGS=apply -var-file config.tfvars
terraform-apply-dev: _docker-run-terraform-dev

_docker-run-terraform-prod: IMAGE_WORKDIR=/project/terraform/envs/prod
_docker-run-terraform-prod: _docker-run-terraform

terraform-init-prod: IMAGE_ARGS=init -backend-config config.tfbackend
terraform-init-prod: _docker-run-terraform-prod

terraform-plan-prod: IMAGE_ARGS=plan -var-file config.tfvars
terraform-plan-prod: _docker-run-terraform-prod

terraform-apply-prod: IMAGE_ARGS=apply -var-file config.tfvars
terraform-apply-prod: _docker-run-terraform-prod
