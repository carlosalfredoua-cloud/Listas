# Recuperar el paquete en la Mac

Este repositorio publico contiene un contenedor cifrado. La contrasena no esta incluida: introdúcela solo cuando Terminal la solicite, sin copiarla en comandos, archivos, chats publicos ni variables de entorno.

1. Descarga o clona la rama completa, conservando juntas `Carlos-Agent-Mac-Cifrado.zip`, `dependencias_descifrado` y `herramientas`.
2. Instala Python 3.12 si falta, mediante el instalador oficial macOS universal2 de [python.org](https://www.python.org/downloads/macos/). No se incluye el runtime ni se requiere Homebrew.
3. Abre `recuperar.command`. Si el doble clic no lo ejecuta, abre Terminal, escribe `bash `, arrastra el archivo a la ventana y pulsa Intro.
4. Introduce la contrasena cuando se solicite. Mientras escribes no aparecen caracteres.

El script crea `.venv-descifrado` localmente e instala las dos dependencias desde las ruedas incluidas, sin Internet, con hashes. Busca Python en PATH y en la ruta del instalador oficial. No cambia politicas ni permisos globales del Mac. Nunca instala claves ni solicita credenciales del buzon.

Primero comprueba AES-256 y la integridad del ZIP cifrado. Antes de extraer archivos, comprueba que el ZIP completo recuperado tenga SHA-256:

`d59d00d09430fafafe64d76564e40220227e68e509f180560fcb71edde7d1d61`

El contenido se extrae en una carpeta **nueva** `Carlos-Agent-Recuperado-...`, junto al repositorio, con su raiz `Carlos-Agent-Entrega/`. No se reemplazan recuperaciones anteriores. Si necesitas otra ubicacion, desde Terminal:

```bash
bash "/ruta/al/repositorio/herramientas/recuperar.command" --destino "/ruta/a/carpeta/existente"
```

La ubicacion debe existir y ser escribible. Los temporales se eliminan si la contrasena es incorrecta o falla la verificacion; no se conserva una salida parcial. Las rutas inseguras, enlaces simbolicos y archivos especiales del ZIP se rechazan. No se incluye una carpeta descifrada dentro del repositorio publico: no añadas los originales recuperados a Git.

Despues, abre las instrucciones de `Carlos-Agent-Entrega/`. La recuperacion no instala la aplicacion ni implementa las funciones pendientes de listas, OCR o Outlook. Tampoco concede control ni permisos sobre la Mac a otro agente. No se afirma ejecucion de estas herramientas en macOS desde el entorno Linux de preparacion; la validacion efectuada se describe por separado.
