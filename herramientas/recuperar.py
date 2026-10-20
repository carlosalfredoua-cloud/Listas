"""Recuperacion local: clave interactiva, AES-256 y SHA-256 antes de extraer."""

from __future__ import annotations

import argparse
import getpass
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import unicodedata
import warnings
import zipfile

import pyzipper


BUNDLE_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PAYLOAD = "Carlos-Agent-Mac-Completo.zip"
EXPECTED_SHA256 = "d59d00d09430fafafe64d76564e40220227e68e509f180560fcb71edde7d1d61"
EXPECTED_ROOT = "Carlos-Agent-Entrega"
MAX_PAYLOAD_BYTES = 256 * 1024 * 1024
MAX_EXTRACTED_BYTES = 1024 * 1024 * 1024
MAX_ENTRIES = 50_000


def _validated_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    entries = archive.infolist()
    if not entries or len(entries) > MAX_ENTRIES:
        raise ValueError("Numero de entradas del paquete no permitido.")
    if sum(entry.file_size for entry in entries) > MAX_EXTRACTED_BYTES:
        raise ValueError("El contenido excede el limite de extraccion.")
    seen: set[str] = set()
    for entry in entries:
        name = entry.filename
        path = PurePosixPath(name)
        parts = name.rstrip("/").split("/")
        if (not name or "\x00" in name or "\\" in name or path.is_absolute()
                or any(part in ("", ".", "..") or ":" in part for part in parts)
                or not path.parts or path.parts[0] != EXPECTED_ROOT):
            raise ValueError("El paquete contiene una ruta no permitida.")
        key = unicodedata.normalize("NFC", name.rstrip("/")).casefold()
        if key in seen:
            raise ValueError("El paquete contiene rutas duplicadas o ambiguas para macOS.")
        seen.add(key)
        mode = (entry.external_attr >> 16) & 0xFFFF
        file_type = stat.S_IFMT(mode)
        if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
            raise ValueError("No se permiten enlaces simbolicos ni archivos especiales.")
        if entry.flag_bits & 1:
            raise ValueError("El ZIP interior no debe contener entradas cifradas.")
    return entries


def recuperar(password: bytes, archive_path: str | Path | None = None,
              destination_parent: str | Path | None = None) -> Path:
    """Devuelve una carpeta NUEVA. Nunca imprime ni guarda la clave.

    Las pruebas pueden pasar bytes directamente sin argumentos de shell ni
    variables de entorno. Errores eliminan los temporales y la salida parcial.
    """
    if not isinstance(password, bytes) or not password:
        raise ValueError("Se requiere una clave no vacia como bytes.")
    encrypted = Path(archive_path) if archive_path is not None else BUNDLE_ROOT / "Carlos-Agent-Mac-Cifrado.zip"
    parent = Path(destination_parent) if destination_parent is not None else BUNDLE_ROOT.parent
    parent = parent.expanduser().resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("El destino debe ser una carpeta existente.")
    if not encrypted.is_file():
        raise FileNotFoundError("No se encontro Carlos-Agent-Mac-Cifrado.zip junto a herramientas.")
    result: Path | None = None
    with tempfile.TemporaryDirectory(prefix=".carlos-recuperacion-", dir=parent) as temporary:
        workspace = Path(temporary)
        payload = workspace / EXPECTED_PAYLOAD
        digest = hashlib.sha256()
        with pyzipper.AESZipFile(encrypted, "r") as protected:
            entries = protected.infolist()
            if len(entries) != 1 or entries[0].filename != EXPECTED_PAYLOAD:
                raise ValueError("El ZIP cifrado no contiene el unico archivo esperado.")
            entry = entries[0]
            if not (entry.flag_bits & 1) or getattr(entry, "wz_aes_strength", None) != 3:
                raise ValueError("El contenedor no utiliza el cifrado AES-256 esperado.")
            if not 0 < entry.file_size <= MAX_PAYLOAD_BYTES:
                raise ValueError("Tamano del paquete cifrado no permitido.")
            size = 0
            # La lectura hasta EOF comprueba la autenticacion AES y el CRC
            # cuando corresponde a la variante del formato WinZip AES.
            with protected.open(entry, pwd=password) as reader, payload.open("xb") as writer:
                while chunk := reader.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_PAYLOAD_BYTES:
                        raise ValueError("El paquete excede el limite permitido.")
                    digest.update(chunk)
                    writer.write(chunk)
            if size != entry.file_size:
                raise ValueError("El paquete recuperado esta incompleto.")
        if digest.hexdigest() != EXPECTED_SHA256:
            raise ValueError("SHA-256 incorrecto: no se extraera el contenido.")
        extracted = workspace / "contenido"
        extracted.mkdir()
        with zipfile.ZipFile(payload, "r") as archive:
            entries = _validated_members(archive)
            for entry in entries:
                target = extracted.joinpath(*PurePosixPath(entry.filename).parts)
                if entry.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer, length=1024 * 1024)
                mode = (entry.external_attr >> 16) & 0xFFFF
                target.chmod(0o700 if mode & 0o111 else 0o600)
        if not (extracted / EXPECTED_ROOT).is_dir():
            raise ValueError("No se encontro la carpeta raiz del paquete.")
        # mkdtemp reserva una carpeta nueva; nunca se reutiliza una salida previa.
        result = Path(tempfile.mkdtemp(prefix="Carlos-Agent-Recuperado-", dir=parent))
        try:
            (extracted / EXPECTED_ROOT).rename(result / EXPECTED_ROOT)
        except BaseException:
            shutil.rmtree(result)
            raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Recuperar localmente Carlos-Agent con AES-256 y SHA-256.")
    parser.add_argument("--destino", type=Path, help="Carpeta existente donde crear una salida nueva (por defecto, junto al repositorio).")
    args = parser.parse_args()
    if sys.version_info < (3, 12):
        parser.error("Se requiere Python 3.12 o posterior.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Contrasena del paquete (no se muestra): ").encode("utf-8")
        result = recuperar(password, destination_parent=args.destino)
        del password
    except (getpass.GetPassWarning, EOFError):
        print("ERROR: se requiere Terminal interactivo con entrada oculta. No pases la clave por argumentos ni variables de entorno.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperacion cancelada.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"No se recupero el paquete. Clave incorrecta, archivo alterado o error local: {exc}", file=sys.stderr)
        return 1
    print(f"AES y SHA-256 verificados. Archivos recuperados en:\n{result / EXPECTED_ROOT}")
    print("No se modificaron datos de una recuperacion anterior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
