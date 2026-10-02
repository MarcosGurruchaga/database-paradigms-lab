# Paradigma Documental (NoSQL) - MongoDB

## 1. Concepto Pedagogico: "Objetos que van mutando" (Schema Evolution)
El paradigma orientado a documentos almacena la informacion en formatos semi-estructurados como **JSON / BSON** (Binary JSON).

### ¿Por que triunfa con "Objetos que van mutando"?
En una base de datos relacional (SQL), si la aplicacion evoluciona y se agregan atributos, es obligatorio ejecutar un `ALTER TABLE` que bloquea la base de datos o deja columnas `NULL` vacias.
En MongoDB, **cada documento es polimorfico**: pueden convivir en la misma coleccion documentos con atributos completamente dispares sin migraciones forzadas.

### Ejemplo Divertido para la Clase: Los Simpsons
A lo largo de las temporadas, distintos personajes de Springfield muestran niveles de complejidad totalmente diferentes sin romper la base:
- **Temporada 1 (MVP plano - Homero):** Estructura plana básica de los años 90 (`ocupacion`, `edad`, `frase_iconica: D'oh!`).
- **Temporada 4 (Evolución de esquema - Marge):** Subdocumentos anidados para su `direccion` y arrays para sus `hobbies` e `hijos` (`["Bart", "Lisa", "Maggie"]`).
- **Temporada 10+ (Polimorfismo extremo - Bart):** Lista de alter-egos (`El Barto`, `El Chico 'Yo No Fui'`, `Bartman`), subdocumento de `expediente_disciplinario_skinner` con arrays de castigos en la pizarra y campo dinámico `nemesis_mortal`.

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
// Documento 1: Estructura plana inicial (Temporada 1)
{
  "temporada_aparicion": 1,
  "nombre": "Homero J. Simpson",
  "edad": 39,
  "ocupacion": "Inspector de Seguridad del Sector 7G",
  "frase_iconica": "D'oh!"
}

// Documento 2: Estructura con arrays y subdocumentos (Temporada 4)
{
  "temporada_aparicion": 4,
  "nombre": "Marjorie Bouvier Simpson",
  "rol": "Ama de casa y Pacificadora",
  "hijos": ["Bart", "Lisa", "Maggie"],
  "direccion": {
    "calle": "Avenida Siempreviva 742",
    "ciudad": "Springfield"
  }
}

// Documento 3: Estructura polimorfica avanzada (Temporada 10+)
{
  "temporada_aparicion": 10,
  "nombre": "Bartholomew Jo-Jo Simpson",
  "apodo": "Bart",
  "edad": 10,
  "alter_egos": [
    { "nombre": "El Barto", "actividad": "Grafitero clandestino", "exito": true },
    { "nombre": "El Chico 'Yo No Fui'", "frase": "Yo no fui", "exito": true },
    { "nombre": "Bartman", "arma": "Resortera y capa", "exito": true }
  ],
  "expediente_disciplinario_skinner": {
    "detenciones_en_pizarra": 450,
    "frases_castigo_memorables": ["No instigare a la revolucion"]
  },
  "nemesis_mortal": "Bob Patino (Sideshow Bob)"
}
```

### Consultas Flexibles en Mongo Express o Mongo Shell:
```javascript
// Buscar personajes con alter-egos exitosos:
db.ciudadanos_springfield.find({ "alter_egos.exito": true });

// Buscar por atributos que solo existen en versiones avanzadas:
db.ciudadanos_springfield.find({ "expediente_disciplinario_skinner.detenciones_en_pizarra": { $gt: 100 } });
```
