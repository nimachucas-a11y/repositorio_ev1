# Microservicio Go - Evaluación DevOps

Proyecto desarrollado para la Evaluación Parcial N°1 de la asignatura Ingeniería DevOps.

El proyecto consiste en un microservicio simple desarrollado en Go, utilizado como base para aplicar control de versiones con Git, trabajo colaborativo mediante GitHub y automatización de pruebas mediante GitHub Actions.

## Tecnologías utilizadas

- Go
- Git
- GitHub
- GitHub Actions

## Estructura del proyecto

```text
repositorio_ev1/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── go.mod
│   ├── main.go
│   └── main_test.go
└── README.md
```

El código fuente del microservicio se encuentra dentro de `src/`.

## Ejecución del proyecto

Para ejecutar el microservicio:

```bash
cd src
go run .
```

El servidor se ejecuta localmente en:

```text
http://localhost:8080
```

## Endpoints

El microservicio contiene los siguientes endpoints:

### GET /health

Permite consultar el estado del servicio.

Ejemplo de respuesta:

```json
{
  "message": "service is running"
}
```

### GET /hello

Retorna un mensaje de bienvenida del microservicio.

### GET /version

Retorna la versión actual del servicio.

## Pruebas

El proyecto contiene pruebas automatizadas para verificar el funcionamiento de los endpoints.

Para ejecutarlas localmente:

```bash
cd src
go test ./...
```

Estas pruebas también son ejecutadas automáticamente mediante GitHub Actions.

---

# Estrategia de ramificación

Para el desarrollo del proyecto se utiliza una estrategia basada en GitFlow.

Las ramas principales son:

- `main`: contiene la versión estable del proyecto.
- `develop`: contiene los cambios que se encuentran en desarrollo e integración.
- `feature/*`: se utiliza para desarrollar nuevas funcionalidades.
- `hotfix/*`: se utiliza para realizar correcciones sobre errores detectados.

## Convención de nombres de ramas

Las ramas utilizan nombres descriptivos y el siguiente formato:

```text
feature/<nombre-de-funcionalidad>
hotfix/<nombre-de-correccion>
```

Durante el desarrollo se utilizaron ramas como:

```text
feature/agregar-endpoint-version
feature/agregar-tests
feature/configurar-ci
hotfix/corregir-mensaje-health
```

## Flujo para nuevas funcionalidades

Las funcionalidades parten desde `develop`.

```text
develop
   │
   └── feature/nombre
           │
           └── Pull Request
                    │
                    ▼
                 develop
```

Flujo utilizado:

1. Actualizar la rama `develop`.
2. Crear una rama `feature/*`.
3. Implementar el cambio.
4. Realizar los commits correspondientes.
5. Publicar la rama en GitHub.
6. Crear un Pull Request hacia `develop`.
7. Revisar los cambios.
8. Realizar el merge.

## Flujo para Hotfix

Los errores que requieren una corrección se trabajan mediante ramas `hotfix/*`.

```text
main
 │
 └── hotfix/nombre
          │
          └── Pull Request
                   │
                   ▼
                  main
```

Una vez aplicada una corrección, el cambio debe mantenerse sincronizado con la rama de desarrollo para evitar que el error vuelva a aparecer en versiones futuras.

---

# Convención de commits

Se utilizan mensajes de commit cortos y descriptivos.

Los principales prefijos utilizados son:

| Prefijo | Uso |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de errores |
| `test:` | Creación o modificación de pruebas |
| `ci:` | Cambios relacionados con integración continua |
| `docs:` | Cambios de documentación |

Ejemplos:

```text
feat: add version endpoint
fix: correct health endpoint message
test: add endpoint tests
ci: add GitHub Actions workflow
docs: update README
```

---

# Pull Requests y revisión

Los cambios desarrollados en ramas `feature/*` se integran a `develop` mediante Pull Requests.

Los cambios correspondientes a `hotfix/*` se integran mediante Pull Requests hacia `main`.

Antes de realizar un merge se revisan los cambios incluidos en el Pull Request para comprobar que correspondan a la funcionalidad o corrección desarrollada.

El uso de Pull Requests permite mantener un historial de los cambios realizados y facilita la trazabilidad del código.

---

# Integración continua

El proyecto utiliza GitHub Actions para automatizar la ejecución de pruebas.

El workflow se encuentra en:

```text
.github/workflows/ci.yml
```

El pipeline se ejecuta automáticamente cuando ocurre alguno de los siguientes eventos:

```text
push → develop
pull request → main
```

El flujo de CI realiza los siguientes pasos:

```text
Cambio en el repositorio
        │
        ▼
GitHub Actions
        │
        ▼
Checkout del código
        │
        ▼
Configuración de Go
        │
        ▼
go test ./...
        │
        ▼
Resultado del pipeline
```

Como el módulo Go se encuentra dentro de `src/`, las pruebas se ejecutan utilizando ese directorio como directorio de trabajo.

El objetivo del workflow es detectar automáticamente problemas en el código antes de integrar cambios importantes en la rama estable.

---

# Control de versiones

Git se utiliza para mantener la trazabilidad de los cambios realizados durante el desarrollo.

Cada funcionalidad o corrección se desarrolla de forma aislada en su propia rama y posteriormente se integra mediante Pull Requests.

Esto permite mantener un historial de:

- ramas utilizadas;
- commits realizados;
- funcionalidades agregadas;
- correcciones realizadas;
- Pull Requests;
- merges;
- ejecuciones de integración continua.

---

# Justificación de la estrategia de ramificación

Se utilizo la ramificacion adecuada para utilizar GitFlow, ya que esto permite que el proyecto sea mantenible en el tiempo y evita conflictos en produccion.
---

# Uso de Inteligencia Artificial

Se utiliza ChatGPT como herramienta de apoyo, de manera chatbot (no agentica) ya que me permitio ir paso a paso construyendo el repo, equivocandome en el camino y corrigiendo errores que siento que fue donde mas aprendi en esta ocasion.
