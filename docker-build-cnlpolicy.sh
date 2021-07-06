export DOCKER_VERSION=1.0.3
# docker build --tag cnl-policy:${DOCKER_VERSION} --build-arg GIT_TOKEN=${GIT_TOKEN} .
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 578177722126.dkr.ecr.us-east-2.amazonaws.com
docker buildx build --platform linux/amd64 -t  cnl-policy:${DOCKER_VERSION} --push --build-arg GIT_TOKEN=${GIT_TOKEN} .
docker tag cnl-policy:${DOCKER_VERSION} 578177722126.dkr.ecr.us-east-2.amazonaws.com/cnl-policy:${DOCKER_VERSION}
docker push 578177722126.dkr.ecr.us-east-2.amazonaws.com/cnl-policy:${DOCKER_VERSION}
