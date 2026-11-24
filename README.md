# FixTool — inventario y ventas

Aplicación web para administrar productos y registrar ventas de una tienda de herramientas. El frontend está hecho con Angular y Tailwind CSS; la API usa FastAPI y SQLAlchemy; los datos se guardan en PostgreSQL de Neon.

## Qué incluye

- Inicio de sesión con cuentas para administrador y vendedor.
- Panel administrativo con productos activos, alertas por stock mínimo e ingresos del día.
- Registro y edición de productos con SKU, categoría, costo, precio de venta y stock.
- Alta de cuentas de vendedor desde el panel del administrador.
- Punto de venta con efectivo, tarjeta, Yape, Plin y transferencia; calcula el vuelto.
- Registro de cada cobro y descuento transaccional de existencias. La API bloquea las filas de producto durante el cobro para evitar vender stock que ya se agotó.
- Historial de ventas disponible para el administrador.
- SQL inicial para Neon, configuración para Vercel y ejemplo de variables para Render.

## Estructura

```text
backend/               API FastAPI y configuración local
frontend/              aplicación Angular + Tailwind
sql/neon_schema.sql    esquema para ejecutar en Neon
```

## 1. Crear la base de datos en Neon

1. Crea un proyecto PostgreSQL en Neon.
2. Abre **SQL Editor** y ejecuta todo el contenido de `sql/neon_schema.sql`.
3. En **Connect**, selecciona la opción de parámetros individuales y copia host, base de datos, usuario, contraseña y puerto.

La aplicación no necesita una URL de conexión completa. En local, crea el archivo copiando el ejemplo:

```bash
cd backend
cp .env.example .env
```

Edita `backend/.env` y completa estos parámetros:

```dotenv
PGHOST=host-de-neon
PGDATABASE=nombre-de-base
PGUSER=usuario-neon
PGPASSWORD=contraseña-neon
PGPORT=5432
PGSSLMODE=require
```

El archivo que contiene las credenciales es **`backend/.env`**. No lo subas a GitHub. El ejemplo seguro para copiar es `backend/.env.example`.

## 2. Ejecutar la API en local

Se recomienda Python 3.11 o 3.12.

```bash
cd backend
python -m venv .venv
```

Activa el entorno virtual:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Instala dependencias, configura `backend/.env` y crea el primer administrador:

```bash
pip install -r requirements.txt
python -m app.cli create-admin
uvicorn app.main:app --reload
```

La API local queda en `http://localhost:8000`; la documentación interactiva está en `http://localhost:8000/docs` y el estado en `http://localhost:8000/health`.

El comando del administrador solicita usuario, nombre y contraseña en la terminal. No hay una cuenta predeterminada. Después de ingresar como administrador, crea las cuentas del personal en **Personal**.

## 3. Ejecutar Angular en local

Se recomienda Node.js 20.19 o superior, 22.12 o superior, o 24.

```bash
cd frontend
npm install
npm start
```

Abre `http://localhost:4200`. La dirección local de la API está en `frontend/src/environments/environment.ts`.

## Despliegue

### Render — backend

1. Crea un servicio web conectado al repositorio de GitHub.
2. Configura **Root Directory** como `backend`.
3. Usa `pip install -r requirements.txt` como comando de build.
4. Usa `uvicorn app.main:app --host 0.0.0.0 --port $PORT` como comando de inicio.
5. Añade en las variables de entorno de Render los valores `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT`, `PGSSLMODE=require`, `JWT_SECRET_KEY` y `APP_TIMEZONE=America/Lima`.
6. En `CORS_ORIGINS`, coloca el origen de Vercel, por ejemplo `https://fixtool.vercel.app`, sin una barra final. Para usar el origen local durante desarrollo, añade `http://localhost:4200` separado por coma.
7. Genera una clave JWT distinta para producción, por ejemplo con `openssl rand -hex 32`.

### Vercel — frontend

1. Importa el repositorio y selecciona `frontend` como **Root Directory**.
2. Usa `npm run build` como comando de build.
3. Usa `dist/fixtool/browser` como directorio de salida.
4. Antes del despliegue, reemplaza `https://YOUR-FIXTOOL-API.onrender.com/api/v1` en `frontend/src/environments/environment.prod.ts` con la URL pública real de Render seguida de `/api/v1`.
5. `frontend/vercel.json` incluye la regla para que las rutas de Angular funcionen al recargar la página.

Si cambias el archivo de entorno de producción, vuelve a desplegar el frontend.

## Subir el proyecto a GitHub

Desde la carpeta raíz del proyecto, crea un repositorio vacío en GitHub y ejecuta:

```bash
git init
git add .
git commit -m "Crear sistema FixTool"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```

El `.gitignore` excluye `backend/.env`, los entornos virtuales, `node_modules` y archivos generados.

## Reglas principales de acceso

| Función | Administrador | Vendedor |
|---|---:|---:|
| Dashboard y resumen | Sí | No |
| Crear, editar y retirar productos | Sí | No |
| Crear cuentas de vendedores | Sí | No |
| Consultar catálogo para vender | Sí | Sí |
| Registrar venta y pago | Sí | Sí |
| Consultar historial | Todas las ventas | No |

La interfaz muestra u oculta opciones según el rol, y la API vuelve a validar los permisos; el control de acceso no depende solo del frontend. El vendedor solo entra al punto de venta.

## Notas

- Los importes se guardan con dos decimales y los precios usados en cada venta quedan copiados en el detalle histórico.
- Los productos se retiran del catálogo con baja lógica para conservar la trazabilidad de ventas anteriores.
- El día del dashboard se calcula con `APP_TIMEZONE`, configurado por defecto en `America/Lima`.
- La sesión frontend se conserva en `localStorage` y el token vence según `JWT_ACCESS_TOKEN_MINUTES` (8 horas por defecto).

