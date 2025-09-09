#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="mhm-ontology-tools:latest"
DOCKERFILE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DOCKERFILE_DIR/.." && pwd)"

detect_platform() {
  local arch
  arch=$(uname -m || true)
  case "$arch" in
    arm64|aarch64)
      echo "linux/arm64";;
    x86_64|amd64)
      echo "linux/amd64";;
    *)
      echo "";;
  esac
}

ensure_image() {
  if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "[tools] Image not found. Building $IMAGE_NAME..."
    build_image
  fi
}

build_image() {
  local platform
  platform=$(detect_platform)
  echo "[tools] Building image for platform: ${platform:-default}"
  if [[ -n "$platform" ]]; then
    docker build --platform "$platform" -t "$IMAGE_NAME" -f "$DOCKERFILE_DIR/Dockerfile" "$DOCKERFILE_DIR"
  else
    docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_DIR/Dockerfile" "$DOCKERFILE_DIR"
  fi
}

run_in_container() {
  ensure_image
  docker run --rm \
    -v "$REPO_ROOT":/work \
    -w /work \
    "$IMAGE_NAME" "$@"
}

run_interactive() {
  ensure_image
  docker run --rm -it \
    -v "$REPO_ROOT":/work \
    -w /work \
    "$IMAGE_NAME" "$@"
}

usage() {
  cat <<'USAGE'
Usage: tooling/run_ontology_tools.sh <command> [args]

Commands:
  build                         Build the Docker image (caches for reuse)
  shell                         Start interactive shell in the tools container

  check-syntax <file.owl>       Validate RDF/XML syntax with Jena riot
  profile <file.owl> [DL|EL]    OWL 2 profile validation via ROBOT
  reason <file.owl> [elk|hermit]Consistency + classification via ROBOT
  report <file.owl>             ROBOT QA report (report.tsv in CWD)
  openllet-consistency <file>   Openllet consistency check (if installed)

  exec -- <args...>             Run arbitrary command in the container

Examples:
  tooling/run_ontology_tools.sh build
  tooling/run_ontology_tools.sh check-syntax mhm_ontology.owl
  tooling/run_ontology_tools.sh profile mhm_ontology.owl DL
  tooling/run_ontology_tools.sh reason mhm_ontology.owl elk
  tooling/run_ontology_tools.sh report mhm_ontology.owl
  tooling/run_ontology_tools.sh shell
  tooling/run_ontology_tools.sh exec -- robot --help
USAGE
}

cmd=${1:-}
case "$cmd" in
  build)
    build_image
    ;;
  shell)
    run_interactive bash
    ;;
  check-syntax)
    [[ ${2:-} ]] || { echo "Need OWL file"; exit 1; }
    run_in_container bash -lc "riot --validate '${2}'"
    ;;
  profile)
    [[ ${2:-} ]] || { echo "Need OWL file"; exit 1; }
    profile=${3:-DL}
    if [[ -f catalog-v001.xml ]]; then
      run_in_container robot validate-profile --catalog catalog-v001.xml --input "$2" --profile "$profile" --output profile.txt && echo "Wrote profile.txt"
    else
      run_in_container robot validate-profile --input "$2" --profile "$profile" --output profile.txt && echo "Wrote profile.txt"
    fi
    ;;
  reason)
    [[ ${2:-} ]] || { echo "Need OWL file"; exit 1; }
    reasoner=${3:-elk}
    out="classified-${reasoner}.owl"
    run_in_container robot reason --reasoner "$reasoner" --input "$2" --consistency true --output "$out" && echo "Wrote $out"
    ;;
  report)
    [[ ${2:-} ]] || { echo "Need OWL file"; exit 1; }
    if [[ -f catalog-v001.xml ]]; then
      run_in_container robot report --catalog catalog-v001.xml --input "$2" --output report.tsv && echo "Wrote report.tsv"
    else
      run_in_container robot report --input "$2" --output report.tsv && echo "Wrote report.tsv"
    fi
    ;;
  openllet-consistency)
    [[ ${2:-} ]] || { echo "Need OWL file"; exit 1; }
    run_in_container bash -lc 'command -v openllet >/dev/null 2>&1 || { echo "Openllet is not installed in this image."; exit 127; }; openllet consistency -i '"$2"''
    ;;
  exec)
    shift || true
    if [[ ${1:-} == "--" ]]; then shift; fi
    run_in_container "$@"
    ;;
  validate-prov)
    # Merge alignment + examples, then run SPARQL ASK queries
    run_in_container bash -lc '
      set -euo pipefail
      mkdir -p build
      robot merge --catalog catalog-v001.xml \
        --input alignments/mhm-prov-align.owl \
        --input examples.ttl \
        --output build/prov-merged.owl
      failures=0
      for q in queries/*.rq; do
        echo "[check] $q"
        out=$(sparql --data build/prov-merged.owl --query "$q" 2>&1 | tr -d "\r")
        if echo "$out" | grep -q "Ask => Yes"; then
          echo "[OK]   $q"
        else
          echo "[FAIL] $q"
          echo "$out" | tail -n 2
          failures=$((failures+1))
        fi
      done
      if [[ $failures -gt 0 ]]; then
        echo "[validate-prov] $failures failure(s)"; exit 2; 
      fi
      echo "[validate-prov] all checks passed"
    '
    ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
