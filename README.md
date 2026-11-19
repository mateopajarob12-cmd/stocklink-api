# StockLink — API (FastAPI)

API REST de StockLink: autenticación JWT, productos y ventas con validación de stock, sobre MySQL/TiDB. Desplegada en Render.
Cliente: [`stocklink`](https://github.com/mateopajarob12-cmd/stocklink) (app Flutter).

- **Documentación interactiva:** https://stocklink-api-x46s.onrender.com/docs

## Endpoints

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| POST | `/api/login` | Devuelve el token JWT (2 h) y el rol | Público |
| GET | `/api/products` | Lista de productos | Token |
| POST | `/api/products` | Crea un producto | Token |
| POST | `/api/sales` | Registra una venta; valida **todo** el stock antes de descontar y confirma en una transacción | Token |
| GET | `/api/sales` | Lista de ventas | Solo propietario |

## Instalación local

Requiere Python 3.10+.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Crear un archivo `.env`:

```dotenv
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=stocklink
```

Para TiDB Cloud usa su host y `DB_PORT=4000` (el código activa SSL cuando el host no es local). Si no defines `DB_PORT`, el valor por defecto es 4000.

```bash
uvicorn main:app --reload
```

Al iniciar, `Base.metadata.create_all` crea las tablas. También puedes usar los scripts de `database/`.

## Base de datos

- `database/stocklink_db.sql`: tablas `products`, `sales` y `sale_items` con sus llaves foráneas.
- `database/seed_test_data.sql`: datos de prueba opcionales (3 productos, 1 venta). Ejecutar una sola vez.

## Usuarios de demostración

| Rol | Correo | Contraseña |
|---|---|---|
| Propietario | `propietario@stocklink.com` | `123` |
| Encargado | `encargado@stocklink.com` | `123` |

## Estructura

```
main.py            # Endpoints, JWT y lógica de ventas
models.py          # Modelos SQLAlchemy: Product, Sale, SaleItem
database.py        # Conexión y sesión (lee .env, SSL en remoto)
database/          # Scripts SQL
requirements.txt
```

## Limitaciones conocidas

Usuarios, contraseña y clave JWT fijos en el código; CORS abierto; sin aislamiento por negocio. Es de demostración académica (ver SRS v2.0).
