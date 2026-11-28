#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
SKILLS_ROOT="$REPO_ROOT/skills"
TARGET="$HOME/.codex/skills"
ALL=false
LIST=false
CATEGORY_ARG=""
SKILL_ARG=""

usage() {
  cat <<'EOF'
Usage: ./scripts/install_skills.sh [--all | --category <cat> | --skill <id>] [--target <path>] [--list]
  --all                 Install every cataloged skill.
  --category <cat>      Install a category; comma-separated values are accepted.
  --skill <id>          Install a skill; comma-separated values are accepted.
  --target <path>       Destination root (default: $HOME/.codex/skills).
  --list                List categories and skills without installing.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=true; shift ;;
    --list) LIST=true; shift ;;
    --category)
      [[ $# -ge 2 ]] || { echo "--category requires a value" >&2; exit 2; }
      CATEGORY_ARG="${CATEGORY_ARG:+$CATEGORY_ARG,}$2"; shift 2 ;;
    --skill)
      [[ $# -ge 2 ]] || { echo "--skill requires a value" >&2; exit 2; }
      SKILL_ARG="${SKILL_ARG:+$SKILL_ARG,}$2"; shift 2 ;;
    --target)
      [[ $# -ge 2 ]] || { echo "--target requires a value" >&2; exit 2; }
      TARGET="$2"; shift 2 ;;
    --category=*) CATEGORY_ARG="${CATEGORY_ARG:+$CATEGORY_ARG,}${1#*=}"; shift ;;
    --skill=*) SKILL_ARG="${SKILL_ARG:+$SKILL_ARG,}${1#*=}"; shift ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$SKILLS_ROOT" ]] || { echo "Skills directory not found: $SKILLS_ROOT" >&2; exit 1; }

catalog_categories=()
catalog_ids=()
catalog_paths=()
for category_dir in "$SKILLS_ROOT"/*; do
  [[ -d "$category_dir" ]] || continue
  category=${category_dir##*/}
  for skill_dir in "$category_dir"/*; do
    [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue
    skill_id=${skill_dir##*/}
    if [[ ! "$category" =~ ^[a-z0-9-]+$ || ! "$skill_id" =~ ^[a-z0-9-]+$ ]]; then
      echo "Invalid category or skill directory name: $skill_dir" >&2
      exit 1
    fi
    for existing_id in "${catalog_ids[@]:-}"; do
      if [[ "$existing_id" == "$skill_id" ]]; then
        echo "Duplicate skill id '$skill_id' across categories; flat installation would be ambiguous." >&2
        exit 1
      fi
    done
    catalog_categories+=("$category")
    catalog_ids+=("$skill_id")
    catalog_paths+=("$skill_dir")
  done
done

if [[ ${#catalog_ids[@]} -eq 0 ]]; then
  echo "No skills found under $SKILLS_ROOT" >&2
  exit 1
fi

contains() {
  local needle="$1"
  shift
  local item
  for item in "$@"; do
    [[ "$item" == "$needle" ]] && return 0
  done
  return 1
}

if $LIST; then
  for category_dir in "$SKILLS_ROOT"/*; do
    [[ -d "$category_dir" ]] || continue
    category=${category_dir##*/}
    count=0
    entries=""
    for index in "${!catalog_ids[@]}"; do
      if [[ "${catalog_categories[$index]}" == "$category" ]]; then
        count=$((count + 1))
        entries+="  - ${catalog_ids[$index]}"$'\n'
      fi
    done
    if [[ $count -gt 0 ]]; then
      printf '%s (%s)\n' "$category" "$count"
      printf '%s' "$entries"
    fi
  done
  printf 'Total: %s skills\n' "${#catalog_ids[@]}"
  exit 0
fi

requested_categories=()
requested_skills=()
if [[ -n "$CATEGORY_ARG" ]]; then IFS=',' read -r -a requested_categories <<< "$CATEGORY_ARG"; fi
if [[ -n "$SKILL_ARG" ]]; then IFS=',' read -r -a requested_skills <<< "$SKILL_ARG"; fi

if ! $ALL && [[ ${#requested_categories[@]} -eq 0 && ${#requested_skills[@]} -eq 0 ]]; then
  echo "Choose --all, --category <cat>, or --skill <id>; use --list to inspect the catalog." >&2
  exit 2
fi
if $ALL && [[ ${#requested_categories[@]} -gt 0 || ${#requested_skills[@]} -gt 0 ]]; then
  echo "--all cannot be combined with --category or --skill." >&2
  exit 2
fi

for requested in ${requested_categories[@]+"${requested_categories[@]}"}; do
  contains "$requested" ${catalog_categories[@]+"${catalog_categories[@]}"} || {
    echo "Unknown category: $requested" >&2; exit 1;
  }
done
for requested in ${requested_skills[@]+"${requested_skills[@]}"}; do
  contains "$requested" ${catalog_ids[@]+"${catalog_ids[@]}"} || {
    echo "Unknown skill: $requested" >&2; exit 1;
  }
done

selected_indices=()
for index in "${!catalog_ids[@]}"; do
  if $ALL || contains "${catalog_categories[$index]}" ${requested_categories[@]+"${requested_categories[@]}"} || \
      contains "${catalog_ids[$index]}" ${requested_skills[@]+"${requested_skills[@]}"}; then
    selected_indices+=("$index")
  fi
done
if [[ ${#selected_indices[@]} -eq 0 ]]; then
  echo "No catalog entries matched the requested category or skill." >&2
  exit 1
fi

if [[ -e "$TARGET" && ! -d "$TARGET" ]]; then
  echo "Target is a file, not a directory: $TARGET" >&2
  exit 1
fi
mkdir -p "$TARGET"
TARGET=$(cd "$TARGET" && pwd -P)

for index in "${selected_indices[@]}"; do
  skill_id=${catalog_ids[$index]}
  source=${catalog_paths[$index]}
  destination="$TARGET/$skill_id"
  rm -rf -- "$destination"
  mkdir -p "$destination"

  while IFS= read -r -d '' file; do
    relative=${file#"$source"/}
    destination_file="$destination/$relative"
    mkdir -p "$(dirname "$destination_file")"
    cp "$file" "$destination_file"
  done < <(find "$source" -type d -name __pycache__ -prune -o -type f ! -name '*.pyc' -print0)

  # Remove only the exact legacy underscore spelling of a migrated skill.
  if [[ "$skill_id" == *-codex ]]; then
    legacy_id="${skill_id%-codex}_codex"
    rm -rf -- "$TARGET/$legacy_id"
  fi
  printf 'Installed %s -> %s\n' "$skill_id" "$destination"
done

printf 'Installed %s skill(s) into %s\n' "${#selected_indices[@]}" "$TARGET"
printf 'Restart Codex to load the refreshed skills.\n'
