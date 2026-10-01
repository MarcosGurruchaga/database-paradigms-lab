# Diseño de Sistemas - Clase de Persistencia NoSQL y Políglota

Este repositorio contiene el laboratorio práctico local para la clase de **Persistencia NoSQL y Paradigmas de Bases de Datos** de la materia **Diseño de Sistemas**.

El objetivo es experimentar de forma visual e interactiva los principales paradigmas de persistencia que discutimos en la teoría, levantando cada motor en Docker junto a su visor web, y utilizando un script en Python para sembrar datos pedagógicos y divertidos basados en cultura pop.

---

## Paradigmas y Casos de Estudio

1. **Relacional (SQL) - PostgreSQL:** El punto de comparación tradicional. Tablas fijas, tipos estrictos, claves foráneas (`FOREIGN KEY`), transacciones y garantías ACID.
2. **Documental (NoSQL) - MongoDB *(Los Simpsons)*:** Demuestra el concepto de **objetos que van mutando (*Schema Evolution*)** y polimorfismo a lo largo de las temporadas sin necesidad de ejecutar migraciones de esquema (`ALTER TABLE`).
3. **Clave-Valor - Redis *(Death Note)*:** Acceso puntual por clave única en memoria RAM con latencia sub-milisegundo ($O(1)$), expiración automática con tiempo de vida (`TTL` de 40 segundos para el paro cardíaco), contadores atómicos y rankings en tiempo real (*Sorted Sets*).
4. **Grafos - Neo4j *(Rick y Morty)*:** Relaciones como ciudadanas de primer nivel (*index-free adjacency*). Recorrido del multiverso interdimensional, alianzas, hostilidad y consultas de conflicto existencial en tiempo constante por salto sin `JOINs` recursivos.
5. **Series Temporales - InfluxDB *(Harry Potter / Hogwarts)*:** Ingesta continua y análisis de telemetría a gran escala. Sensores mágicos comparando la actividad clandestina en la Torre de Gryffindor frente a la incursión de Dementores en las Mazmorras de Slytherin.
6. **Familias de Columnas (Wide-Column) - Apache Cassandra *(Fullmetal Alchemist / Titanes)*:** Big Data masivo de alta escritura (*High-Write Throughput*), arquitectura sin maestro (P2P), particionado distribuido (*Partition Key*) y ordenamiento físico en disco (*Clustering Key*) para registrar avistamientos militares por distrito.

---

## Requisitos previos

- **Docker Desktop** instalado y en ejecución.
- **Python 3.10+** (para ejecutar el script de sembrado y pruebas).

---

## Guía de Ejecución Rápida

### 1. Levantar los 6 motores y sus visores web
Abrir una terminal de PowerShell en la raíz del proyecto y ejecutar:

```powershell
docker compose up -d
```

Para verificar que los 10 contenedores levantaron y están saludables:
```powershell
docker compose ps
```

*(También pueden usar el script automatizado: `.\run.ps1 up`)*.

### 2. Cargar los datos de prueba (Seed)
El script `seed_and_demo.py` conecta a cada motor, inicializa los esquemas, carga los datos temáticos y ejecuta consultas analíticas en la terminal con tablas formateadas:

```powershell
# Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la demostracion de los 6 paradigmas
python seed_and_demo.py
```

*(O directamente con el helper: `.\run.ps1 seed`)*.

Si desean sembrar o consultar un solo motor puntual en clase:
```powershell
python seed_and_demo.py --engine mongodb
python seed_and_demo.py --engine redis
python seed_and_demo.py --engine neo4j
python seed_and_demo.py --engine influxdb
python seed_and_demo.py --engine cassandra
python seed_and_demo.py --engine postgres
```

---

## Interfaces Web de Gestión (Dashboards para proyectar en clase)

Cada motor cuenta con su propia interfaz gráfica mapeada en puertos locales para inspeccionar los datos en vivo:

