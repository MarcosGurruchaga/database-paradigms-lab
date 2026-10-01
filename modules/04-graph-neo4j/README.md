# Paradigma de Grafos - Neo4j (Mini Red Social)

## 1. Concepto Pedagogico: "La Mini Red Social"
El modelo de grafos modela el mundo real mediante **Nodos** (entidades como Personas o Publicaciones) y **Relaciones dirigidas** (aristas como `AMIGO_DE`, `SIGUE_A`, `LE_GUSTA`).

### ¿Por que usarlo en una Red Social?
En SQL, responder "¿Quienes son los amigos de mis amigos que aun no conozco?" requiere encadenar 3 o 4 `JOINs` sobre millones de registros, degradando el rendimiento exponencialmente.
En Neo4j (*index-free adjacency*), cada nodo apunta directamente a sus vecinos en memoria RAM, permitiendo recorrer grafos de millones de personas en tiempo constante $O(1)$ por salto.

---

## 2. Configuración en el Laboratorio
- **Motor:** `Neo4j 5.20 Community`
- **Puertos:** `7474` (HTTP) y `7687` (Bolt)
- **Volumen local:** `./data/neo4j`
- **Dashboard Web:** Neo4j Browser nativo en [http://localhost:7474](http://localhost:7474)
  - **Conexión:** `bolt://localhost:7687`
  - **Usuario:** `neo4j`
  - **Contraseña:** `neo4jpassword`

---

## 3. Ejemplo Cypher Demostrado

### Creación de Nodos y Relaciones
```cypher
CREATE (devops:Team {name: 'DevOps & SRE', lead: 'Marcos Gurruchaga'})
CREATE (backend:Team {name: 'Core Platform', lead: 'Ana Gómez'})

CREATE (msAuth:Microservice {name: 'Auth-Service', tier: 'critical', language: 'Go'})
CREATE (msPayment:Microservice {name: 'Payment-Gateway', tier: 'critical', language: 'Java'})
CREATE (msWeb:Microservice {name: 'Web-Portal', tier: 'frontend', language: 'TypeScript'})

CREATE (backend)-[:OWNS_CODE]->(msAuth)
CREATE (msWeb)-[:DEPENDS_ON {protocol: 'gRPC'}]->(msPayment)
CREATE (msPayment)-[:DEPENDS_ON {protocol: 'gRPC'}]->(msAuth)
```

### Consulta de Impacto en Cascada
```cypher
MATCH (target:Microservice {name: 'Auth-Service'})<-[:DEPENDS_ON*1..2]-(affected:Microservice)
OPTIONAL MATCH (team:Team)-[:OWNS_CODE]->(affected)
RETURN DISTINCT affected.name AS service, affected.tier AS tier, team.name AS team
ORDER BY affected.tier DESC;
```
En el explorador visual de Neo4j en `http://localhost:7474`, puedes visualizar el grafo interactivo con nodos coloreados y arcos interactivos.
