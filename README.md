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

## Estructura

```text
backend/               API FastAPI y configuración local
frontend/              aplicación Angular + Tailwind
```

