# Estructura del repositorio

Cada práctica reúne sus fuentes, configuración y documentación. Se conserva la numeración de las sesiones y se normalizan las carpetas que antes utilizaban el prefijo `sesion`.

| Ruta anterior | Ruta actual |
| --- | --- |
| `1-3/` | `practicas/1-3/` |
| `1-4/` | `practicas/1-4/` |
| `2-1/` | `practicas/2-1/` |
| `2-2/` | `practicas/2-2/` |
| `sesion2-3/` | `practicas/2-3/` |
| `sesion3/` | `practicas/3/` |
| `sesion4/` | `practicas/4/` |
| `2-1/capturas/` | `archivo/capturas_previas/2-1/` |
| `2-2/capturas/` | `archivo/capturas_previas/2-2/` |
| `2-3/capturas/` | `archivo/capturas_previas/2-3/` |

La antigua carpeta `2-3` solo contenía capturas. Su código estaba en `sesion2-3` y ahora queda identificado como `practicas/2-3`.

## Trabajar desde la máquina virtual

```bash
cd ~/repositorio_practicas/practicas/2-1
```

Los scripts que usan `$(pwd)` deben ejecutarse desde la carpeta de la práctica correspondiente. Las carpetas `basedatos/` e `instance/` permanecen locales y no deben añadirse al índice de Git. No se eliminan los datos locales al reorganizar las sesiones.

En la VM se han dejado enlaces simbólicos locales desde las rutas anteriores hacia las nuevas carpetas. Se excluyen mediante `.git/info/exclude` y no duplican el contenido del repositorio. Sirven para conservar referencias de servicios y comandos anteriores mientras se utiliza la estructura nueva.

Los archivos `__pycache__`, `.pyc` y las bases SQLite generadas se retiran del seguimiento de versiones. La configuración local que ya necesitaba la aplicación se conserva. La limpieza del índice no reescribe el historial anterior.

## Memorias y evidencias

Las memorias nuevas están en `memoria/` dentro de la sesión. Sus capturas y registros corresponden a las pruebas indicadas en el documento. El archivo de capturas previas se mantiene como material histórico y no se utiliza para sustituir ejecuciones nuevas.

Las memorias ya publicadas de UDP y TCP describen las rutas utilizadas en aquellas ejecuciones. Para lanzar sus verificadores después de la reorganización hay que entrar en `practicas/1-3` o `practicas/1-4` respectivamente.
