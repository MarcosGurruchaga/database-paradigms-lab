# Diseño de Sistemas - Clase de Persistencia NoSQL y Políglota

Este repositorio contiene el laboratorio práctico para la clase de **Persistencia NoSQL** de la materia **Diseño de Sistemas**.

El objetivo es ver en funcionamiento los distintos paradigmas de bases de datos que discutimos en la teoría, levantando cada motor en Docker y usando un script en Python para sembrar datos de prueba y ejecutar consultas típicas.

---

## Paradigmas que vemos en la clase

1. **Relacional (SQL) - PostgreSQL:** El punto de comparación tradicional. Tablas fijas, tipos estrictos, claves foráneas y garantías ACID.
2. **Documental - MongoDB:** Útil cuando las entidades mutan rápido en el tiempo (*schema evolution* o polimorfismo) sin necesidad de correr migraciones de esquema (`ALTER TABLE`).
3. **Clave-Valor - Redis:** Acceso puntual por clave en memoria RAM con latencia sub-milisegundo ($O(1)$) para sesiones, flags globales y contadores atómicos.
4. **Grafos - Neo4j:** Relaciones como ciudadanas de primer nivel. Permite recorrer redes y conexiones complejas (redes sociales, recomendaciones) sin el costo de encadenar múltiples `JOINs`.
5. **Series Temporales / Columnar - InfluxDB:** Almacenamiento optimizado para grandes volúmenes de métricas en el tiempo. Demuestra el enfoque analítico columnar similar al que usan herramientas como BigQuery o ClickHouse.

---

## Requisitos previos

- **Docker Desktop** instalado y en ejecución.
- **Python 3.10+** (para ejecutar el script de prueba).

---

## Guía de Ejecución Rápida

### 1. Levantar los servicios
Abrir una terminal de PowerShell en la raíz del proyecto y ejecutar:

```powershell
docker compose up -d
```

Para verificar que todos los contenedores levantaron correctamente:
```powershell
docker compose ps
```

*(Nota: también pueden usar el script helper: `.\run.ps1 up`)*.

### 2. Cargar los datos de prueba (Seed)
El script `seed_and_demo.py` conecta a cada motor, inicializa los esquemas, carga datos representativos y ejecuta consultas de prueba:

```powershell
# Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias necesarias
pip install -r requirements.txt

# Ejecutar la demostración completa
python seed_and_demo.py
```

*(O directamente con el helper: `.\run.ps1 seed`)*.

Si quieren probar un solo motor puntual:
```powershell
python seed_and_demo.py --engine mongodb
python seed_and_demo.py --engine neo4j
python seed_and_demo.py --engine redis
```

---

## Interfaces Web de Gestión (Para ver en clase)

Cada servicio incluye una interfaz gráfica para inspeccionar los datos directamente desde el navegador:

| Motor | URL Local | Configuración / Credenciales | ¿Qué mirar en clase? |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | [http://localhost:8080](http://localhost:8080) | Servidor: `postgres` \| Puerto Host: `5433` \| User: `postgres` \| Pass: `postgrespassword` \| DB: `lab_sql` | Tablas `usuarios` y `pedidos` con integridad referencial (FK). |
| **MongoDB** | [http://localhost:8081](http://localhost:8081) | Acceso directo (sin clave en local) | Colección `usuarios_evolutivos`: ver cómo conviven documentos de distintas versiones (v1, v2 y v3) con diferentes campos en la misma colección. |
| **Redis** | [http://localhost:5540](http://localhost:5540) | Host: `redis` \| Pass: `redispassword` *(URL: `redis://default:redispassword@redis:6379`)* | Hashes de sesión con TTL (expiración), contadores atómicos y listas. |
| **Neo4j** | [http://localhost:7474](http://localhost:7474) | Conexión: `bolt://localhost:7687` \| User: `neo4j` \| Pass: `neo4jpassword` | Red social de personas: ejecutar `MATCH (p:Persona) RETURN p` para ver el grafo visual interactivo. |
| **InfluxDB** | [http://localhost:8086](http://localhost:8086) | User: `influxadmin` \| Pass: `influxpassword123` | En **Data Explorer**, graficar `cpu_utilizada_pct` para comparar tráfico web (`srv-01`) vs batch jobs (`srv-02`). |

*(Tip: ejecutando `.\run.ps1 open-dashboards` se abren todas las pestañas juntas en el navegador).*

---

## Casos de Uso y Consultas para Mostrar en Clase

### 1. Relacional - PostgreSQL
* **Concepto:** Tablas estrictas y relaciones 1:N.
* **Consulta:** Agregación con `JOIN` y `GROUP BY` calculando el total facturado por usuario:
```sql
SELECT u.nombre, u.categoria, COUNT(p.id) AS total_pedidos, COALESCE(SUM(p.precio), 0) AS total_gastado
FROM usuarios u
LEFT JOIN pedidos p ON u.id = p.usuario_id
GROUP BY u.id, u.nombre, u.categoria
ORDER BY total_gastado DESC;
```

### 2. Documental - MongoDB (`usuarios_evolutivos`)
* **Concepto:** Schema evolution. En la misma colección conviven:
  * Documento v1: campos básicos planos (`nombre`, `email`).
  * Documento v2: suma arrays de teléfonos y objeto anidado `direccion`.
  * Documento v3: suma suscripción SaaS y preferencias.
* **Consulta:** Búsqueda flexible sobre documentos heterogéneos sin haber tenido que correr ningún `ALTER TABLE`.

### 3. Clave-Valor - Redis
* **Concepto:** Acceso $O(1)$ directo por clave en memoria RAM.
* **Casos:**
  * `session:tok_9942`: Hash con datos del usuario logueado y expiración automática (`TTL`).
  * `config:sistema:mantenimiento`: Feature flag booleano leído al vuelo.
  * `contador:visitas:aula_virtual`: Contador con incremento atómico (`INCRBY`).
  * `ranking:estudiantes:top`: Leaderboard ordenado mediante Sorted Sets (`ZADD`).

### 4. Grafos - Neo4j
* **Concepto:** Red social de personas conectadas por relaciones directas (`:AMIGO_DE`, `:SIGUE_A`, `:LE_GUSTA`, `:COLABORA_CON`).
* **Consulta didáctica (Recomendación "Amigos de mis amigos"):**
```cypher
MATCH (yo:Persona {name: 'Marcos'})-[:AMIGO_DE]->(amigo:Persona)-[:AMIGO_DE]->(amigo_de_amigo:Persona)
WHERE NOT (yo)-[:AMIGO_DE]->(amigo_de_amigo) AND yo <> amigo_de_amigo
RETURN amigo_de_amigo.name AS sugerencia, amigo_de_amigo.rol AS rol, amigo.name AS amigo_en_comun;
```

### 5. Series Temporales / Columnar - InfluxDB
* **Concepto:** Procesamiento analítico masivo por columnas (estilo BigQuery) en vez de lectura por filas.
* **Demostración:** En Data Explorer, comparar los dos servidores:
  * `srv-prod-latam-01`: Curva oscilante de tráfico web diurno.
  * `srv-prod-latam-02`: Servidor batch que permanece bajo y mete un pico abrupto de trabajo.

---

## Detener y Limpiar el Laboratorio

Para apagar los contenedores conservando los datos:
```powershell
docker compose down
# o: .\run.ps1 down
```

Para reiniciar todo a cero borrando los datos persistidos en `./data`:
```powershell
.\run.ps1 clean
```

---
*Cátedra de Diseño de Sistemas - Guía práctica de persistencia políglota.*
