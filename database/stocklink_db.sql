-- StockLink - esquema de base de datos para la API FastAPI
-- Compatible con MySQL / TiDB.
-- Definición alineada con stocklink-api/models.py.
-- No incluye negocios, usuarios ni auditoría porque no existen en los modelos actuales.

CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    category VARCHAR(50),
    stock INT,
    minStock INT,
    price FLOAT,
    PRIMARY KEY (id),
    KEY ix_products_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sales (
    id INT NOT NULL AUTO_INCREMENT,
    total FLOAT,
    encargado VARCHAR(100),
    time DATETIME,
    PRIMARY KEY (id),
    KEY ix_sales_id (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sale_items (
    id INT NOT NULL AUTO_INCREMENT,
    sale_id INT,
    product_id INT,
    quantity INT,
    unit_price FLOAT,
    PRIMARY KEY (id),
    KEY ix_sale_items_id (id),
    KEY ix_sale_items_sale_id (sale_id),
    KEY ix_sale_items_product_id (product_id),
    CONSTRAINT fk_sale_items_sale
        FOREIGN KEY (sale_id) REFERENCES sales(id),
    CONSTRAINT fk_sale_items_product
        FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- main.py ejecuta Base.metadata.create_all(bind=engine) al iniciar.
-- Este script permite crear manualmente el mismo esquema en una base vacía.
