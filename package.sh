#!/bin/sh

set -e

SCRIPT_ROOT=$(dirname "$(readlink -f $0)")

unset GIT_DIR
unset GIT_WORK_DIR
unset GIT_INDEX_FILE

: ${DOCKERHUB="projectsite.com"}
: ${PACKAGENAME="project-backend"}

build() {
  tag="$DOCKERHUB/$PACKAGENAME:$ENVIRONMENT-$TAGVERSION"

  pkgroot=$(printf %s/%s docker $PACKAGENAME)
  docker \
    build "$SCRIPT_ROOT" \
      --file "$SCRIPT_ROOT/$pkgroot/Dockerfile" \
      --build-arg ENVIRONMENT=$ENVIRONMENT \
      --tag $tag
  docker push $tag
}

command=$1
shift

case "$command" in
  build)
    build
    ;;
esac
