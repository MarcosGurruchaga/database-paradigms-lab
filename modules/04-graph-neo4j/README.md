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
- **Relaciones que se repiten entre nodos (Tipos de Aristas Reutilizables):**
  - **`:HIJO_DE` (Parentesco familiar repetido):**
    - `(Morty)-[:HIJO_DE]->(Beth)`
    - `(Morty)-[:HIJO_DE]->(Jerry)`
    - `(Summer)-[:HIJO_DE]->(Beth)`
    - `(Summer)-[:HIJO_DE]->(Jerry)`
    - `(Beth)-[:HIJO_DE]->(Rick)`
  - **`:NIETO_DE`:** `(Morty)-[:NIETO_DE]->(Rick)`, `(Summer)-[:NIETO_DE]->(Rick)`
  - **`:AMIGO_DE`:** `(Rick)-[:AMIGO_DE]->(Hombre Pajaro)`, `(Morty)-[:AMIGO_DE]->(Hombre Pajaro)`, `(Jerry)-[:AMIGO_DE]->(Mr Meeseeks)`
  - **`:ODIA_A`:** `(Jerry)-[:ODIA_A]->(Rick)`, `(Rick)-[:ODIA_A]->(Jerry)`, `(Evil Morty)-[:ODIA_A]->(Rick)`
  - **`:VIAJA_CON`:** `(Rick)-[:VIAJA_CON]->(Morty)`, `(Morty)-[:VIAJA_CON]->(Rick)`, `(Summer)-[:VIAJA_CON]->(Rick)`
  - **`:HERMANO_DE`:** `(Morty)-[:HERMANO_DE]->(Summer)`, `(Summer)-[:HERMANO_DE]->(Morty)`
  - **`:CASADA_CON` / `:CASADO_CON`:** `(Beth) <-> (Jerry)`
  - **Tragedia de Meeseeks:** `(Rick)-[:INVOCO_A]->(Meeseeks)`, `(Meeseeks)-[:QUIERE_ELIMINAR_A]->(Jerry)`

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

### B. Filtrar por la relacion repetida `:HIJO_DE` (Arbol Familiar)
```cypher
MATCH (hijo:Personaje)-[:HIJO_DE]->(padre:Personaje)
RETURN hijo.name AS descendiente, padre.name AS progenitor;
```

### C. Traversal de 2 saltos: Descubrir abuelos sin saber quien es el padre
```cypher
MATCH (nieto:Personaje)-[:HIJO_DE]->(:Personaje)-[:HIJO_DE]->(abuelo:Personaje)
RETURN nieto.name AS nieto, abuelo.name AS abuelo;
```

### D. ¿Quienes se odian mutuamente? (Relacion bidireccional `:ODIA_A`)
```cypher
MATCH (a:Personaje)-[:ODIA_A]->(b:Personaje)
RETURN a.name AS odiador, b.name AS odiado;
```

### E. Analizar el Conflicto Existencial de Mr Meeseeks con Jerry
```cypher
MATCH (m:Personaje {name: 'Mr Meeseeks'})-[r:QUIERE_ELIMINAR_A]->(j:Personaje {name: 'Jerry Smith'})
RETURN m.name, r.motivo, j.name;
```
