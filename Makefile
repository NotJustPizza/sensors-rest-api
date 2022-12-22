DEV_IMAGE_NAME = dev-env

docker-build: IMAGE=$(DEV_IMAGE_NAME)
docker-build: IMAGE_VERSION=latest
docker-build:
	docker build . -t $(IMAGE):$(IMAGE_VERSION)

_docker-run: IMAGE=$(DEV_IMAGE_NAME)
_docker-run: IMAGE_VERSION=latest
_docker-run: PROJECT_DIR=$(shell pwd)
_docker-run: PROJECT_MOUNT_DIR=/mnt/project
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
		$(DOCKER_ARGS) \
	$(IMAGE):$(IMAGE_VERSION) $(IMAGE_ARGS)

_docker-run-default: IMAGE_WORKDIR=/mnt/project
_docker-run-default: _docker-run

pre-commit-run: ENTRYPOINT=pre-commit
pre-commit-run: IMAGE_ARGS=run --all-files
pre-commit-run: DOCKER_ARGS=-e PRE_COMMIT_HOME=.cache/pre-commit $(CUSTOM_DOCKER_ARGS)
pre-commit-run: _docker-run-default

pre-commit-install:
	cp pre-commit-hook.sh .git/hooks/pre-commit

python-black: ENTRYPOINT=black
python-black: IMAGE_ARGS=.
python-black: _docker-run-default

python-pytest: ENTRYPOINT=pytest
python-pytest: IMAGE_ARGS=.
python-pytest: _docker-run-default

_docker-run-terraform: ENTRYPOINT=terraform
_docker-run-terraform: DOCKER_ARGS=-it
_docker-run-terraform: _docker-run

terraform-fmt: IMAGE_WORKDIR=/mnt/project/terraform
terraform-fmt: IMAGE_ARGS=fmt -recursive .
terraform-fmt: _docker-run-terraform

_docker-run-terraform-dev: IMAGE_WORKDIR=/mnt/project/terraform/envs/dev
_docker-run-terraform-dev: _docker-run-terraform

terraform-init-dev: IMAGE_ARGS=init -backend-config config.tfbackend
terraform-init-dev: _docker-run-terraform-dev

terraform-plan-dev: IMAGE_ARGS=plan -var-file config.tfvars
terraform-plan-dev: _docker-run-terraform-dev

terraform-apply-dev: IMAGE_ARGS=apply -var-file config.tfvars
terraform-apply-dev: _docker-run-terraform-dev

terraform-destroy-dev: IMAGE_ARGS=destroy -var-file config.tfvars
terraform-destroy-dev: _docker-run-terraform-dev

_docker-run-terraform-prod: IMAGE_WORKDIR=/mnt/project/terraform/envs/prod
_docker-run-terraform-prod: _docker-run-terraform

terraform-init-prod: IMAGE_ARGS=init -backend-config config.tfbackend
terraform-init-prod: _docker-run-terraform-prod

terraform-plan-prod: IMAGE_ARGS=plan -var-file config.tfvars
terraform-plan-prod: _docker-run-terraform-prod

terraform-apply-prod: IMAGE_ARGS=apply -var-file config.tfvars
terraform-apply-prod: _docker-run-terraform-prod

terraform-destroy-prod: IMAGE_ARGS=destroy -var-file config.tfvars
terraform-destroy-prod: _docker-run-terraform-prod
