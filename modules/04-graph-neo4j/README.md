# Paradigma de Grafos - Neo4j (Mini Red Social)

## 1. Concepto Pedagogico: "La Mini Red Social"
El modelo de grafos modela el mundo real mediante **Nodos** (entidades como Personas) y **Relaciones dirigidas** (aristas de primer nivel como `AMIGO_DE`, `SIGUE_A`, `LE_GUSTA`, `ESTUDIA_CON`).

### ¿Por que usarlo en una Red Social?
En SQL, responder *"¿Quienes son los amigos de mis amigos que aun no conozco?"* requiere encadenar 3 o 4 `JOINs` costosos sobre tablas con millones de registros, degradando el rendimiento de la base de datos.
En Neo4j (*index-free adjacency*), cada nodo apunta directamente en memoria RAM a sus conexiones, permitiendo recorrer grafos de millones de personas en tiempo constante $O(1)$ por salto.

---

## 2. Configuracion en el Laboratorio
- **Motor:** `Neo4j 5.20 Community`
- **Puertos:** `7474` (HTTP Browser UI) y `7687` (Bolt)
- **Volumen local:** `./data/neo4j`
- **Dashboard Web:** Neo4j Browser en [http://localhost:7474](http://localhost:7474)
  - **Conexion:** `bolt://localhost:7687`
  - **Usuario:** `neo4j`
  - **Contrasena:** `neo4jpassword`

> **Nota Visual para la Clase:** En Neo4j Browser, cada circulo muestra por defecto la propiedad `name`. Al definir `{name: 'Marcos'}`, el nombre de cada persona aparece centrado en el circulo sin confusiones.

---

## 3. Consultas Cypher para la Clase en Vivo

### A. Ver toda la Red Social
```cypher
MATCH (p:Persona) RETURN p
```

### B. Ver las relaciones de amistad
```cypher
MATCH p=()-[r:AMIGO_DE]->() RETURN p
```

### C. Ver a quien le dio "Me Gusta" cada persona
```cypher
MATCH p=()-[r:LE_GUSTA]->() RETURN p
```

### D. Algoritmo de Sugerencia ("Amigos de mis amigos que no conozco")
```cypher
MATCH (yo:Persona {name: 'Marcos'})-[:AMIGO_DE]->(amigo:Persona)-[:AMIGO_DE]->(amigo_de_amigo:Persona)
WHERE NOT (yo)-[:AMIGO_DE]->(amigo_de_amigo) AND yo <> amigo_de_amigo
RETURN 
    amigo_de_amigo.name AS persona_recomendada,
    amigo_de_amigo.rol AS rol,
    amigo.name AS amigo_en_comun;
```
