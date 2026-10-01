# Paradigma Relacional (SQL) - PostgreSQL

## 1. Concepto y Filosofia
El paradigma relacional organiza la informacion en **tablas** compuestas por filas (tuplas) y columnas (atributos) estrictamente tipadas. Se basa en el algebra relacional y garantiza las propiedades **ACID** (Atomicidad, Consistencia, Aislamiento y Durabilidad).

### ¿Cuando usarlo?
- Datos estructurados con relaciones bien definidas y relaciones One-to-Many / Many-to-Many.
- Transacciones financieras, contabilidad, ERP, sistemas de facturacion y cobros.
- Cuando se requiere estricta integridad referencial y prevencion de datos huerfanos (`FOREIGN KEY`, `UNIQUE`, `NOT NULL`).

---

## 2. Configuracion en el Laboratorio
- **Motor:** `PostgreSQL 16 Alpine`
- **Puerto Host:** `5433` (mapeado a `5432` interno para evitar conflictos con servicios PostgreSQL locales)
- **Volumen local:** `./data/postgres`
- **Base de datos:** `lab_sql`
- **Dashboard Web:** Adminer en [http://localhost:8080](http://localhost:8080)
  - **Sistema:** PostgreSQL
  - **Servidor:** `postgres`
  - **Usuario:** `postgres`
  - **Contrasena:** `postgrespassword`
  - **Base de datos:** `lab_sql`

---

## 3. Modelo de Datos del Laboratorio
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    categoria VARCHAR(50) DEFAULT 'Estudiante',
    creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    producto VARCHAR(100) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(30) DEFAULT 'completado',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Consulta de Agregacion Analitica (JOIN + GROUP BY)
```sql
SELECT 
    u.id,
    u.nombre,
    u.categoria,
    COUNT(p.id) AS total_pedidos,
    COALESCE(SUM(p.precio), 0) AS total_gastado
FROM usuarios u
LEFT JOIN pedidos p ON u.id = p.usuario_id
GROUP BY u.id, u.nombre, u.categoria
ORDER BY total_gastado DESC;
```
