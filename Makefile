nonprod_IMAGE_NAME = nonprod-tools
nonprod_IMAGE_TARGET = nonprod-tools

docker-build: IMAGE=$(nonprod_IMAGE_NAME)
docker-build: IMAGE_TARGET=$(nonprod_IMAGE_TARGET)
docker-build: IMAGE_VERSION=latest
docker-build:
	docker buildx build . --progress=tty -t $(IMAGE):$(IMAGE_VERSION) --target $(IMAGE_TARGET)

_docker-run: IMAGE=$(nonprod_IMAGE_NAME)
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

black: ENTRYPOINT=black
black: IMAGE_ARGS=.
black: _docker-run-default

pytest: ENTRYPOINT=pytest
pytest: IMAGE_ARGS=. --verbose
pytest: _docker-run-default

poetry-show: ENTRYPOINT=poetry
poetry-show: IMAGE_WORKDIR=/opt/src
poetry-show: IMAGE_ARGS=show --outdated
poetry-show: _docker-run

poetry-update: ENTRYPOINT=poetry
poetry-update: IMAGE_ARGS=update --lock
poetry-update: _docker-run-default
# Rebuild image based on new lock file
poetry-update: docker-build

_docker-run-terraform: ENTRYPOINT=terraform
_docker-run-terraform: DOCKER_ARGS=-it
_docker-run-terraform: _docker-run

terraform-fmt: IMAGE_WORKDIR=/mnt/project/terraform
terraform-fmt: IMAGE_ARGS=fmt -recursive .
terraform-fmt: _docker-run-terraform

_docker-run-terraform-nonprod: IMAGE_WORKDIR=/mnt/project/terraform/envs/nonprod
_docker-run-terraform-nonprod: _docker-run-terraform

terraform-init-nonprod: IMAGE_ARGS=init -backend-config config.tfbackend
terraform-init-nonprod: _docker-run-terraform-nonprod

terraform-plan-nonprod: IMAGE_ARGS=plan -var-file config.tfvars
terraform-plan-nonprod: _docker-run-terraform-nonprod


terraform-apply-nonprod: IMAGE_ARGS=apply -var-file config.tfvars
terraform-apply-nonprod: _docker-run-terraform-nonprod

terraform-destroy-nonprod: IMAGE_ARGS=destroy -var-file config.tfvars
terraform-destroy-nonprod: _docker-run-terraform-nonprod

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
