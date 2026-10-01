# Paradigma Documental (NoSQL) - MongoDB

## 1. Concepto y Filosofía
El paradigma orientado a documentos almacena la información en formatos semi-estructurados como **JSON / BSON** (Binary JSON). Cada documento es una entidad auto-contenida con su propio esquema dinámico (Schema-less o Schema-flexible).

### ¿Cuándo usarlo?
- Catálogos de productos con atributos variables (ropa con talles y colores vs electrodomésticos con voltaje).
- Gestión de contenido (CMS), blogs, perfiles de usuario enriquecidos.
- Aplicaciones ágiles con esquemas que evolucionan rápidamente en sprints.
- Alta velocidad de lectura/escritura horizontal mediante sharding.

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
  "role": "DevOps Engineer",
  "skills": ["Docker", "Kubernetes", "Python", "Terraform", "PostgreSQL"],
  "experience_years": 6,
  "active_projects": [
    { "name": "Infrastructure Modernization", "tier": "mission-critical", "cloud": "AWS" },
    { "name": "NoSQL Database Lab", "tier": "internal", "cloud": "Hybrid" }
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
