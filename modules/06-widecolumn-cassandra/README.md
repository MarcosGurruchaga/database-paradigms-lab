# Paradigma Familias de Columnas (Wide-Column) - Apache Cassandra

## 1. Concepto Pedagogico: ¿Cual es el beneficio EXACTO de Cassandra?
En las bases de datos relacionales tradicionales, la escala horizontal (agregar decenas de maquinas baratas en cluster) es dolorosa o imposible debido a la centralizacion de bloqueos transaccionales y los cuellos de botella del nodo maestro.

Apache Cassandra (basado en el paper de **Bigtable** de Google y la arquitectura **Dynamo** de Amazon) es una base de datos distribuida **Wide-Column** (familias de columnas) optimizada para **altisimos volumenes de escritura (High-Write Throughput) y Big Data masivo**.

### Las 4 Claves de su Arquitectura:
1. **Arquitectura Sin Maestro (Masterless P2P):** Todos los nodos del cluster son iguales (peer-to-peer). No existe un unico punto de falla ("Single Point of Failure"). Si un nodo cae, los demas atienden las lecturas y escrituras sin interrupcion mediante el protocolo Gossip.
2. **Escrituras Masivas Inmediatas (LSM-Tree):** Toda escritura se guarda secuencialmente en el `CommitLog` en disco y en la `MemTable` en memoria RAM en milisegundos ($O(1)$). No hay bloqueos de tablas ni indices pesados ralentizando la ingesta.
3. **Partition Key (Particionado Distribuido):** Define en que nodo especifico del cluster se almacena el dato mediante un algoritmo de hashing consistente (Murmur3). Permite distribuir petabytes de datos entre 50 o 500 servidores.
4. **Clustering Key (Orden Fisico en Disco):** Dentro de cada particion, las filas se almacenan **fisicamente ordenadas en disco** (en archivos inmutables llamados SSTables). Esto permite que consultar *"los ultimos 20 avistamientos del Distrito Shiganshina"* sea un seek secuencial instantaneo en disco, sin importar si la base tiene 500 millones de registros.

> **Regla de Oro en Cassandra:** En SQL se modela pensando en las entidades y relaciones, y luego se hacen `JOINs`. **En Cassandra NO existen los `JOINs`**: se modela estrictamente a partir de las preguntas/queries exactas que la aplicacion necesita responder (*Queries-First Design*).

---

## 2. Configuracion en el Laboratorio
- **Motor:** `Apache Cassandra 4.1`
- **Puerto CQL:** `9042`
- **Volumen local:** `./data/cassandra`
- **Keyspace:** `defensa_amestris`
- **Dashboard Web:** Cassandra Web en [http://localhost:8082](http://localhost:8082)
  - Visor interactivo para explorar keyspaces, tablas, tokens de particion y ejecutar consultas CQL.

---

## 3. Ejemplo Pedagogico: Red de Deteccion de Amenazas (Fullmetal Alchemist / Titanes)

### Definicion de la Tabla (Column Family)
```sql
CREATE KEYSPACE IF NOT EXISTS defensa_amestris
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS defensa_amestris.avistamientos_amenazas (
    distrito text,                      -- PARTITION KEY: Distribuye en el cluster
    fecha_registro timestamp,           -- CLUSTERING KEY: Ordena en disco
    id_avistamiento uuid,               -- CLUSTERING KEY: Desempata registros
    tipo_amenaza text,                  -- Titan Colosal, Acorazado, Quimera, Homunculo
    tamano_estimado_metros double,
    cantidad_avistada int,
    nivel_peligro text,                 -- ALTO, EXTREMO, APOCALIPTICO
    alquimista_o_comandante text,       -- Edward Elric, Roy Mustang, Levi Ackerman
    detalles_tacticos map<text, text>,  -- Wide-Column Sparse Map (columnas dinamicas)
    PRIMARY KEY ((distrito), fecha_registro, id_avistamiento)
) WITH CLUSTERING ORDER BY (fecha_registro DESC);
```

### Insercion de Eventos Masivos
```sql
INSERT INTO defensa_amestris.avistamientos_amenazas (
    distrito, fecha_registro, id_avistamiento, tipo_amenaza,
    tamano_estimado_metros, cantidad_avistada, nivel_peligro,
    alquimista_o_comandante, detalles_tacticos
) VALUES (
    'Distrito Shiganshina', toTimestamp(now()), uuid(), 'Titan Colosal',
    60.0, 1, 'APOCALIPTICO', 'Capitan Levi Ackerman',
    {'vulnerabilidad': 'Nuca posterior', 'clima': 'Tormenta de Vapor', 'orden': 'Evacuar'}
);
```

---

## 4. Consultas CQL para Mostrar en Clase

### A. Consulta Optima por Partition Key (Tiempo de respuesta < 2ms)
Cassandra consulta directamente la particion del nodo asignado al `Distrito Shiganshina` y lee las filas de disco ya ordenadas cronologicamente de forma descendente:
```sql
SELECT distrito, fecha_registro, tipo_amenaza, tamano_estimado_metros,
       cantidad_avistada, nivel_peligro, alquimista_o_comandante, detalles_tacticos
FROM defensa_amestris.avistamientos_amenazas
WHERE distrito = 'Distrito Shiganshina'
LIMIT 5;
```

### B. El "Anti-Patron" de Cassandra (Momento de Ensenanza)
Si intentas ejecutar:
```sql
SELECT * FROM defensa_amestris.avistamientos_amenazas 
WHERE alquimista_o_comandante = 'Edward Elric';
```
Cassandra arrojara un error `InvalidQueryException: Cannot execute this query without ALLOW FILTERING`.
**¿Por que?** Porque `alquimista_o_comandante` no es la Partition Key. Para responder eso, Cassandra tendria que preguntarle a TODOS los nodos del cluster y escanear todos los terabytes de disco (Full Scan distribuido). Cassandra protege al desarrollador de cometer este error en produccion.
