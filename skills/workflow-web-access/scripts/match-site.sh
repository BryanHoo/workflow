#!/usr/bin/env bash
# 根据用户输入匹配站点经验文件。

set -u

DIR="$(cd "$(dirname "$0")/../references/site-patterns" && pwd)"
[ ! -d "$DIR" ] && exit 0
[ $# -eq 0 ] && exit 0

QUERY="$*"

for file in "$DIR"/*.md; do
  [ ! -f "$file" ] && continue

  domain="$(basename "$file" .md)"
  aliases="$(grep '^aliases:' "$file" | sed 's/^aliases: *//;s/\[//g;s/\]//g;s/, */|/g;s/ *$//')"
  patterns="$domain"
  [ -n "$aliases" ] && patterns="$patterns|$aliases"

  if echo "$QUERY" | grep -qiE "$patterns"; then
    echo "--- 站点经验: $domain ---"
    awk 'BEGIN{n=0} /^---$/{n++;next} n>=2{print}' "$file"
    echo ""
  fi
done
