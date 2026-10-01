# Paradigma Documental (NoSQL) - MongoDB

## 1. Concepto Pedagogico: "Objetos que van mutando" (Schema Evolution)
El paradigma orientado a documentos almacena la informacion en formatos semi-estructurados como **JSON / BSON** (Binary JSON).

### ¿Por que triunfa con "Objetos que van mutando"?
En una base de datos relacional (SQL), si la aplicacion evoluciona y se agregan atributos, es obligatorio ejecutar un `ALTER TABLE` que bloquea la base de datos o deja columnas `NULL` vacias.
En MongoDB, **cada documento es polimorfico**: pueden convivir en la misma coleccion documentos con atributos completamente dispares sin migraciones forzadas.

### Ejemplo Divertido para la Clase: Los Simpsons
A lo largo de las temporadas, los personajes van sumando vidas paralelas, facetas y datos medicos:
- **Temporada 1 (MVP plano):** Homero basico de los 90s con campos planos (`ocupacion`, `edad`, `frase_iconica`).
- **Temporada 4 (Evolucion de esquema):** Marge con subdocumentos anidados para su direccion y arreglos para sus hobbies e hijos (`["Bart", "Lisa", "Maggie"]`).
- **Temporada 10+ (Polimorfismo extremo):** Homero con una lista de alter-egos (`Don Barredora`, `Cosme Fulanito`, `El Hombre Pie`, `Astronauta`), ficha medica con crayones en el cerebro y membresia a `Los Magios`.

---

## 2. Configuracion en el Laboratorio
- **Motor:** `MongoDB 7.0`
- **Puerto:** `27017`
- **Volumen local:** `./data/mongo`
- **Base de datos:** `lab_nosql`
- **Coleccion:** `ciudadanos_springfield`
- **Dashboard Web:** Mongo Express en [http://localhost:8081](http://localhost:8081)
  - Acceso directo sin login basico en entorno local.

---

## 3. Ejemplo de Estructuras Polimorficas en una Misma Coleccion
```json
// Documento 1: Estructura simple (Temporada 1)
{
  "temporada_aparicion": 1,
  "nombre": "Homero J. Simpson",
  "edad": 39,
  "ocupacion": "Inspector de Seguridad del Sector 7G",
  "frase_iconica": "D'oh!"
}

// Documento 2: Estructura polimorfica avanzada (Temporada 10+)
{
  "temporada_aparicion": 10,
  "nombre": "Homero J. Simpson",
  "alter_egos": [
    { "nombre": "Don Barredora", "vehiculo": "Camion con pala", "exito": true },
    { "nombre": "Cosme Fulanito", "disfraz": "Bigote y galera", "exito": false },
    { "nombre": "El Hombre Pie", "arma": "Pasteles de crema", "exito": true }
  ],
  "ficha_medica_dr_hibbert": {
    "crayones_en_el_cerebro": 1,
    "infartos_superados": 3
  },
  "membresias": ["Club de los Magios (Numero 908)"]
}
```

### Consultas Flexibles en Mongo Express o Mongo Shell:
```javascript
// Buscar personajes con alter-egos exitosos:
db.ciudadanos_springfield.find({ "alter_egos.exito": true });

// Buscar por atributos que solo existen en versiones avanzadas:
db.ciudadanos_springfield.find({ "ficha_medica_dr_hibbert.crayones_en_el_cerebro": { $gt: 0 } });
```
