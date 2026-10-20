# Entrega cifrada de Carlos-Agent para Mac

Esta rama contiene el **paquete completo cifrado** para continuar el proyecto en una Mac independiente. La contraseña se entrega por separado; no está en GitHub.

## Descargar desde GitHub

1. Mantén seleccionada la rama **`entrega-caguamin`**.
2. Presiona **Code → Download ZIP** y extrae esa descarga de GitHub.
3. Conserva juntos `Carlos-Agent-Mac-Cifrado.zip`, `dependencias_descifrado/` y `herramientas/`.

La descarga de GitHub incluye las herramientas para abrir el archivo cifrado. No intentes abrir ese archivo directamente con Finder: el formato AES requiere la herramienta incluida.

## Abrirlo en la Mac

1. Si falta Python 3.12, instala la distribución oficial macOS universal2 desde [python.org](https://www.python.org/downloads/release/python-31210/). La Mac tendrá Internet; no necesita Homebrew ni acceso al repositorio para los archivos ya descargados.
2. Abre `herramientas/recuperar.command`. Si el doble clic no lo ejecuta, abre Terminal, escribe `bash `, arrastra ese archivo a Terminal y pulsa Intro.
3. Introduce la contraseña que te entregue la persona que comparte el paquete. Al escribir no se muestran caracteres.
4. Al terminar, la herramienta mostrará la ubicación de una carpeta nueva **`Carlos-Agent-Recuperado-.../Carlos-Agent-Entrega/`**. Ábrela y empieza por `LEEME_PRIMERO.md` y `MENSAJE_PARA_CAGUAMIN.txt`.

La herramienta instala sus dependencias desde las ruedas incluidas para Mac Intel y Apple Silicon, verifica AES-256 y SHA-256, y recupera los archivos sin reemplazar una recuperación anterior. Consulta `herramientas/README.md` para más detalles.

## Qué se recupera

- **Los cinco documentos originales completos**, incluido el Excel original.
- Código fuente e historial Git del proyecto.
- Manual para Caguamin, decisiones, plan de desarrollo y pruebas de aceptación.
- Catálogo de sedes, plantillas y análisis documental.
- Dependencias y herramientas de preparación de la base.

En total se recuperan **185 archivos**, con manifiesto de integridad. Este contenedor protege el ZIP completo como un único payload para no publicar los nombres ni el contenido de sus documentos interiores.

El alcance del proyecto es **listas de asistencia primero; nómina después**. El programa base está incluido, y el manual distingue lo existente del OCR, conector Outlook y módulo de listas que aún deben implementarse. La recuperación no conecta Outlook ni concede permisos de control de la Mac.

## Comprobaciones

Se probó en Linux la recuperación completa, igualdad del SHA-256 y manifiesto interior, y rechazo de contraseña incorrecta sin dejar datos parciales. Las dependencias del descifrado se resolvieron para ambas arquitecturas de Mac; la ejecución de macOS/Finder debe comprobarse en destino.

La contraseña y los archivos descifrados deben permanecer fuera de este repositorio público. La salida predeterminada se crea fuera de él. La rama `main` del programa no se modifica con esta entrega.
