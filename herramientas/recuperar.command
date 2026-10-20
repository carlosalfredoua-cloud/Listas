#!/bin/bash
set -euo pipefail
CARLOS_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CARLOS_BUNDLE_DIR="$(CDPATH= cd -- "$CARLOS_HELPER_DIR/.." && pwd)"
CARLOS_VENV="$CARLOS_BUNDLE_DIR/.venv-descifrado"
CARLOS_ENV_PYTHON="$CARLOS_VENV/bin/python"
CARLOS_PYTHON=""
for candidate in "$CARLOS_ENV_PYTHON" python3.12 /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3,12))' >/dev/null 2>&1; then
        CARLOS_PYTHON="$candidate"
        break
    fi
done
if [[ -z "$CARLOS_PYTHON" ]]; then
    printf '%s\n' 'Falta Python 3.12 o posterior. Instala Python 3.12 universal2 desde python.org y vuelve a ejecutar. No se requiere Homebrew.' >&2
    exit 1
fi
if [[ ! -e "$CARLOS_VENV" ]]; then
    "$CARLOS_PYTHON" -m venv "$CARLOS_VENV"
fi
if [[ ! -x "$CARLOS_ENV_PYTHON" ]] || ! "$CARLOS_ENV_PYTHON" -c 'import sys; raise SystemExit(sys.version_info < (3,12))'; then
    printf '%s\n' 'El entorno .venv-descifrado existente no es compatible. No se ha eliminado; apartalo manualmente antes de reintentar.' >&2
    exit 1
fi
"$CARLOS_ENV_PYTHON" -m pip --isolated --disable-pip-version-check --no-input --no-cache-dir install --no-index --find-links "$CARLOS_BUNDLE_DIR/dependencias_descifrado/wheels" --only-binary=:all: --require-hashes -r "$CARLOS_HELPER_DIR/requirements-descifrado.txt"
exec "$CARLOS_ENV_PYTHON" "$CARLOS_HELPER_DIR/recuperar.py" "$@"
