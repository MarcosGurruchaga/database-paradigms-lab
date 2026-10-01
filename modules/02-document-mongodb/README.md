## 1. Concepto Pedagogico: "Objetos que van mutando" (Schema Evolution)
El paradigma orientado a documentos almacena la informacion en formatos semi-estructurados como **JSON / BSON** (Binary JSON).

### ¿Por que triunfa con "Objetos que van mutando"?
En una base de datos relacional (SQL), si la aplicacion evoluciona y se agregan atributos, es obligatorio ejecutar un `ALTER TABLE` que bloquea la base de datos o deja columnas `NULL` vacias.
En MongoDB, **cada documento es polimorfico**: pueden convivir en la misma coleccion documentos de la version 1 (MVP simple), version 2 (con arreglos y telefonos) y version 3 (con suscripciones complejas y preferencias anidadas) sin migraciones forzadas.

### ¿Cuando usarlo?
- Entidades y catalogos cuyos atributos cambian frecuentemente entre sprints.
- Aplicaciones donde diferentes tipos de usuarios o productos tienen datos dispares.
- Modelos jerarquicos anidados (evita hacer 4 o 5 JOINs para armar una vista de perfil).

---

## 2. Configuración en el Laboratorio
- **Motor:** `MongoDB 7.0`
- **Puerto:** `27017`
- **Volumen local:** `./data/mongo`
- **Base de datos:** `lab_nosql`
- **Colección:** `developer_profiles`
- **Dashboard Web:** Mongo Express en [http://localhost:8081](http://localhost:8081)
  - Sin login básico requerido en modo laboratorio local.

---

## 3. Ejemplo de Estructura Documental
```json
{
  "_id": "66fb10a12e3...",
  "username": "mgurruchaga",
  "name": "Marcos Gurruchaga",
  "role": "Ayudante de Catedra & DevOps",
  "skills": ["Docker", "Kubernetes", "Python", "Neo4j", "PostgreSQL"],
  "experience_years": 4,
  "active_projects": [
    { "name": "Laboratorio Multi-Paradigma NoSQL", "tier": "educativo", "cloud": "Docker" }
  ],
  "settings": {
    "dark_mode": true,
    "notifications": { "slack": true, "email": false }
  }
}
```

### Consulta Flexible con Filtro por Arreglo:
```javascript
db.developer_profiles.find(
  { skills: { $all: ["Docker"] } },
  { name: 1, role: 1, skills: 1, active_projects: 1 }
);
```
