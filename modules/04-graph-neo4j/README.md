# Paradigma de Grafos - Neo4j

## 1. Concepto y Filosofía
El modelo de grafos se basa en la teoría matemática de grafos, compuesta por **Nodos** (entidades), **Propiedades** (atributos clave-valor) y **Relaciones dirigidas y tipadas** (aristas de primer nivel). A diferencia de las bases relacionales que requieren operaciones JOIN costosas, los grafos implementan *index-free adjacency*, permitiendo recorrer relaciones en tiempo constante $O(1)$ por salto.

### ¿Cuándo usarlo?
- Redes sociales y recomendación de amigos/contactos ("Gente que quizás conozcas").
- Detección de fraude financiero (análisis de patrones circulares y cuentas mula).
- Gestión de dependencias en arquitecturas complejas (Service Mesh, Microservicios, Topología de Red).
- Motores de recomendación contextual ("Usuarios que compraron X también compraron Y").
- Knowledge Graphs e Inteligencia Artificial (Graph RAG).

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
