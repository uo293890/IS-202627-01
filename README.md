# Ingeniería de Servicios

Repositorio de prácticas de laboratorio de `uo293890`. Cada sesión tiene su código y, cuando está preparada, una memoria con explicaciones, capturas y registros reales de ejecución.

## Prácticas

| Sesión | Contenido | Documentación |
| --- | --- | --- |
| [1.3](practicas/1-3) | Programación de red con Python y UDP | [Memoria](practicas/1-3/memoria/memoria.md) · [PDF](practicas/1-3/memoria/memoria.pdf) |
| [1.4](practicas/1-4) | Programación de red con Python y TCP | [Memoria](practicas/1-4/memoria/memoria.md) · [PDF](practicas/1-4/memoria/memoria.pdf) |
| [2.1](practicas/2-1) | Nginx, Flask, Gunicorn y MariaDB | [Memoria](practicas/2-1/memoria/memoria.md) · [PDF](practicas/2-1/memoria/memoria.pdf) |
| [2.2](practicas/2-2) | Aplicación web de amigos y API REST | [Memoria](practicas/2-2/memoria/memoria.md) · [PDF](practicas/2-2/memoria/memoria.pdf) |
| [2.3](practicas/2-3) | Aplicación de amigos y monitorización | Pendiente de documentar |
| [3](practicas/3) | FTP, SFTP, SSH y Telnet | Pendiente de documentar |
| [4](practicas/4) | DNS y correo electrónico | Pendiente de documentar |

## Organización

```text
practicas/
  1-3/  1-4/  2-1/  2-2/  2-3/  3/  4/
    codigo y configuracion de cada sesion
    memoria/
      memoria.md
      memoria.pdf
      capturas/
      evidencias/
archivo/
  capturas_previas/
docs/
  estructura.md
```

Las capturas antiguas que ya estaban en GitHub se conservan en [archivo/capturas_previas](archivo/capturas_previas). Las memorias nuevas utilizan las evidencias guardadas dentro de su propia práctica.

Los directorios de bases de datos, entornos virtuales y cachés son datos locales y se excluyen de Git. Las rutas antiguas de la raíz se sustituyen por `practicas/<sesion>`; consulta el [mapa de cambios](docs/estructura.md). Los ejemplos históricos que aparecen en memorias anteriores mantienen las rutas que se utilizaron al obtener sus capturas.