| Paradigma / Motor | URL Local | Configuración / Credenciales | ¿Qué inspeccionar en la clase? |
| :--- | :--- | :--- | :--- |
| **1. SQL (PostgreSQL)** | [http://localhost:8080](http://localhost:8080) | Servidor: `postgres` \| Puerto: `5433` \| User: `postgres` \| Pass: `postgrespassword` \| DB: `lab_sql` | Adminer: Tablas `usuarios` y `pedidos`, claves foráneas y ejecución de JOINs. |
| **2. Documental (MongoDB)** | [http://localhost:8081](http://localhost:8081) | Acceso directo (Mongo Express) | Colección `ciudadanos_springfield`: Ver cómo conviven Homero v1 (plano), Marge v4 (arrays) y Homero v10 (alter-egos y ficha médica) sin `ALTER TABLE`. |
| **3. Clave-Valor (Redis)** | [http://localhost:5540](http://localhost:5540) | Host: `redis` \| Puerto: `6379` \| Pass: `redispassword` *(URL: `redis://default:redispassword@localhost:6379`)* | RedisInsight: Ver la víctima `kuro_otoishi` con su barra regresiva de **TTL (40s)**, el contador atómico de Kira y el ranking de sospechosos de L. |
| **4. Grafos (Neo4j)** | [http://localhost:7474](http://localhost:7474) | Conexión: `bolt://localhost:7687` \| User: `neo4j` \| Pass: `neo4jpassword` | Neo4j Browser: Grafo visual interactivo con `MATCH (p:Personaje) RETURN p`. Cada nodo tiene su nombre centrado en el círculo. |
| **5. Series de Tiempo (InfluxDB)** | [http://localhost:8086](http://localhost:8086) | User: `influxadmin` \| Pass: `influxpassword123` \| Org: `devops-lab` | Data Explorer: Graficar `presencia_dementores_pct` comparando la `Torre-Gryffindor` vs las `Mazmorras-Slytherin`. |
| **6. Wide-Column (Cassandra)** | [http://localhost:8082](http://localhost:8082) | Acceso directo (Cassandra Web) | Keyspace `defensa_amestris`, tabla `avistamientos_amenazas`. Inspeccionar el particionado distribuido y el orden cronológico en disco. |

> **Tip:** Ejecutando `.\run.ps1 open-dashboards` se abrirán automáticamente las 6 interfaces en pestañas de tu navegador.

---

## Casos de Estudio y Consultas Pedagógicas

### 1. Relacional - PostgreSQL (Cátedra Universitaria)
* **Concepto:** Tablas rígidas, tipos estrictos e integridad referencial (FK).
* **Consulta:** Agregación con `JOIN` y `GROUP BY` calculando pedidos vinculados:
```sql
SELECT u.nombre, u.categoria, COUNT(p.id) AS total_pedidos, COALESCE(SUM(p.precio), 0) AS total_gastado
FROM usuarios u
LEFT JOIN pedidos p ON u.id = p.usuario_id
GROUP BY u.id, u.nombre, u.categoria
ORDER BY total_gastado DESC;
```

### 2. Documental - MongoDB (`ciudadanos_springfield` - Los Simpsons)
* **Concepto:** *Schema Evolution* y polimorfismo.
* **Demostración:** En una base relacional, agregar hobbies o una lista de alter-egos exigiría crear 3 tablas intermedias y correr migraciones bloqueantes. En MongoDB conviven en el mismo documento:
  * **Temporada 1:** Homero básico con campos planos (`ocupacion`, `direccion_plana`).
  * **Temporada 4:** Marge con arrays (`hobbies`, `hijos`) y subdocumento `direccion`.
  * **Temporada 10+:** Homero multifacético con array de alter-egos (`Don Barredora`, `Cosme Fulanito`, `El Hombre Pie`, `Astronauta`), ficha médica con crayones en el cerebro y membresía a `Los Magios`.
```javascript
// Buscar personajes con alter-egos exitosos:
db.ciudadanos_springfield.find({ "alter_egos.exito": true });
```

### 3. Clave-Valor - Redis (Death Note)
* **Concepto:** Lecturas y escrituras puntuales $O(1)$ en memoria RAM con expiración automática.
* **Estructuras mostradas:**
  * **Hash con TTL de 40s:** `deathnote:victima:kuro_otoishi` (Regla: si no se aclara la causa en 40 segundos, muere de paro cardíaco). Se observa el contador de expiración en tiempo real.
  * **Strings directos:** `deathnote:regla:01` y `deathnote:regla:02` con las reglas de Ryuk.
  * **Contador atómico:** `kira:contador:criminales_eliminados` incrementado con `INCRBY` en nanosegundos sin locks.
  * **Sorted Set (ZSet):** `cuartel_l:probabilidad_ser_kira` con el ranking en vivo de probabilidades calculado por el Detective L (Light Yagami: 96.8%, Misa Amane: 88.5%).

### 4. Grafos - Neo4j (Rick y Morty)
* **Concepto:** Red de relaciones complejas. Las aristas son elementos de primer orden con atributos y dirección.
* **Modelado:** Cada nodo es un `:Personaje` con la propiedad `name` en primer lugar (`Rick Sanchez`, `Morty Smith`, `Jerry Smith`, `Hombre Pajaro`, `Mr Meeseeks`, `Evil Morty`).
* **Consultas Cypher para la clase:**
```cypher
// 1. Ver todo el multiverso conectado
MATCH (p:Personaje) RETURN p;

// 2. Traversal: ¿Por que Mr Meeseeks quiere eliminar a Jerry?
MATCH (m:Personaje {name: 'Mr Meeseeks'})-[r:QUIERE_ELIMINAR_A]->(j:Personaje {name: 'Jerry Smith'})
RETURN m.name, r.motivo, j.name;

// 3. Aliados y enemigos directos de Rick
MATCH (rick:Personaje {name: 'Rick Sanchez'})-[r]-(otro:Personaje)
RETURN otro.name AS personaje, type(r) AS relacion, otro.rol AS rol;
```

### 5. Series Temporales - InfluxDB (Harry Potter / Hogwarts)
* **Concepto:** Almacenamiento columnar y analítica continua sobre series temporales.
* **Demostración:** En el **Data Explorer** de InfluxDB, seleccionar el bucket `telemetry-bucket`, measurement `telemetria_hogwarts` y comparar las dos ubicaciones:
  * `Torre-Gryffindor`: Actividad clandestina del Ejército de Dumbledore practicando encantamientos (`hechizos_por_minuto` creciente y `energia_lumos_lux` alta).
  * `Mazmorras-Slytherin`: Actividad normal interrumpida por una alarma abrupta de **Dementores** patrullando (salto a más de 75% en `presencia_dementores_pct` y caída del brillo Lumos).

### 6. Wide-Column - Apache Cassandra (Fullmetal Alchemist / Titanes)
* **Concepto:** ¿Cuál es el beneficio exacto de Cassandra frente a SQL y Mongo?
  1. **High-Write Throughput masivo:** Arquitectura LSM-Tree (CommitLog + MemTable) que escribe en disco en milisegundos sin locks ni contención transaccional.
  2. **Partition Key (`distrito`):** Distribuye petabytes de datos en decenas de nodos de un cluster sin nodo maestro (*Masterless P2P*).
  3. **Clustering Key (`fecha_registro DESC`):** Guarda las filas **físicamente ordenadas en disco**. Consultar *"los últimos avistamientos del Distrito Shiganshina"* toma menos de 2 milisegundos mediante un único seek secuencial en disco.
  4. **Wide-Column Sparse Map (`detalles_tacticos`):** Almacena mapas de atributos dinámicos sin desperdiciar espacio en columnas `NULL`.
```sql
-- Consulta optima aprovechando el particionado y orden fisico en disco
SELECT distrito, fecha_registro, tipo_amenaza, tamano_estimado_metros,
       cantidad_avistada, nivel_peligro, alquimista_o_comandante, detalles_tacticos
FROM defensa_amestris.avistamientos_amenazas
WHERE distrito = 'Distrito Shiganshina'
LIMIT 5;
```

---

## Detener y Limpiar el Laboratorio

Para apagar los contenedores conservando los datos:
```powershell
docker compose down
# o: .\run.ps1 down
```

Para reiniciar el laboratorio completo a cero borrando los volúmenes persistidos en `./data`:
```powershell
.\run.ps1 clean
```

---
*Cátedra de Diseño de Sistemas - Guía práctica de persistencia políglota.*
