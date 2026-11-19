-- DATOS DE PRUEBA StockLink (MySQL / TiDB)
-- Ejemplos académicos; NO representan ventas históricas reales.
-- Ejecutar después de database/stocklink_db.sql.
-- Los identificadores explícitos mantienen las referencias de sale_items válidas.

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO products (id, code, name, category, stock, minStock, price) VALUES
(9001, 'TEST-001', 'Arroz 1 kg (prueba)', 'Abarrotes', 48, 10, 4200.00),
(9002, 'TEST-002', 'Aceite 1 L (prueba)', 'Abarrotes', 24, 5, 8900.00),
(9003, 'TEST-003', 'Jabón (prueba)', 'Aseo', 30, 8, 3500.00);

INSERT INTO sales (id, total, encargado, time) VALUES
(9001, 17300.00, 'encargado@stocklink.com [DATOS DE PRUEBA]', '2026-11-19 09:00:00');

INSERT INTO sale_items (id, sale_id, product_id, quantity, unit_price) VALUES
(9001, 9001, 9001, 2, 4200.00),
(9002, 9001, 9002, 1, 8900.00);

-- Comprobación referencial:
-- sale_items.sale_id -> sales.id (9001)
-- sale_items.product_id -> products.id (9001 y 9002)
