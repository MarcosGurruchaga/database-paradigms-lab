#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
LABORATORIO MULTI-PARADIGMA DE BASES DE DATOS (EDICION PEDAGOGICA PARA CLASES)
Script de Sembrado (Seed) y Demostracion Funcional

Paradigmas y Casos de Uso Explicados:
  1. Relacional (SQL) -> PostgreSQL: Tablas estructuradas fijas e integridad ACID
  2. Documental (NoSQL) -> MongoDB: Objetos flexibles que van mutando (Schema Evolution)
  3. Clave-Valor -> Redis: Recuperacion puntual ultra-rapida por clave O(1)
  4. Grafos -> Neo4j: Mini Red Social (Amigos, Seguidores, Likes y Recomendacion)
  5. Series Temporales / Columnar -> InfluxDB: Analitica de grandes volumenes de metricas
=============================================================================
"""

import sys
import os
import time
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Forzar codificacion UTF-8 para evitar errores de codificacion en terminales Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Librerias de presentacion en terminal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich import box

# Drivers de bases de datos
try:
    import psycopg
    from psycopg.rows import dict_row
    USE_PSYCOPG3 = True
except ImportError:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_PSYCOPG3 = False

from pymongo import MongoClient
import redis
from neo4j import GraphDatabase
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

console = Console(highlight=False)

# =============================================================================
# CONFIGURACION POR DEFECTO
# =============================================================================
CONFIG = {
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5433")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgrespassword"),
        "dbname": os.getenv("POSTGRES_DB", "lab_sql")
    },
    "mongodb": {
        "host": os.getenv("MONGO_HOST", "localhost"),
        "port": int(os.getenv("MONGO_PORT", "27017")),
        "user": os.getenv("MONGO_USER", "mongo"),
        "password": os.getenv("MONGO_PASSWORD", "mongopassword"),
        "dbname": os.getenv("MONGO_DB", "lab_nosql")
    },
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "password": os.getenv("REDIS_PASSWORD", "redispassword")
    },
    "neo4j": {
        "uri": f"bolt://{os.getenv('NEO4J_HOST', 'localhost')}:{os.getenv('NEO4J_BOLT_PORT', '7687')}",
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "neo4jpassword")
    },
    "influxdb": {
        "url": f"http://{os.getenv('INFLUXDB_HOST', 'localhost')}:{os.getenv('INFLUXDB_PORT', '8086')}",
        "token": os.getenv("INFLUXDB_TOKEN", "lab-super-secret-admin-token-2026"),
        "org": os.getenv("INFLUXDB_ORG", "devops-lab"),
        "bucket": os.getenv("INFLUXDB_BUCKET", "telemetry-bucket")
    }
}


def retry_connection(func, engine_name: str, max_retries: int = 6, delay: int = 3):
    """Ejecuta una funcion de conexion con reintentos para tolerar el arranque de contenedores."""
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                console.print(f"[bold red][ERROR] Fallo conectando a {engine_name}:[/] {e}")
                raise e
            console.print(f"[yellow][ESPERA] Esperando inicializacion de {engine_name} (intento {attempt}/{max_retries})...[/]")
            time.sleep(delay)


# =============================================================================
# 1. PARADIGMA RELACIONAL (SQL): PostgreSQL
# CONCEPTO CLAVE: Estructura rigida en tablas, integridad referencial y ACID
# =============================================================================
def demo_postgresql():
    console.rule("[bold cyan]1. PARADIGMA RELACIONAL (SQL) - PostgreSQL[/]")
    console.print("[italic white]Concepto: Tablas estrictas, columnas tipadas e integridad referencial (claves foraneas).[/]\n")

    cfg = CONFIG["postgres"]

    def connect():
        if USE_PSYCOPG3:
            return psycopg.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
                dbname=cfg["dbname"],
                autocommit=True,
                row_factory=dict_row
            )
        else:
            c = psycopg2.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
                dbname=cfg["dbname"]
            )
            c.autocommit = True
            return c

    conn = retry_connection(connect, "PostgreSQL")
    cursor = conn.cursor() if USE_PSYCOPG3 else conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        DROP TABLE IF EXISTS pedidos CASCADE;
        DROP TABLE IF EXISTS usuarios CASCADE;

        CREATE TABLE usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            categoria VARCHAR(50) DEFAULT 'Estudiante',
            creado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE pedidos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            producto VARCHAR(100) NOT NULL,
            precio NUMERIC(10, 2) NOT NULL,
            estado VARCHAR(30) DEFAULT 'completado',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Sembrado representativo
    usuarios = [
        ("Marcos Gurruchaga", "marcos@universidad.edu", "Profesor"),
        ("Ana Gomez", "ana@universidad.edu", "Estudiante"),
        ("Carlos Silva", "carlos@universidad.edu", "Investigador")
    ]
    cursor.executemany("INSERT INTO usuarios (nombre, email, categoria) VALUES (%s, %s, %s);", usuarios)

    pedidos = [
        (1, "Licencia Docker Pro", 60.00, "completado"),
        (1, "Libro Diseno de Sistemas Distribuidos", 45.50, "completado"),
        (2, "Curso Bases de Datos NoSQL", 25.00, "completado"),
        (2, "Teclado Ergonomico", 110.00, "pendiente"),
        (3, "Acceso a Cluster Cloud GPU", 250.00, "completado")
    ]
    cursor.executemany("INSERT INTO pedidos (usuario_id, producto, precio, estado) VALUES (%s, %s, %s, %s);", pedidos)
    console.print(f"[green][OK] Creadas tablas DDL relacionales con integridad referencial (FK).[/]")
    console.print(f"[green][OK] Sembrados {len(usuarios)} usuarios y {len(pedidos)} pedidos vinculados.[/]\n")

    # Consulta representativa: JOIN + GROUP BY
    cursor.execute("""
        SELECT 
            u.id,
            u.nombre,
            u.categoria,
            COUNT(p.id) AS total_pedidos,
            COALESCE(SUM(p.precio), 0) AS total_gastado
        FROM usuarios u
        LEFT JOIN pedidos p ON u.id = p.usuario_id
        GROUP BY u.id, u.nombre, u.categoria
        ORDER BY total_gastado DESC;
    """)
    filas = cursor.fetchall()

    tabla = Table(title="PostgreSQL: Consulta Analitica con JOIN y Agrupacion", box=box.ROUNDED)
    tabla.add_column("ID", justify="center", style="cyan")
    tabla.add_column("Usuario", style="white")
    tabla.add_column("Categoria", style="magenta")
    tabla.add_column("Cant. Pedidos", justify="right", style="green")
    tabla.add_column("Total Facturado (USD)", justify="right", style="bold yellow")

    for f in filas:
        tabla.add_row(str(f["id"]), f["nombre"], f["categoria"], str(f["total_pedidos"]), f"${f['total_gastado']:,.2f}")

    console.print(tabla)
    cursor.close()
    conn.close()
    return True


# =============================================================================
# 2. PARADIGMA DOCUMENTAL (NoSQL): MongoDB
# CONCEPTO CLAVE: "Objetos que van mutando" (Schema Evolution / Polimorfismo)
# En una misma coleccion conviven versiones con campos dinamicos sin ALTER TABLE
# =============================================================================
def demo_mongodb():
    console.rule("[bold green]2. PARADIGMA DOCUMENTAL (NoSQL) - MongoDB[/]")
    console.print("[italic white]Concepto: Objetos que van mutando en el tiempo (Schema Evolution) sin migraciones rigidas de tabla.[/]\n")

    cfg = CONFIG["mongodb"]
    uri = f"mongodb://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/"

    def connect():
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        return client

    client = retry_connection(connect, "MongoDB")
    db = client[cfg["dbname"]]
    coleccion = db["usuarios_evolutivos"]
    coleccion.delete_many({})

    # Demostracion de objetos que mutan en diferentes generaciones de la aplicacion:
    documentos_mutantes = [
        # Generacion 1 (Version Inicial MVP): Datos planos basicos
        {
            "version_schema": 1,
            "username": "lucas99",
            "nombre": "Lucas Martinez",
            "email": "lucas@example.com",
            "fecha_registro": "2023-01-15"
        },
        # Generacion 2 (La app suma telefonos multiples y direccion anidada):
        {
            "version_schema": 2,
            "username": "sofia_dev",
            "nombre": "Sofia Valenzuela",
            "email": "sofia@example.com",
            "telefonos": ["+54 11 5555-1234", "+54 11 9999-8888"],
            "direccion": {
                "calle": "Av. Corrientes 1234",
                "ciudad": "Buenos Aires",
                "pais": "Argentina"
            },
            "activo": True
        },
        # Generacion 3 (Version moderna: Suma suscripcion SaaS, preferencias dinamicas y metadatos):
        {
            "version_schema": 3,
            "username": "mgurruchaga",
            "nombre": "Marcos Gurruchaga",
            "email": "marcos@example.com",
            "telefonos": ["+54 11 4444-7777"],
            "suscripcion": {
                "plan": "Enterprise Cloud",
                "auto_renovacion": True,
                "limite_contenedores": 50
            },
            "preferencias": {
                "tema_oscuro": True,
                "notificaciones": {"email": True, "discord": True, "sms": False}
            },
            "skills": ["Docker", "Neo4j", "MongoDB", "Redis", "PostgreSQL"],
            "activo": True
        }
    ]

    coleccion.insert_many(documentos_mutantes)
    console.print(f"[green][OK] Insertados 3 documentos con esquemas totalmente diferentes (Generaciones v1, v2 y v3).[/]")
    console.print("[dim]Nota para la clase: Ninguno requirio ejecutar un 'ALTER TABLE'. Conviven en la misma coleccion.[/]\n")

    # Consulta flexible: Filtrar por atributos anidados que solo existen en versiones avanzadas
    resultados = list(coleccion.find())

    tabla = Table(title="MongoDB: Objetos con Esquema Evolutivo (Diferentes Atributos en una Coleccion)", box=box.ROUNDED)
    tabla.add_column("Gen", justify="center", style="cyan")
    tabla.add_column("Usuario", style="white")
    tabla.add_column("Estructura de Campos Presentes", style="yellow")
    tabla.add_column("Objeto Anidado / Atributo Dinamico", style="green")

    for doc in resultados:
        campos = list(doc.keys())
        campos.remove("_id")
        gen = f"v{doc.get('version_schema', 1)}"
        
        detalle = "Solo campos planos"
        if "direccion" in doc:
            detalle = f"Direccion: {doc['direccion']['ciudad']}, {doc['direccion']['pais']}"
        elif "suscripcion" in doc:
            detalle = f"Plan: {doc['suscripcion']['plan']} (Skills: {len(doc.get('skills', []))})"

        tabla.add_row(gen, doc["nombre"], ", ".join(campos), detalle)

    console.print(tabla)
    client.close()
    return True


# =============================================================================
# 3. PARADIGMA CLAVE-VALOR: Redis
# CONCEPTO CLAVE: "Recuperar datos facilmente puntuales" por Key en O(1)
# No hay indices complejos: si sabes la clave, el acceso es en sub-milisegundos
# =============================================================================
def demo_redis():
    console.rule("[bold red]3. PARADIGMA CLAVE-VALOR - Redis[/]")
    console.print("[italic white]Concepto: Acceso puntual directo por Clave en memoria RAM con complejidad O(1) y latencia sub-milisegundo.[/]\n")

    cfg = CONFIG["redis"]

    def connect():
        r = redis.Redis(host=cfg["host"], port=cfg["port"], password=cfg["password"], decode_responses=True)
        r.ping()
        return r

    r = retry_connection(connect, "Redis")

    # Caso 1: Recuperacion puntual de Sesion de Usuario por Token (Hash + TTL)
    token_profesor = "session:tok_9942"
    r.hset(token_profesor, mapping={
        "usuario_id": "42",
        "username": "mgurruchaga",
        "rol": "profesor_titular",
        "email": "marcos@universidad.edu",
        "login_ip": "192.168.1.100"
    })
    r.expire(token_profesor, 3600)  # Expira en 1 hora

    token_alumna = "session:tok_1050"
    r.hset(token_alumna, mapping={
        "usuario_id": "50",
        "username": "anagomez",
        "rol": "estudiante",
        "email": "ana@universidad.edu",
        "login_ip": "192.168.1.105"
    })
    r.expire(token_alumna, 3600)

    # Caso 2: Recuperacion puntual de Configuracion Global / Feature Flags
    r.set("config:sistema:mantenimiento", "false")
    r.set("config:feature_flags:modo_oscuro", "true")

    # Caso 3: Contador puntual rapido (Atomic Increment)
    clave_contador = "contador:visitas:aula_virtual"
    r.set(clave_contador, "150")
    r.incrby(clave_contador, 12)

    # Caso 4: Ranking en tiempo real (Sorted Set - ZSET)
    r.delete("ranking:estudiantes:top")
    r.zadd("ranking:estudiantes:top", {
        "Marcos Gurruchaga": 995.0,
        "Ana Gomez": 960.0,
        "Carlos Silva": 920.0,
        "Sofia Lopez": 890.0
    })

    # Caso 5: Cola de mensajes / notificaciones pendientes (List)
    r.delete("cola:notificaciones")
    r.rpush("cola:notificaciones", "Bienvenido al Laboratorio NoSQL", "Nueva tarea de Grafos publicada", "Servidores en linea")

    console.print("[green][OK] Claves de diferentes tipos guardadas en memoria RAM (Hashes, Strings, ZSet, List).[/]")

    # Demostracion de lecturas directas puntuales:
    sesion_recuperada = r.hgetall(token_profesor)
    ttl_restante = r.ttl(token_profesor)
    estado_mantenimiento = r.get("config:sistema:mantenimiento")
    total_visitas = r.get(clave_contador)
    top_ranking = r.zrevrange("ranking:estudiantes:top", 0, 2, withscores=True)

    arbol = Tree("[bold cyan]Redis: Recuperacion Puntual Directa por Clave[/]")

    nodo_sesion = arbol.add(f"[bold yellow]1. Hash puntual '{token_profesor}' (TTL: {ttl_restante}s)[/]")
    for k, v in sesion_recuperada.items():
        nodo_sesion.add(f"[dim]{k}:[/] [white]{v}[/]")

    arbol.add(f"[bold yellow]2. String puntual 'config:sistema:mantenimiento':[/] [bold green]{estado_mantenimiento}[/] (Verifica flags del sistema al vuelo)")
    arbol.add(f"[bold yellow]3. String contador '{clave_contador}':[/] [bold magenta]{total_visitas} visitas[/] (Contador atomico instantaneo)")

    nodo_rank = arbol.add("[bold yellow]4. Sorted Set 'ranking:estudiantes:top' (Top 3):[/]")
    for pos, (nombre, puntaje) in enumerate(top_ranking, start=1):
        nodo_rank.add(f"#{pos} [white]{nombre}[/]: [bold cyan]{puntaje} pts[/]")

    console.print(arbol)
    r.close()
    return True


# =============================================================================
# 4. PARADIGMA DE GRAFOS: Neo4j
# CONCEPTO CLAVE: "Mini Red Social" (100% Personas conectadas por Amistad, Likes y Seguimiento)
# =============================================================================
def demo_neo4j():
    console.rule("[bold blue]4. PARADIGMA DE GRAFOS - Neo4j[/]")
    console.print("[italic white]Concepto: Mini Red Social de Personas: Nodos (:Persona) conectados por Amistad, Likes y Seguidores.[/]\n")

    cfg = CONFIG["neo4j"]

    def connect():
        driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
        driver.verify_connectivity()
        return driver

    driver = retry_connection(connect, "Neo4j")

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        # Sembrado de la Mini Red Social
        # La propiedad 'name' es la que Neo4j Browser muestra siempre por defecto en el centro de cada nodo
        cypher_seed = """
        // 1. Nodos de Personas (solo personas con 'name' como primer atributo)
        CREATE (marcos:Persona {name: 'Marcos', nombre_completo: 'Marcos Gurruchaga', rol: 'Profesor DevOps'})
        CREATE (ana:Persona {name: 'Ana', nombre_completo: 'Ana Gomez', rol: 'Estudiante Cloud'})
        CREATE (carlos:Persona {name: 'Carlos', nombre_completo: 'Carlos Silva', rol: 'Backend Developer'})
        CREATE (sofia:Persona {name: 'Sofia', nombre_completo: 'Sofia Lopez', rol: 'Data Scientist'})
        CREATE (mateo:Persona {name: 'Mateo', nombre_completo: 'Mateo Rivas', rol: 'Frontend Dev'})
        CREATE (lucas:Persona {name: 'Lucas', nombre_completo: 'Lucas Martinez', rol: 'DevOps Engineer'})

        // 2. Relaciones de Amistad Mutua (:AMIGO_DE)
        CREATE (marcos)-[:AMIGO_DE]->(ana)
        CREATE (ana)-[:AMIGO_DE]->(marcos)

        CREATE (ana)-[:AMIGO_DE]->(carlos)
        CREATE (carlos)-[:AMIGO_DE]->(ana)

        CREATE (carlos)-[:AMIGO_DE]->(sofia)
        CREATE (sofia)-[:AMIGO_DE]->(carlos)

        CREATE (mateo)-[:AMIGO_DE]->(lucas)
        CREATE (lucas)-[:AMIGO_DE]->(mateo)

        // 3. Relaciones de Seguimiento (:SIGUE_A)
        CREATE (carlos)-[:SIGUE_A]->(marcos)
        CREATE (sofia)-[:SIGUE_A]->(marcos)
        CREATE (mateo)-[:SIGUE_A]->(marcos)
        CREATE (lucas)-[:SIGUE_A]->(ana)

        // 4. Interacciones Directas de Likes entre personas (:LE_GUSTA)
        CREATE (carlos)-[:LE_GUSTA]->(ana)
        CREATE (ana)-[:LE_GUSTA]->(marcos)
        CREATE (sofia)-[:LE_GUSTA]->(carlos)
        CREATE (marcos)-[:LE_GUSTA]->(ana)
        CREATE (lucas)-[:LE_GUSTA]->(mateo)

        // 5. Relaciones de Estudio / Trabajo (:ESTUDIA_CON)
        CREATE (ana)-[:ESTUDIA_CON]->(carlos)
        CREATE (mateo)-[:ESTUDIA_CON]->(lucas)
        """
        session.run(cypher_seed)
        console.print("[green][OK] Mini Red Social construida: Nodos (:Persona) con propiedad 'name' y relaciones (:AMIGO_DE, :SIGUE_A, :LE_GUSTA, :ESTUDIA_CON).[/]\n")

        # Consulta 1: Algoritmo de recomendacion social ("Amigos de mis amigos que aun no conozco")
        query_amigos = """
        MATCH (yo:Persona {name: 'Marcos'})-[:AMIGO_DE]->(amigo:Persona)-[:AMIGO_DE]->(amigo_de_amigo:Persona)
        WHERE NOT (yo)-[:AMIGO_DE]->(amigo_de_amigo) AND yo <> amigo_de_amigo
        RETURN 
            amigo_de_amigo.name AS sugerencia,
            amigo_de_amigo.rol AS rol,
            amigo.name AS amigo_en_comun
        """
        sugerencias = session.run(query_amigos).data()

        tabla_sug = Table(title="Neo4j: Algoritmo de Sugerencia Social ('Amigos de mis amigos')", box=box.ROUNDED)
        tabla_sug.add_column("Persona Sugerida", style="cyan")
        tabla_sug.add_column("Rol / Especialidad", style="white")
        tabla_sug.add_column("Amigo en Comun (Puente)", style="yellow")

        for r in sugerencias:
            tabla_sug.add_row(r["sugerencia"], r["rol"], r["amigo_en_comun"])

        console.print(tabla_sug)

        # Consulta 2: Interacciones de Likes entre personas (:LE_GUSTA)
        query_likes = """
        MATCH (origen:Persona)-[:LE_GUSTA]->(destino:Persona)
        RETURN origen.name AS dio_like, destino.name AS le_gusta_perfil_de, destino.rol AS rol
        ORDER BY dio_like
        """
        likes = session.run(query_likes).data()

        tabla_likes = Table(title="Neo4j: Interacciones de Likes entre Personas (:LE_GUSTA)", box=box.ROUNDED)
        tabla_likes.add_column("Persona (Dio Like)", style="magenta")
        tabla_likes.add_column("-> Le gusta el perfil de ->", style="cyan")
        tabla_likes.add_column("Rol de la Persona", style="yellow")

        for l in likes:
            tabla_likes.add_row(l["dio_like"], l["le_gusta_perfil_de"], l["rol"])

        console.print(tabla_likes)

    driver.close()
    return True


# =============================================================================
# 5. PARADIGMA COLUMNAR / SERIES TEMPORALES: InfluxDB (Analitica masiva)
# CONCEPTO CLAVE: "Muchos datos para analizar" (Analitica vectorial estilo BigQuery)
# En lugar de leer fila por fila, agrupa y calcula estadisticas sobre columnas de metricas
# =============================================================================
def demo_influxdb():
    console.rule("[bold magenta]5. SERIES TEMPORALES / ENFOQUE COLUMNAR - InfluxDB 2.x[/]")
    console.print("[italic white]Concepto: Procesamiento de grandes volumenes de datos para analitica y agregaciones masivas en tiempo real.[/]\n")

    cfg = CONFIG["influxdb"]

    def connect():
        client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"], timeout=5000)
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"InfluxDB no saludable: {health.message}")
        return client

    client = retry_connection(connect, "InfluxDB")
    
    # Limpiar datos previos para que el Data Explorer se vea perfecto y sin lineas duplicadas
    try:
        del_api = client.delete_api()
        del_api.delete(
            start="1970-01-01T00:00:00Z",
            stop=datetime.now(timezone.utc).isoformat(),
            predicate="",
            bucket=cfg["bucket"],
            org=cfg["org"]
        )
    except Exception:
        pass

    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Inyeccion masiva de telemetria analitica con patrones claramente diferenciados
    import math
    ahora = datetime.now(timezone.utc)
    puntos = []

    # 30 puntos espaciados cada 3 minutos (cubre la ultima hora y media)
    total_puntos = 30
    for i in range(total_puntos):
        t = ahora - timedelta(minutes=(total_puntos - 1 - i) * 3)

        # ---------------------------------------------------------------------
        # Servidor 01: Servidor Web / API de Usuarios
        # Comportamiento: Ondas suaves de trafico organico con subidas y bajadas
        # ---------------------------------------------------------------------
        cpu_01 = round(42.0 + 26.0 * math.sin(i / 4.0) + ((i % 3) * 1.5), 1)
        mem_01 = round(54.0 + 9.0 * math.sin(i / 5.5) + ((i % 2) * 1.2), 1)
        req_01 = int(2800 + 1400 * math.sin(i / 4.0) + (i * 20))

        puntos.append(
            Point("metricas_servidores")
            .tag("host", "srv-prod-latam-01")
            .tag("datacenter", "dc-buenos-aires")
            .tag("tipo_servidor", "api-gateway")
            .field("cpu_utilizada_pct", max(15.0, min(95.0, cpu_01)))
            .field("memoria_utilizada_pct", max(20.0, min(95.0, mem_01)))
            .field("peticiones_por_seg", req_01)
            .time(t, WritePrecision.NS)
        )

        # ---------------------------------------------------------------------
        # Servidor 02: Servidor de Tareas en Segundo Plano / Batch Worker
        # Comportamiento: Base baja (20%), rastro abrupto de carga pesada (88%)
        # entre los puntos 10 y 20, y luego recuperacion
        # ---------------------------------------------------------------------
        if 10 <= i <= 21:
            # Procesamiento batch en ejecucion
            cpu_02 = round(82.0 + ((i % 5) * 2.3), 1)
            mem_02 = round(68.0 + ((i - 10) * 1.8), 1)
            req_02 = int(950 + ((i % 3) * 180))
        else:
            # Reposo / Tareas livianas
            cpu_02 = round(22.0 + ((i % 4) * 2.0), 1)
            mem_02 = round(38.0 + ((i % 3) * 1.5), 1)
            req_02 = int(320 + ((i % 2) * 60))

        puntos.append(
            Point("metricas_servidores")
            .tag("host", "srv-prod-latam-02")
            .tag("datacenter", "dc-buenos-aires")
            .tag("tipo_servidor", "batch-worker")
            .field("cpu_utilizada_pct", max(10.0, min(98.0, cpu_02)))
            .field("memoria_utilizada_pct", max(20.0, min(95.0, mem_02)))
            .field("peticiones_por_seg", req_02)
            .time(t, WritePrecision.NS)
        )

    write_api.write(bucket=cfg["bucket"], org=cfg["org"], record=puntos)
    console.print(f"[green][OK] Inyectados {len(puntos)} registros analiticos en '{cfg['bucket']}' (30 timestamps por host).[/]")
    console.print("[dim]Nota visual: 'srv-prod-latam-01' muestra ondas de trafico web, 'srv-prod-latam-02' muestra picos de procesamiento batch.[/]\n")

    # Consulta FLUX analitica: Agregacion de columna (Tail + Filtro)
    query_api = client.query_api()
    flux_query = f"""
    from(bucket: "{cfg['bucket']}")
      |> range(start: -2h)
      |> filter(fn: (r) => r["_measurement"] == "metricas_servidores")
      |> filter(fn: (r) => r["_field"] == "cpu_utilizada_pct")
      |> tail(n: 4)
    """
    tablas = query_api.query(flux_query, org=cfg["org"])

    tabla = Table(title="InfluxDB: Lectura Analitica Comparativa de CPU (Ultimos Registros)", box=box.ROUNDED)
    tabla.add_column("Hora (UTC)", style="white")
    tabla.add_column("Host", style="cyan")
    tabla.add_column("Metrica", style="yellow")
    tabla.add_column("CPU Utilizada (%)", justify="right", style="bold green")

    for tbl in tablas:
        for record in tbl.records:
            t_str = record.get_time().strftime("%H:%M:%S")
            tabla.add_row(t_str, record.values.get("host", "N/A"), record.get_field(), f"{record.get_value():.2f}")

    console.print(tabla)
    client.close()
    return True


# =============================================================================
# EJECUCION PRINCIPAL
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Laboratorio Multi-Paradigma de Bases de Datos para Clases")
    parser.add_argument("--all", action="store_true", default=True, help="Ejecutar demostracion completa")
    parser.add_argument("--engine", choices=["postgres", "mongodb", "redis", "neo4j", "influxdb"], help="Ejecutar solo un motor especifico")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold white on blue]  LABORATORIO PRACTICO DE BASES DE DATOS - CLASE EN VIVO  [/]\n"
        "[italic cyan]Demostracion de los 5 Paradigmas Principales con Casos Reales[/]",
        border_style="cyan"
    ))

    motores = {
        "postgres": ("1. Relacional (SQL) -> Tablas estructuradas e integridad ACID", demo_postgresql),
        "mongodb": ("2. Documental (NoSQL) -> Objetos flexibles que mutan en el tiempo", demo_mongodb),
        "redis": ("3. Clave-Valor -> Recuperacion puntual ultra-rapida O(1)", demo_redis),
        "neo4j": ("4. Grafos -> Mini Red Social (Amigos, Likes y Recomendaciones)", demo_neo4j),
        "influxdb": ("5. Series Temporales / Columnar -> Analitica de grandes volumenes de metricas", demo_influxdb)
    }

    seleccionados = [args.engine] if args.engine else list(motores.keys())
    resumen = {}

    for clave in seleccionados:
        titulo, func = motores[clave]
        try:
            func()
            resumen[titulo] = "[bold green]EXITO (Sembrado y Consultado)[/]"
        except Exception as e:
            resumen[titulo] = f"[bold red]ERROR ({type(e).__name__})[/]"

    # Reporte final
    tabla_reporte = Table(title="Resumen Final para la Clase", box=box.HEAVY_EDGE)
    tabla_reporte.add_column("Paradigma Demostrado", style="white")
    tabla_reporte.add_column("Estado", justify="center")

    for tit, est in resumen.items():
        tabla_reporte.add_row(tit, est)

    console.print("\n")
    console.print(Panel(tabla_reporte, border_style="green", title="[bold green]Reporte de Estado[/]"))


if __name__ == "__main__":
    main()
