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
    token_sesion = "session:tok_9942"
    r.hset(token_sesion, mapping={
        "usuario_id": "42",
        "username": "mgurruchaga",
        "rol": "profesor_titular",
        "login_ip": "192.168.1.100"
    })
    r.expire(token_sesion, 1800)  # Expira en 30 minutos

    # Caso 2: Recuperacion puntual de Configuracion Global de la Plataforma
    clave_config = "config:sistema:mantenimiento"
    r.set(clave_config, "false")

    # Caso 3: Contador puntual rapido (Atomic Increment)
    clave_contador = "contador:visitas:aula_virtual"
    r.set(clave_contador, "150")
    r.incrby(clave_contador, 5)

    console.print("[green][OK] Claves puntuales guardadas en memoria RAM.[/]")

    # Demostracion de lecturas directas puntuales:
    sesion_recuperada = r.hgetall(token_sesion)
    ttl_restante = r.ttl(token_sesion)
    estado_mantenimiento = r.get(clave_config)
    total_visitas = r.get(clave_contador)

    arbol = Tree("[bold cyan]Redis: Recuperacion Puntual Directa por Clave[/]")

    nodo_sesion = arbol.add(f"[bold yellow]1. Clave puntual '{token_sesion}' (TTL: {ttl_restante}s)[/]")
    for k, v in sesion_recuperada.items():
        nodo_sesion.add(f"[dim]{k}:[/] [white]{v}[/]")

    arbol.add(f"[bold yellow]2. Clave puntual '{clave_config}':[/] [bold green]{estado_mantenimiento}[/] (Verifica flags del sistema al vuelo)")
    arbol.add(f"[bold yellow]3. Clave puntual '{clave_contador}':[/] [bold magenta]{total_visitas} visitas[/] (Contador atomico instantaneo)")

    console.print(arbol)
    r.close()
    return True


