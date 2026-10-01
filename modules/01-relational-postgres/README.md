# Paradigma Relacional (SQL) - PostgreSQL

## 1. Concepto y Filosofía
El paradigma relacional organiza la información en **tablas** compuestas por filas (tuplas) y columnas (atributos) estrictamente tipadas. Se basa en el álgebra relacional y garantiza las propiedades **ACID** (Atomicidad, Consistencia, Aislamiento y Durabilidad).

### ¿Cuándo usarlo?
- Datos estructurados con relaciones bien definidas y relaciones Many-to-Many / One-to-Many.
- Transacciones financieras, contabilidad, ERP, sistemas de facturación y comercio electrónico.
- Cuando se requiere estricta integridad referencial y prevención de datos huérfanos (`FOREIGN KEY`, `UNIQUE`, `NOT NULL`).

---

## 2. Configuracion en el Laboratorio
- **Motor:** `PostgreSQL 16 Alpine`
- **Puerto Host:** `5433` (mapeado a `5432` interno para evitar conflictos con PostgreSQL local)
- **Volumen local:** `./data/postgres`
- **Base de datos:** `lab_sql`
- **Dashboard Web:** Adminer en [http://localhost:8080](http://localhost:8080)
  - **Sistema:** PostgreSQL
  - **Servidor:** `postgres`
  - **Usuario:** `postgres`
  - **Contrasena:** `postgrespassword`
  - **Base de datos:** `lab_sql`

---

## 3. Modelo de Datos del Ejemplo
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product VARCHAR(100) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(30) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Consulta de agregación analítica (JOIN + SUM)
```sql
SELECT 
    u.id,
    u.name,
    u.role,
    COUNT(o.id) AS total_orders,
    COALESCE(SUM(o.amount), 0) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name, u.role
ORDER BY total_spent DESC;
```
