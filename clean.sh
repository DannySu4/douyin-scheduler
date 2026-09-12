#!/usr/bin/env bash
# 清理运行/编译产物，保持仓库干净
set -e
cd "$(dirname "$0")"
rm -rf __pycache__ tests/__pycache__ .pytest_cache logs/ *.pyc
echo "cleaned"
