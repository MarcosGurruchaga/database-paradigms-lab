# Paradigma de Grafos - Neo4j (Rick y Morty)

## 1. Concepto Pedagogico: "Redes y Traversals de Relaciones Directas"
El modelo de grafos modela el mundo mediante **Nodos** (entidades como Personajes) y **Relaciones dirigidas** (aristas de primer nivel como `VIAJA_CON`, `AMIGO_DE`, `DESPRECIA_A`, `QUIERE_ELIMINAR_A`).

### ¿Por que triunfa frente a SQL?
En SQL, responder *"¿Quienes son los enemigos de mis amigos o que camino conecta a Rick con Jerry?"* requiere multiples `JOINs` costosos que degradan el motor.
En Neo4j (*index-free adjacency*), cada nodo contiene punteros en memoria RAM a sus vecinos directos, permitiendo navegar grafos enormes a velocidad constante $O(1)$ por salto.

---

## 2. Ejemplo Divertido para la Clase: Multiverso Rick y Morty
Los nodos representan a los personajes del universo de Rick y Morty, y la primera propiedad creada es estrictamente `name`:
- **Nodos:** `Rick Sanchez`, `Morty Smith`, `Summer Smith`, `Jerry Smith`, `Beth Smith`, `Hombre Pajaro`, `Evil Morty`, `Mr Meeseeks`.
- **Relaciones con propiedades:**
  - `(Rick)-[:VIAJA_CON {portales: 450}]->(Morty)`
  - `(Rick)-[:AMIGO_DE {lealtad: 'Extrema'}]->(Hombre Pajaro)`
  - `(Rick)-[:DESPRECIA_A {motivo: 'Incompetencia'}]->(Jerry)`
  - `(Rick)-[:INVOCO_A]->(Mr Meeseeks)`
  - `(Jerry)-[:PIDIO_AYUDA_A]->(Mr Meeseeks)`
  - `(Mr Meeseeks)-[:QUIERE_ELIMINAR_A {motivo: 'Existir es dolor'}]->(Jerry)`
  - `(Evil Morty)-[:ENEMIGO_MORTAL_DE]->(Rick)`

> **Nota Visual para la Clase:** Al usar `name` como primera propiedad de cada nodo, la interfaz de **Neo4j Browser** dibuja directamente el nombre del personaje en el centro del circulo sin mostrar IDs ni nombres extraños.

---

## 3. Configuracion en el Laboratorio
- **Motor:** `Neo4j 5.20 Community`
- **Puertos:** `7474` (HTTP Browser UI) y `7687` (Bolt)
- **Volumen local:** `./data/neo4j`
- **Dashboard Web:** Neo4j Browser en [http://localhost:7474](http://localhost:7474)
  - **Conexion:** `bolt://localhost:7687`
  - **Usuario:** `neo4j`
  - **Contrasena:** `neo4jpassword`

---

## 4. Consultas Cypher para Ejecutar en Vivo

### A. Ver todo el multiverso interconectado
```cypher
MATCH (p:Personaje) RETURN p;
```

### B. ¿Quienes viajan juntos por las dimensiones?
```cypher
MATCH p=()-[r:VIAJA_CON]->() RETURN p;
```

### C. Analizar el Conflicto Existencial de Mr Meeseeks con Jerry
```cypher
MATCH (m:Personaje {name: 'Mr Meeseeks'})-[r:QUIERE_ELIMINAR_A]->(j:Personaje {name: 'Jerry Smith'})
RETURN m.name, r.motivo, j.name;
```

### D. Red de conexiones directas de Rick Sanchez
```cypher
MATCH (rick:Personaje {name: 'Rick Sanchez'})-[r]-(otro:Personaje)
RETURN otro.name AS personaje, type(r) AS relacion, otro.dimension AS dimension;
```
