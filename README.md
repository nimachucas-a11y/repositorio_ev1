# Microservicio Go - Evaluación Parcial 2

Proyecto de Ingeniería DevOps DOY0101. Reutiliza el microservicio de la evaluación anterior y configura pruebas, análisis de seguridad, contenedores y despliegue simulado en GitHub Actions.

Repositorio: [nimachucas-a11y/repositorio_ev1](https://github.com/nimachucas-a11y/repositorio_ev1).

La documentacion anterior se conserva como [archivo historico de la Evaluacion 1](docs/evaluacion1.md).

## Integrantes

- Integrante 1: **[Completar nombre]**.
- Integrante 2: **[Completar nombre]**.

## Aplicación y respuestas

El módulo está en `src/`, declara Go `1.26.1` y no tiene dependencias externas declaradas. El servidor escucha en el puerto `8080` y responde JSON:

| Ruta | Estado esperado | Respuesta esperada |
|---|---|---|
| `/health` | `200` | `{"message":"service is running"}` |
| `/hello` | `200` | `{"message":"hello from golang microservice"}` |
| `/version` | `200` | `{"message":"version 1.0.0"}` |

La respuesta de `/health` conserva la correccion ya publicada en `main`. No hay base de datos, login ni operaciones CRUD.

## Archivos principales

| Archivo | Contenido |
|---|---|
| `src/main.go` | Servidor y handlers HTTP |
| `src/main_test.go` | Pruebas de los tres handlers |
| `Dockerfile` | Compilación Go en una etapa e imagen final `scratch` con usuario no root |
| `compose.yaml` | Imagen, puertos, recursos y restricciones del contenedor |
| `.github/workflows/ci.yml` | Pruebas y Snyk Code en CI |
| `.github/workflows/deploy.yml` | Construcción Docker y despliegue simulado |
| `.github/dependabot.yml` | Revisión semanal de Go, Docker y GitHub Actions |

## Pruebas y controles

Cada prueba Go usa `httptest` y comprueba HTTP `200`, `Content-Type: application/json`, JSON válido y el mensaje de su ruta. No necesita iniciar un servidor externo.

Snyk Code analiza `src/` en la organización `nikopatrick`, identificada en el workflow por `e5f9abaf-af71-48d7-8c15-b8697f6c338b`. El token se obtiene desde un secreto de GitHub; no se almacena en el código.

En esta configuración, una prueba fallida, un hallazgo de Snyk Code o un error del análisis detiene el job. No se configuró `continue-on-error` ni un filtro de severidad.

Dependabot revisa semanalmente los ecosistemas `gomod` en `/src`, `docker` en `/` y `github-actions` en `/`. La configuración debe estar en la rama predeterminada de GitHub para activarse. Los PR de actualización no se fusionan automáticamente.

## Configuración necesaria en GitHub

En el repositorio:

1. En `Settings > Secrets and variables > Actions`, guardar el token de Snyk como secreto de repositorio `SNYK_TOKEN`.
2. En `Settings > Secrets and variables > Dependabot`, guardar también `SNYK_TOKEN` para que los PR de Dependabot puedan ejecutar el análisis. Los secretos de Actions y Dependabot son almacenes separados.
3. En la configuración de seguridad, habilitar o comprobar `Dependabot alerts` y `Dependabot security updates`.
4. Verificar que Actions esté habilitado y que el token tenga acceso a la organización de Snyk con Snyk Code activado. Renovarlo cuando venza.

No copiar tokens a archivos, logs ni capturas. Los PR desde forks no reciben los secretos normales de Actions; este proyecto no incorpora un mecanismo especial para esos PR.

## Flujo de integración continua

`Go CI` se activa con un push a `develop` o con un pull request dirigido a `main`.

1. Descarga el repositorio.
2. Prepara Go.
3. Ejecuta las pruebas desde `src/`.
4. Instala Snyk y ejecuta el análisis del código.

Un push a una rama de trabajo sin PR a `main` no activa este workflow con los eventos actuales.

## Despliegue simulado

`CD - Simulated deployment` se activa con un push a `main`, por ejemplo al fusionar un PR.

1. Registra el commit y la URL de ejecución.
2. Ejecuta pruebas y Snyk Code.
3. Valida la configuración Compose y construye la imagen `microservicio-usuarios:<SHA-del-commit>`.
4. Levanta dos réplicas con Compose usando la imagen construida, sin reconstruirla ni descargar otra.
5. Obtiene los puertos asignados, espera disponibilidad y comprueba las tres rutas en cada réplica.
6. Reúne evidencias y las publica como artifact.
7. Limpia los contenedores, incluso si hay fallos.

La aplicación corre temporalmente en el runner de GitHub. No queda un servidor público después del job. Este workflow reemplaza el envío anterior del ejecutable a EC2; los secretos AWS no se utilizan aquí.

## Compose y escalabilidad configurada

Compose utiliza `IMAGE_TAG`, con valor por defecto `local`; el workflow lo establece con el SHA del commit. La imagen final ejecuta el servicio con usuario no root.

Cada contenedor tiene un límite inicial de `0.50` CPU y `128m` de memoria, sistema de archivos de sólo lectura, capacidades eliminadas y restricción de nuevos privilegios. Estos límites no son una medición de carga ni una garantía de rendimiento.

Los puertos anfitriones se asignan dinámicamente y se publican sólo en `127.0.0.1`. El puerto interno continúa siendo `8080`. La publicación dinámica permite que dos réplicas convivan sin intentar ocupar el mismo puerto del runner.

El workflow inicia dos réplicas y comprueba ambas. Esto configura escalado manual mediante Compose; no incorpora balanceador ni escalado automático. El resultado efectivo se acredita con la ejecución y sus logs.

No hay healthcheck dentro de la imagen `scratch`; la disponibilidad y las respuestas se verifican desde el runner.

## Evidencias y trazabilidad

En `Actions`, abrir la ejecución de `CD - Simulated deployment` correspondiente al commit y descargar el artifact:

`simulated-deployment-<SHA-del-commit>`

Su contenido incluye:

- `deployment.txt`: commit, imagen y enlace a la ejecución.
- `tests.log`, `snyk.log` y `build.log`: resultados de los controles y construcción.
- `image.json`: identificación de la imagen construida.
- `endpoints.log`: verificaciones de las rutas desplegadas.
- `replicas.json`: identificación, direcciones y resultados de las dos réplicas.
- `containers.txt`, `containers.log` y `compose.yaml`: estado, logs y configuración usada.

Si un paso anterior falla, algunos archivos pueden no existir. La recolección y publicación de evidencias se intentan incluso ante fallos; la existencia de un artifact no significa que el pipeline haya pasado.

## Relación con la pauta

| Indicador | Implementación | Evidencia a comprobar |
|---|---|---|
| IE1: contenedores | `Dockerfile` y construcción en Actions | `build.log`, `image.json` |
| IE2: pruebas | Pruebas de handlers en CI y despliegue | Job exitoso y `tests.log` |
| IE3: seguridad y escalabilidad | Dependabot, Snyk Code, límites y réplicas | Configuración de seguridad, `snyk.log` y comprobaciones de las réplicas |
| IE4: despliegue y trazabilidad | Workflow simulado, etiqueta SHA y este README | Ejecución del mismo commit y artifact asociado |
| IE5: orquestación | Compose y dos réplicas en el despliegue | Estado de contenedores y respuestas de ambas instancias |

## Resultados verificados

El siguiente registro corresponde a una ejecución real de GitHub Actions del código integrado mediante el [PR #10](https://github.com/nimachucas-a11y/repositorio_ev1/pull/10). Es un checkpoint de evidencia; las actualizaciones posteriores de documentación tienen sus propios commits y ejecuciones.

- Commit desplegado: `d2f56999e48f94cea8a445b5673730f10fd04691`.
- [CI del PR](https://github.com/nimachucas-a11y/repositorio_ev1/actions/runs/41234098666): pruebas y Snyk Code aprobados.
- [Despliegue simulado 41234506100](https://github.com/nimachucas-a11y/repositorio_ev1/actions/runs/41234506100): ejecución exitosa, incluidos construcción, arranque, comprobaciones y limpieza.
- Imagen construida: `microservicio-usuarios:d2f56999e48f94cea8a445b5673730f10fd04691`.
- ID de imagen: `sha256:9141d20717dbb060dcd1a9ea2402881b7237504684ca1ac1a98d378f6d82c818`.
- Artifact descargado y revisado: `simulated-deployment-d2f56999e48f94cea8a445b5673730f10fd04691`, disponible en la ejecución enlazada.
- Snyk Code: `Total issues: 0` en esa ejecución; esto no garantiza ausencia de toda vulnerabilidad.
- Réplicas confirmadas: dos contenedores distintos, publicados en `127.0.0.1:32768` y `127.0.0.1:32769` durante ese job.
- Comprobaciones: seis respuestas HTTP `200`, con `application/json` y los mensajes esperados; `/health`, `/hello` y `/version` en cada réplica.

`replicas.json`, `endpoints.log`, `containers.txt` e `image.json` permiten comprobar estos resultados y su relación con el commit. Los puertos son temporales: no son direcciones de un servicio que siga disponible después del job.

Se confirmó que existe `SNYK_TOKEN` tanto en los secretos de Actions como en los de Dependabot, sin leer sus valores. `Dependabot alerts` y `Dependabot security updates` están habilitados y su estado se confirmó mediante la API de GitHub.

No se declara una cobertura porcentual. Antes de entregar, revisar también el estado de Actions correspondiente al commit final y completar los apartados propios del equipo.

## Declaración de uso de IA

Se utilizó Codex como apoyo para explicar conceptos y preparar el Dockerfile, las ampliaciones de pruebas, Compose, Dependabot, los workflows de GitHub Actions y esta documentación. También se consultó para interpretar resultados y errores de Snyk. El uso incluyó generación de código y configuración, no sólo corrección de redacción.

Referencia de la herramienta utilizada: [OpenAI Codex](https://openai.com/codex/).

La validación disponible y los resultados pendientes se distinguen en este README. Los integrantes deben revisar esta declaración y comprobar que describa su uso real de IA y las condiciones de la pauta.

## Justificaciones técnicas del equipo

**[Pendiente: redactar por el equipo, sin redacción de IA, conforme a la pauta.]**

## Conclusiones del equipo

**[Pendiente: redactar por el equipo, sin redacción de IA, conforme a la pauta.]**

### Reflexión individual - integrante 1

**[Pendiente: completar nombre y reflexión propia de aprendizaje y contribución, sin apoyo de IA.]**

### Reflexión individual - integrante 2

**[Pendiente: completar nombre y reflexión propia de aprendizaje y contribución, sin apoyo de IA.]**

## Entrega

Completar los apartados personales, verificar una ejecución exitosa del commit final y comprobar que el docente pueda acceder al repositorio. Entregar el enlace del repositorio en AVA y por correo docente dentro del plazo de la asignatura. La pauta no fija una fecha calendario en el documento ni exige un video o una lista concreta de capturas.

## Referencias técnicas

- [Docker: construcción multietapa](https://docs.docker.com/build/building/multi-stage/).
- [Docker Compose: servicios](https://docs.docker.com/reference/compose-file/services/).
- [Snyk: análisis de código con CLI](https://docs.snyk.io/developer-tools/snyk-cli/commands/code-test).
- [GitHub: opciones de Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference).
- [GitHub: secretos de Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).
- [Bibliotecas Duoc UC: guía de inteligencia artificial y citación](https://bibliotecas.duoc.cl/ia). Los integrantes deben completar la cita de su uso conforme a la guía y a las indicaciones de la asignatura.