# =============================================================================
# 4. PARADIGMA DE GRAFOS: Neo4j
# CONCEPTO CLAVE: "Mini Red Social" (Nodos de personas, relaciones de amistad,
# seguimiento y publicaciones, recomendando 'amigos de mis amigos')
# =============================================================================
def demo_neo4j():
    console.rule("[bold blue]4. PARADIGMA DE GRAFOS - Neo4j[/]")
    console.print("[italic white]Concepto: Mini Red Social: Nodos de Usuarios y Publicaciones conectados por Amistad, Seguimiento y Likes.[/]\n")

    cfg = CONFIG["neo4j"]

    def connect():
        driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
        driver.verify_connectivity()
        return driver

    driver = retry_connection(connect, "Neo4j")

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        # Sembrado de la Mini Red Social
        # Marcos es amigo de Ana y sigue a Mateo.
        # Ana es amiga de Carlos. (Por lo tanto, Carlos es "amigo de un amigo" de Marcos).
        # Publicaciones con likes.
        cypher_seed = """
        // 1. Nodos de Usuarios
        CREATE (marcos:Usuario {nombre: 'Marcos Gurruchaga', profesion: 'DevOps & Profesor', ciudad: 'Buenos Aires'})
        CREATE (ana:Usuario {nombre: 'Ana Gomez', profesion: 'Cloud Architect', ciudad: 'Cordoba'})
        CREATE (carlos:Usuario {nombre: 'Carlos Silva', profesion: 'Backend Dev', ciudad: 'Rosario'})
        CREATE (sofia:Usuario {nombre: 'Sofia Lopez', profesion: 'Data Scientist', ciudad: 'Mendoza'})
        CREATE (mateo:Usuario {nombre: 'Mateo Rivas', profesion: 'Estudiante', ciudad: 'Buenos Aires'})

        // 2. Relaciones de Amistad y Seguimiento
        CREATE (marcos)-[:AMIGO_DE]->(ana)
        CREATE (ana)-[:AMIGO_DE]->(marcos)

        CREATE (ana)-[:AMIGO_DE]->(carlos)
        CREATE (carlos)-[:AMIGO_DE]->(ana)

        CREATE (carlos)-[:AMIGO_DE]->(sofia)
        CREATE (sofia)-[:AMIGO_DE]->(carlos)

        CREATE (marcos)-[:SIGUE_A]->(mateo)
        CREATE (mateo)-[:SIGUE_A]->(marcos)

        // 3. Publicaciones
        CREATE (post1:Publicacion {titulo: 'Laboratorio de Bases de Datos Docker', tema: 'DevOps'})
        CREATE (post2:Publicacion {titulo: 'Introduccion a Grafos con Neo4j', tema: 'GraphDB'})

        CREATE (marcos)-[:PUBLICO]->(post1)
        CREATE (sofia)-[:PUBLICO]->(post2)

        // 4. Interacciones (Likes)
        CREATE (ana)-[:LE_GUSTA]->(post1)
        CREATE (carlos)-[:LE_GUSTA]->(post1)
        CREATE (marcos)-[:LE_GUSTA]->(post2)
        """
        session.run(cypher_seed)
        console.print("[green][OK] Mini Red Social construida: Nodos (:Usuario, :Publicacion) y Aristas (:AMIGO_DE, :SIGUE_A, :LE_GUSTA).[/]\n")

        # Consulta 1: Algoritmo de recomendacion de amigos ("Amigos de mis amigos que aun no conozco")
        # Quien es amigo de mis amigos con quien Marcos aun NO tiene amistad directa?
        query_amigos = """
        MATCH (yo:Usuario {nombre: 'Marcos Gurruchaga'})-[:AMIGO_DE]->(amigo:Usuario)-[:AMIGO_DE]->(amigo_de_amigo:Usuario)
        WHERE NOT (yo)-[:AMIGO_DE]->(amigo_de_amigo) AND yo <> amigo_de_amigo
        RETURN 
            amigo_de_amigo.nombre AS sugerencia,
            amigo_de_amigo.profesion AS profesion,
            amigo.nombre AS amigo_en_comun
        """
        sugerencias = session.run(query_amigos).data()

        tabla_sug = Table(title="Neo4j: Algoritmo de Sugerencia Social ('Amigos de mis amigos')", box=box.ROUNDED)
        tabla_sug.add_column("Usuario Recomendado", style="cyan")
        tabla_sug.add_column("Profesion", style="white")
        tabla_sug.add_column("Conectado a traves de (Amigo en Comun)", style="yellow")

        for r in sugerencias:
            tabla_sug.add_row(r["sugerencia"], r["profesion"], r["amigo_en_comun"])

        console.print(tabla_sug)

        # Consulta 2: Interacciones con posts
        query_feed = """
        MATCH (u:Usuario)-[:LE_GUSTA]->(p:Publicacion)<-[:PUBLICO]-(autor:Usuario)
        RETURN p.titulo AS publicacion, autor.nombre AS autor, collect(u.nombre) AS personas_que_dieron_like
        """
        feed = session.run(query_feed).data()

        tabla_feed = Table(title="Neo4j: Quien interactuo con cada Publicacion (Likes de la red)", box=box.ROUNDED)
        tabla_feed.add_column("Publicacion", style="white")
        tabla_feed.add_column("Autor", style="magenta")
        tabla_feed.add_column("Likes recibidos de", style="green")

        for f in feed:
            tabla_feed.add_row(f["publicacion"], f["autor"], ", ".join(f["personas_que_dieron_like"]))

        console.print(tabla_feed)

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
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Inyeccion masiva de telemetria analitica (15 puntos temporales por host)
    ahora = datetime.now(timezone.utc)
    puntos = []

    hosts = ["srv-prod-latam-01", "srv-prod-latam-02"]
    for host in hosts:
        for i in range(12):
            t = ahora - timedelta(minutes=(12 - i) * 5)
            cpu = round(25.0 + (i * 3.5) + (5 if "01" in host else 8), 2)
            mem = round(45.0 + (i * 2.2), 2)
            reqs = int(1200 + (i * 150))

            p = (
                Point("metricas_servidores")
                .tag("host", host)
                .tag("datacenter", "dc-buenos-aires")
                .field("cpu_utilizada_pct", cpu)
                .field("memoria_utilizada_pct", mem)
                .field("peticiones_por_seg", reqs)
                .time(t, WritePrecision.NS)
            )
            puntos.append(p)

    write_api.write(bucket=cfg["bucket"], org=cfg["org"], record=puntos)
    console.print(f"[green][OK] Inyectados {len(puntos)} registros analiticos en el bucket '{cfg['bucket']}'.[/]\n")

    # Consulta FLUX analitica: Agregacion de columna (Tail + Filtro)
    query_api = client.query_api()
    flux_query = f"""
    from(bucket: "{cfg['bucket']}")
      |> range(start: -2h)
      |> filter(fn: (r) => r["_measurement"] == "metricas_servidores")
      |> filter(fn: (r) => r["_field"] == "cpu_utilizada_pct" or r["_field"] == "peticiones_por_seg")
      |> tail(n: 6)
    """
    tablas = query_api.query(flux_query, org=cfg["org"])

    tabla = Table(title="InfluxDB: Lectura Analitica Columnar (Ultimos Registros Agregados)", box=box.ROUNDED)
    tabla.add_column("Hora (UTC)", style="white")
    tabla.add_column("Host", style="cyan")
    tabla.add_column("Columna / Metrica", style="yellow")
    tabla.add_column("Valor Analizado", justify="right", style="bold green")

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
