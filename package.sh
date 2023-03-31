#!/bin/sh

set -e

unset GIT_DIR
unset GIT_WORK_DIR
unset GIT_INDEX_FILE

PACKAGENAME=${PWD##*/}
: ${DOCKERHUB:="docker.project.site"}
: ${TAGVERSION:=$(git rev-parse --short HEAD)}
: ${ENVIRONMENT:="production"}

SCRIPT_ROOT=$(dirname "$(readlink -f $0)")
DOCKER_ROOT="$SCRIPT_ROOT/docker/ci"
IMAGE="$DOCKERHUB/$PACKAGENAME:$ENVIRONMENT-$TAGVERSION"

COLOR='\033[0;34m'
NC='\033[0m'

info() {
  printf "${COLOR}Running command with the following variables:${NC}\n"
  printf "PACKAGENAME=${COLOR}${PACKAGENAME}${NC}\n"
  printf "DOCKERHUB=${COLOR}${DOCKERHUB}${NC}\n"
  printf "IMAGE=${COLOR}${IMAGE}${NC}\n\n"
}

build() {
  docker \
    build "$SCRIPT_ROOT" \
      --file "$DOCKER_ROOT/Dockerfile" \
      --build-arg ENVIRONMENT=$ENVIRONMENT \
      --tag $IMAGE
  docker push $IMAGE
}

compose() {
  env IMAGE=$IMAGE PACKAGENAME=$PACKAGENAME docker compose \
    -f "$DOCKER_ROOT/docker-compose.yml" \
    $@
}

config() {
  echo "Running config in $PACKAGENAME-conf"
  docker run --rm -it -v $PACKAGENAME-conf:/conf -w /conf alpine sh -c "apk add vim && sh"
}

command=$1
shift

info
case "$command" in
  build)
    build
    ;;
  up)
    compose "up" "-d" "--build"
    ;;
  compose)
    compose $@
    ;;
  pull)
    compose "pull"
    ;;
  manage)
    compose "exec" "web" "python" "manage.py" $@
    ;;
  config)
    config
    ;;
esac
