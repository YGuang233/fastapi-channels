#!/usr/bin/env bash
set -x

#ruff check fastapi_channels tests docs_src scripts --fix
#ruff format fastapi_channels tests docs_src scripts
ruff check fastapi_channels/throttling --fix
ruff format fastapi_channels/throttling scripts
# --exclude fastapi_channels/**/*_d.py 这个还没有尝试
# ruff直接对我在pyproject.toml中排除的文件不做处理了，虽然这很好但是真奇怪
read -r -p "Press enter to close"