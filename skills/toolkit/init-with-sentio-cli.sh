#!/usr/bin/env bash
set -euo pipefail

if [[ ${1:-} == "" ]]; then
  echo "Usage: $0 <project-name> [chain-type] [target-directory] [eth-chain-id]"
  echo "Example: $0 my-processor eth . 1"
  exit 1
fi

PROJECT_NAME="$1"
CHAIN_TYPE="${2:-eth}"
TARGET_DIR="${3:-.}"
ETH_CHAIN_ID="${4:-1}"

cmd=(npx -y @sentio/cli@latest create "$PROJECT_NAME" --directory "$TARGET_DIR" -c "$CHAIN_TYPE")
if [[ "$CHAIN_TYPE" == "eth" ]]; then
  cmd+=(--chain-id "$ETH_CHAIN_ID")
fi

printf 'Running:'
printf ' %q' "${cmd[@]}"
printf '\n'
"${cmd[@]}"

echo ""
echo "Project initialized at: $TARGET_DIR/$PROJECT_NAME"
echo "Next steps:"
echo "  cd '$TARGET_DIR/$PROJECT_NAME'"
echo "  npm run test"
echo "  npm run build"
