#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
LABORATORIO MULTI-PARADIGMA DE BASES DE DATOS (EDICION PEDAGOGICA PARA CLASES)
Script de Sembrado (Seed) y Demostracion Funcional

Paradigmas y Casos de Uso Explicados con Ejemplos Divertidos:
  1. Relacional (SQL) -> PostgreSQL: Estructura rigida e integridad referencial (ACID)
  2. Documental (NoSQL) -> MongoDB: Schema Evolution / Objetos que mutan (Los Simpsons)
  3. Clave-Valor -> Redis: Acceso puntual ultra-rapido O(1) en RAM con TTL (Death Note)
  4. Grafos -> Neo4j: Red de relaciones y traversals interdimensionales (Rick y Morty)
  5. Series Temporales -> InfluxDB: Telemetria continua en tiempo real (Harry Potter / Hogwarts)
  6. Familias de Columnas (Wide-Column) -> Apache Cassandra: Big Data masivo de alta escritura,
     particionado distribuido y clustering keys (Fullmetal Alchemist / Titanes)
=============================================================================
"""

import sys
import os
import time
import argparse
import math
import uuid
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

# Cassandra Driver (con pyasyncore para compatibilidad con Python 3.12+)
try:
    import pyasyncore
except ImportError:
    pass

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

console = Console(highlight=False)

# =============================================================================
# CONFIGURACION DE CONEXION POR DEFECTO
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
    },
    "cassandra": {
        "host": os.getenv("CASSANDRA_HOST", "127.0.0.1"),
        "port": int(os.getenv("CASSANDRA_PORT", "9042")),
        "keyspace": "defensa_amestris"
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
# CONCEPTO CLAVE: Estructura fija en tablas, integridad referencial y ACID
# =============================================================================
def demo_postgresql():
    console.rule("[bold cyan]1. PARADIGMA RELACIONAL (SQL) - PostgreSQL[/]")
    console.print("[italic white]Concepto: Tablas estrictas, columnas tipadas, integridad referencial (FK) y garantias ACID.[/]\n")

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

    # Sembrado representativo del ambito academico de la catedra
    usuarios = [
        ("Dra. Valeria Ramos", "valeria.ramos@universidad.edu", "Profesora Titular"),
        ("Marcos Gurruchaga", "marcos.gurruchaga@universidad.edu", "Ayudante de Catedra"),
        ("Ana Gomez", "ana.gomez@estudiantes.edu", "Estudiante"),
        ("Carlos Silva", "carlos.silva@estudiantes.edu", "Estudiante")
    ]
    cursor.executemany("INSERT INTO usuarios (nombre, email, categoria) VALUES (%s, %s, %s);", usuarios)

    pedidos = [
        (1, "Licencia Software Servidor Academico", 150.00, "completado"),
        (2, "Teclado Mecanico para Correcciones", 85.00, "completado"),
        (2, "Libro Diseno de Sistemas Distribuidos", 45.50, "completado"),
        (3, "Manual de Bases de Datos NoSQL", 30.00, "completado"),
        (4, "Cuaderno de Laboratorio y Guias", 15.00, "pendiente")
    ]
    cursor.executemany("INSERT INTO pedidos (usuario_id, producto, precio, estado) VALUES (%s, %s, %s, %s);", pedidos)
    console.print(f"[green][OK] DDL ejecutado: Tablas relacionales 'usuarios' y 'pedidos' creadas con FK estricta.[/]")
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

    tabla = Table(title="PostgreSQL: Consulta con JOIN y Agrupacion Agregada", box=box.ROUNDED)
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
# EJEMPLO: Los Simpsons - Diferentes temporadas y facetas en una misma coleccion
# =============================================================================
def demo_mongodb():
    console.rule("[bold green]2. PARADIGMA DOCUMENTAL (NoSQL) - MongoDB[/]")
    console.print("[italic white]Concepto: Schema Evolution y Polimorfismo. Objetos que mutan de atributos sin requerir 'ALTER TABLE'.[/]\n")

    cfg = CONFIG["mongodb"]
    uri = f"mongodb://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/"

    def connect():
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        return client

    client = retry_connection(connect, "MongoDB")
    db = client[cfg["dbname"]]
    coleccion = db["ciudadanos_springfield"]
    coleccion.delete_many({})

    # Demostracion de Schema Evolution a lo largo de las temporadas de la serie:
    simpsons_mutantes = [
        # Documento 1 (Temporada 1 - MVP Inicial de la serie): Estructura plana basica
        {
            "temporada_aparicion": 1,
            "nombre": "Homero J. Simpson",
            "edad": 39,
            "ocupacion": "Inspector de Seguridad del Sector 7G",
            "direccion_plana": "Avenida Siempreviva 742",
            "frase_iconica": "D'oh!",
            "hobbies": ["Ver television", "Tomar cerveza Duff"]
        },
        # Documento 2 (Temporada 4 - La app evoluciona: agrega listas y subdocumentos anidados):
        {
            "temporada_aparicion": 4,
            "nombre": "Marjorie Bouvier Simpson",
            "rol": "Ama de casa y Pacificadora",
            "hijos": ["Bart", "Lisa", "Maggie"],
            "hobbies": ["Pintura mural", "Tejido", "Bolos con las Boludas"],
            "direccion": {
                "calle": "Avenida Siempreviva 742",
                "ciudad": "Springfield",
                "estado": "Desconocido (cerca de Shelbyville)"
            },
            "licencia_conducir": {
                "activa": True,
                "infracciones": 0
            }
        },
        # Documento 3 (Temporada 10+ - Polimorfismo extremo: Alter-egos, historial de detenciones y nemesis):
        {
            "temporada_aparicion": 10,
            "nombre": "Bartholomew Jo-Jo Simpson",
            "apodo": "Bart",
            "edad": 10,
            "alter_egos": [
                {"nombre": "El Barto", "actividad": "Grafitero clandestino", "exito": True},
                {"nombre": "El Chico 'Yo No Fui'", "frase": "Yo no fui", "exito": True},
                {"nombre": "Bartman", "arma": "Resortera y capa", "exito": True}
            ],
            "expediente_disciplinario_skinner": {
                "detenciones_en_pizarra": 450,
                "frases_castigo_memorables": ["No instigare a la revolucion", "El gas del profe no es un ambientador"],
                "veces_enviado_a_direccion": 85
            },
            "nemesis_mortal": "Bob Patino (Sideshow Bob)",
            "mascota_favorita": "Ayudante de Santa (Galgo)"
        }
    ]

    coleccion.insert_many(simpsons_mutantes)
    console.print(f"[green][OK] Insertados {len(simpsons_mutantes)} documentos de Los Simpsons con estructuras totalmente polimorficas.[/]")
    console.print("[dim]Nota para la clase: Homero (v1) tiene campos planos, Marge (v4) tiene subdocumento de direccion y Bart (v10) tiene alter-egos y expediente escolar sin ningun ALTER TABLE.[/]\n")

    # Consulta y exposicion en tabla
    resultados = list(coleccion.find())

    tabla = Table(title="MongoDB: Objetos que Mutan en el Tiempo (Coleccion 'ciudadanos_springfield')", box=box.ROUNDED)
    tabla.add_column("Temporada", justify="center", style="cyan")
    tabla.add_column("Personaje", style="bold white")
    tabla.add_column("Campos Presentes en el Documento", style="yellow")
    tabla.add_column("Estructura Dinamica Destacada", style="green")

    for doc in resultados:
        campos = [k for k in doc.keys() if k != "_id"]
        temp = f"Temp {doc.get('temporada_aparicion', 1)}"
        
        if "alter_egos" in doc:
            nombres_egos = [e["nombre"] for e in doc["alter_egos"]]
            detalle = f"Alter-Egos: {', '.join(nombres_egos)} | Detenciones: {doc['expediente_disciplinario_skinner']['detenciones_en_pizarra']}"
        elif "direccion" in doc:
            detalle = f"Hijos: {', '.join(doc.get('hijos', []))} | Dir: {doc['direccion']['calle']}"
        else:
            detalle = f"Frase: '{doc.get('frase_iconica')}' | Ocupacion: {doc.get('ocupacion')}"

        tabla.add_row(temp, doc["nombre"], ", ".join(campos[:5]) + ("..." if len(campos) > 5 else ""), detalle)

    console.print(tabla)
    client.close()
    return True


# =============================================================================
# 3. PARADIGMA CLAVE-VALOR: Redis
# CONCEPTO CLAVE: "Recuperar datos facilmente puntuales" en O(1) en RAM
# EJEMPLO: Death Note - Victimas con TTL de 40s, Reglas del Shinigami y Sospechosos de L
# =============================================================================
def demo_redis():
    console.rule("[bold red]3. PARADIGMA CLAVE-VALOR - Redis[/]")
    console.print("[italic white]Concepto: Lectura y escritura ultra-rapida por Clave puntual en RAM con complejidad O(1) y expiracion automatica (TTL).[/]\n")

    cfg = CONFIG["redis"]

    def connect():
        r = redis.Redis(host=cfg["host"], port=cfg["port"], password=cfg["password"], decode_responses=True)
        r.ping()
        return r

    r = retry_connection(connect, "Redis")

    # 1. HASH con TTL de 40 Segundos (Regla Sagrada del Death Note)
    # "Si la causa de muerte no se especifica dentro de los 40 segundos, la persona morira de paro cardiaco"
    clave_victima = "deathnote:victima:kuro_otoishi"
    r.hset(clave_victima, mapping={
        "nombre": "Kuro Otoishi",
        "crimen": "Secuestro de 8 rehenes en guarderia",
        "causa_muerte": "Paro cardiaco fulminante",
        "anotado_por": "Kira (Light Yagami)",
        "hora_anotacion": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })
    r.expire(clave_victima, 40)  # Expira en 40 segundos exactos

    # 2. STRINGS PUNTUALES: Reglas del Shinigami Ryuk
    r.set("deathnote:regla:01", "La persona cuyo nombre sea escrito en esta libreta morira.")
    r.set("deathnote:regla:02", "Esta libreta no surtira efecto a menos que el escritor tenga en mente el rostro de la persona.")

    # 3. CONTADOR ATOMICO (INCRBY): Contador de criminales juzgados por Kira
    clave_contador = "kira:contador:criminales_eliminados"
    r.set(clave_contador, "1240")
    r.incrby(clave_contador, 1)  # Incremento atomico en nanosegundos sin locks

    # 4. SORTED SET (ZSET): Probabilidad de sospechosos segun el Detective L
    clave_sospechosos = "cuartel_l:probabilidad_ser_kira"
    r.delete(clave_sospechosos)
    r.zadd(clave_sospechosos, {
        "Light Yagami": 96.8,
        "Misa Amane (Segunda Kira)": 88.5,
        "Teru Mikami": 75.0,
        "Kyosuke Higuchi (Yotsuba)": 62.4,
        "Touta Matsuda (Detective)": 0.05
    })

    # 5. LIST (COLA DE TAREAS): Manzanas favoritas para aplacar a Ryuk
    clave_manzanas = "shinigami:ryuk:manzanas_pendientes"
    r.delete(clave_manzanas)
    r.rpush(clave_manzanas, "Manzana roja de la region de Nagano", "Manzana verde acida Fuji", "Tarta dulce de manzana")

    console.print("[green][OK] Claves de Death Note sembradas en memoria RAM (Hashes con TTL 40s, Strings, ZSet, List).[/]")

    # Lectura puntual en O(1)
    victima_recuperada = r.hgetall(clave_victima)
    ttl_restante = r.ttl(clave_victima)
    regla_01 = r.get("deathnote:regla:01")
    total_eliminados = r.get(clave_contador)
    top_sospechosos = r.zrevrange(clave_sospechosos, 0, 2, withscores=True)

    arbol = Tree("[bold red]Redis: Recuperacion Puntual Directa por Clave (Death Note)[/]")

    nodo_victima = arbol.add(f"[bold yellow]1. Hash Puntual '{clave_victima}' [bold red](TTL: {ttl_restante}s restantes)[/]")
    for k, v in victima_recuperada.items():
        nodo_victima.add(f"[dim]{k}:[/] [white]{v}[/]")

    arbol.add(f"[bold yellow]2. String Puntual 'deathnote:regla:01':[/] [italic cyan]\"{regla_01}\"[/]")
    arbol.add(f"[bold yellow]3. Contador Atomico '{clave_contador}':[/] [bold green]{total_eliminados} criminales[/] (Incremento instantaneo)")

    nodo_rank = arbol.add("[bold yellow]4. Sorted Set 'cuartel_l:probabilidad_ser_kira' (Top 3 de L):[/]")
    for pos, (nombre, puntaje) in enumerate(top_sospechosos, start=1):
        nodo_rank.add(f"#{pos} [bold white]{nombre}[/]: [bold magenta]{puntaje}% probabilidad[/]")

    console.print(arbol)
    r.close()
    return True


# =============================================================================
# 4. PARADIGMA DE GRAFOS: Neo4j
# CONCEPTO CLAVE: "Mini Red Social / Multiverso de Relaciones Directas"
# EJEMPLO: Rick y Morty - Nodos de Personajes y Conexiones Interdimensionales
# =============================================================================
def demo_neo4j():
    console.rule("[bold blue]4. PARADIGMA DE GRAFOS - Neo4j[/]")
    console.print("[italic white]Concepto: Red de entidades interconectadas. La propiedad 'name' define el nodo para visualizacion en Neo4j Browser.[/]\n")

    cfg = CONFIG["neo4j"]

    def connect():
        driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
        driver.verify_connectivity()
        return driver

    driver = retry_connection(connect, "Neo4j")

    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        # Sembrado de Rick y Morty
        # REGLA CRITICA: La primera propiedad es 'name' para que el visor de Neo4j Browser centre el nombre del personaje
        cypher_seed = """
        // 1. Nodos de Personajes
        CREATE (rick:Personaje {name: 'Rick Sanchez', dimension: 'C-137', especie: 'Humano / Genio', estado: 'Ebrio'})
        CREATE (morty:Personaje {name: 'Morty Smith', dimension: 'C-137', especie: 'Humano', rol: 'Nieto Acompanante'})
        CREATE (summer:Personaje {name: 'Summer Smith', dimension: 'C-137', especie: 'Humana', rol: 'Hermana Mayor Rebelde'})
        CREATE (jerry:Personaje {name: 'Jerry Smith', dimension: 'C-137', especie: 'Humano', ocupacion: 'Desempleado'})
        CREATE (beth:Personaje {name: 'Beth Smith', dimension: 'C-137', especie: 'Humana', ocupacion: 'Cirujana de Caballos'})
        CREATE (birdperson:Personaje {name: 'Hombre Pajaro', dimension: 'C-137', especie: 'Pajaro Humanoide', rol: 'Mejor Amigo Guerrero'})
        CREATE (evil_morty:Personaje {name: 'Evil Morty', dimension: 'Desconocida', especie: 'Humano', rol: 'Presidente de la Ciudadela'})
        CREATE (meeseeks:Personaje {name: 'Mr Meeseeks', dimension: 'Caja Meeseeks', especie: 'Entidad Temporal', proposito: 'Bajar 2 golpes de golf'})

        // 2. Relaciones Familiares y de Aventura (Originales)
        CREATE (rick)-[:VIAJA_CON {portales_abiertos: 450}]->(morty)
        CREATE (morty)-[:VIAJA_CON]->(rick)
        CREATE (morty)-[:HERMANO_DE]->(summer)
        CREATE (summer)-[:HERMANO_DE]->(morty)
        CREATE (summer)-[:SIGUE_AVENTURAS_DE]->(rick)
        CREATE (beth)-[:CASADA_CON]->(jerry)
        CREATE (jerry)-[:CASADO_CON]->(beth)

        // Relacion Repetida entre Multiples Nodos: :HIJO_DE
        CREATE (morty)-[:HIJO_DE]->(beth)
        CREATE (morty)-[:HIJO_DE]->(jerry)
        CREATE (summer)-[:HIJO_DE]->(beth)
        CREATE (summer)-[:HIJO_DE]->(jerry)
        CREATE (beth)-[:HIJO_DE]->(rick)

        // 3. Amistades y Alianzas Fuertes (Originales)
        CREATE (rick)-[:AMIGO_DE {nivel_lealtad: 'Extremo'}]->(birdperson)
        CREATE (birdperson)-[:AMIGO_DE]->(rick)

        // 4. Invocacion y Tragedia Existencial de Mr Meeseeks (Originales)
        CREATE (rick)-[:INVOCO_A]->(meeseeks)
        CREATE (jerry)-[:PIDIO_AYUDA_A]->(meeseeks)
        CREATE (meeseeks)-[:QUIERE_ELIMINAR_A {motivo: 'Existir es dolor para un Meeseeks'}]->(jerry)

        // 5. Hostilidad, Desprecio y Enemistad (Originales)
        CREATE (rick)-[:DESPRECIA_A {motivo: 'Incompetencia cronica'}]->(jerry)
        CREATE (jerry)-[:ODIA_A]->(rick)
        CREATE (evil_morty)-[:ENEMIGO_MORTAL_DE]->(rick)
        """
        session.run(cypher_seed)
        console.print("[green][OK] Grafo de Rick y Morty sembrado: Relaciones originales + aristas repetidas (:HIJO_DE).[/]\n")

        # Consulta 1: Red de relaciones de Rick (Aliados, Companeros y Enemigos)
        query_rick = """
        MATCH (rick:Personaje {name: 'Rick Sanchez'})-[r]-(otro:Personaje)
        RETURN otro.name AS personaje, type(r) AS relacion, otro.rol AS rol, otro.dimension AS dimension
        ORDER BY relacion
        """
        relaciones_rick = session.run(query_rick).data()

        tabla_rick = Table(title="Neo4j: Entorno de Relaciones Directas de Rick Sanchez (C-137)", box=box.ROUNDED)
        tabla_rick.add_column("Personaje Conectado", style="cyan")
        tabla_rick.add_column("Tipo de Relacion", style="magenta")
        tabla_rick.add_column("Rol / Descripcion", style="yellow")
        tabla_rick.add_column("Dimension", style="white")

        for r in relaciones_rick:
            tabla_rick.add_row(r["personaje"], r["relacion"], str(r.get("rol", "-")), r["dimension"])

        console.print(tabla_rick)

        # Consulta 2: Demostracion de Relacion Repetida entre varios nodos (:HIJO_DE)
        query_hijos = """
        MATCH (descendiente:Personaje)-[:HIJO_DE]->(progenitor:Personaje)
        RETURN descendiente.name AS hijo, progenitor.name AS padre_madre
        ORDER BY padre_madre, hijo
        """
        hijos_data = session.run(query_hijos).data()

        tabla_hijos = Table(title="Neo4j: Relacion Repetida entre Nodos (:HIJO_DE - Arbol Familiar)", box=box.ROUNDED)
        tabla_hijos.add_column("Personaje (Hijo/a)", style="cyan")
        tabla_hijos.add_column("Tipo de Arista", style="magenta", justify="center")
        tabla_hijos.add_column("Padre / Madre", style="bold green")

        for h in hijos_data:
            tabla_hijos.add_row(h["hijo"], "-[:HIJO_DE]->", h["padre_madre"])

        console.print(tabla_hijos)

        # Consulta 3: Conflicto - ¿Por que Mr Meeseeks quiere eliminar a Jerry?
        query_meeseeks = """
        MATCH (m:Personaje {name: 'Mr Meeseeks'})-[r:QUIERE_ELIMINAR_A]->(j:Personaje {name: 'Jerry Smith'})
        RETURN m.name AS agresor, type(r) AS accion, j.name AS victima, r.motivo AS causa_filosofica
        """
        conflicto = session.run(query_meeseeks).data()

        tabla_conflicto = Table(title="Neo4j: Traversal de Conflicto Existencial", box=box.ROUNDED)
        tabla_conflicto.add_column("Agresor", style="bold red")
        tabla_conflicto.add_column("Accion", style="yellow")
        tabla_conflicto.add_column("Objetivo", style="bold cyan")
        tabla_conflicto.add_column("Motivo del Traversal", style="white")

        for c in conflicto:
            tabla_conflicto.add_row(c["agresor"], c["accion"], c["victima"], c["causa_filosofica"])

        console.print(tabla_conflicto)

    driver.close()
    return True


# =============================================================================
# 5. PARADIGMA DE SERIES TEMPORALES: InfluxDB
# CONCEPTO CLAVE: Ingesta masiva continua y analitica temporal en tiempo real
# EJEMPLO: Harry Potter - Sensores Magicos en Hogwarts (Gryffindor vs Slytherin)
# =============================================================================
def demo_influxdb():
    console.rule("[bold magenta]5. SERIES TEMPORALES - InfluxDB 2.x[/]")
    console.print("[italic white]Concepto: Telemetria continua por estampas de tiempo (Time-Series) optimizada para agregaciones analiticas.[/]\n")

    cfg = CONFIG["influxdb"]

    def connect():
        client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"], timeout=5000)
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"InfluxDB no saludable: {health.message}")
        return client

    client = retry_connection(connect, "InfluxDB")
    
    # Limpiar datos previos para visualizacion limpia en InfluxDB Data Explorer
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

    # Inyeccion de 30 puntos espaciados cada 3 minutos para dos ubicaciones magicas de Hogwarts
    ahora = datetime.now(timezone.utc)
    puntos = []
    total_puntos = 30

    for i in range(total_puntos):
        t = ahora - timedelta(minutes=(total_puntos - 1 - i) * 3)

        # ---------------------------------------------------------------------
        # 1. Torre de Gryffindor:
        # Actividad del Ejercito de Dumbledore practicando encantamientos clandestinos.
        # Patron: Hechizos crecientes con picos oscilantes y buena energia luminosa.
        # ---------------------------------------------------------------------
        hechizos_gryff = int(45 + 30 * math.sin(i / 3.5) + (i * 1.8))
        lumos_lux = round(80.0 + 15.0 * math.cos(i / 4.0), 1)
        dementores_gryff = round(max(0.0, 5.0 + 3.0 * math.sin(i / 2.0)), 1)

        puntos.append(
            Point("telemetria_hogwarts")
            .tag("ubicacion", "Torre-Gryffindor")
            .tag("castillo", "Hogwarts")
            .tag("sensor_magico", "Grimorio-Analitico-Gryffindor")
            .field("hechizos_por_minuto", max(10, hechizos_gryff))
            .field("energia_lumos_lux", lumos_lux)
            .field("presencia_dementores_pct", dementores_gryff)
            .time(t, WritePrecision.NS)
        )

        # ---------------------------------------------------------------------
        # 2. Mazmorras de Slytherin:
        # Actividad controlada de pociones, pero con una incursion abrupta de Dementores
        # patrullando entre los puntos 12 y 22 (frio espectral alto y caida de Lumos).
        # ---------------------------------------------------------------------
        if 12 <= i <= 22:
            # Dementores merodeando los pasillos de las mazmorras
            dementores_slyth = round(75.0 + ((i % 4) * 4.2), 1)
            lumos_slyth = round(15.0 - ((i % 3) * 2.1), 1)
            hechizos_slyth = int(120 + ((i % 5) * 15))  # Hechizos defensivos desesperados
        else:
            dementores_slyth = round(8.0 + ((i % 3) * 1.5), 1)
            lumos_slyth = round(45.0 + ((i % 4) * 2.0), 1)
            hechizos_slyth = int(25 + ((i % 3) * 8))

        puntos.append(
            Point("telemetria_hogwarts")
            .tag("ubicacion", "Mazmorras-Slytherin")
            .tag("castillo", "Hogwarts")
            .tag("sensor_magico", "Grimorio-Analitico-Slytherin")
            .field("hechizos_por_minuto", hechizos_slyth)
            .field("energia_lumos_lux", max(5.0, lumos_slyth))
            .field("presencia_dementores_pct", dementores_slyth)
            .time(t, WritePrecision.NS)
        )

    write_api.write(bucket=cfg["bucket"], org=cfg["org"], record=puntos)
    console.print(f"[green][OK] Inyectados {len(puntos)} registros de telemetria magica en '{cfg['bucket']}' (Castillo de Hogwarts).[/]")
    console.print("[dim]Nota visual: 'Torre-Gryffindor' muestra practica clandestina de hechizos; 'Mazmorras-Slytherin' muestra alerta por Dementores.[/]\n")

    # Consulta FLUX analitica: Ultimos registros de presencia de Dementores
    query_api = client.query_api()
    flux_query = f"""
    from(bucket: "{cfg['bucket']}")
      |> range(start: -2h)
      |> filter(fn: (r) => r["_measurement"] == "telemetria_hogwarts")
      |> filter(fn: (r) => r["_field"] == "presencia_dementores_pct")
      |> tail(n: 3)
    """
    tablas = query_api.query(flux_query, org=cfg["org"])

    tabla = Table(title="InfluxDB: Lectura Analitica de Presencia de Dementores en Hogwarts", box=box.ROUNDED)
    tabla.add_column("Hora (UTC)", style="white")
    tabla.add_column("Ubicacion", style="bold cyan")
    tabla.add_column("Sensor Magico", style="yellow")
    tabla.add_column("Presencia Dementores (%)", justify="right", style="bold red")

    for tbl in tablas:
        for record in tbl.records:
            t_str = record.get_time().strftime("%H:%M:%S")
            val = record.get_value()
            estilo = "bold red" if val > 50 else "bold green"
            tabla.add_row(t_str, record.values.get("ubicacion", "N/A"), record.values.get("sensor_magico", "N/A"), f"[{estilo}]{val:.1f}%[/]")

    console.print(tabla)
    client.close()
    return True


# =============================================================================
# 6. PARADIGMA FAMILIAS DE COLUMNAS (WIDE-COLUMN): Apache Cassandra
# CONCEPTO CLAVE: Big Data masivo de alta escritura (High-Write Throughput),
# particionado horizontal sin Master (Partition Key) y orden fisico en disco (Clustering Key).
# EJEMPLO: Fullmetal Alchemist / Ataque a los Titanes - Deteccion de Amenazas por Zona
# =============================================================================
def demo_cassandra():
    console.rule("[bold yellow]6. FAMILIAS DE COLUMNAS (WIDE-COLUMN) - Apache Cassandra[/]")
    console.print("[italic white]Concepto: Arquitectura descentralizada P2P, particionado distribuido (Partition Key) y ordenamiento fisico en disco (Clustering Key).[/]\n")

    cfg = CONFIG["cassandra"]

    def connect():
        cluster = Cluster([cfg["host"]], port=cfg["port"])
        session = cluster.connect()
        return cluster, session

    cluster, session = retry_connection(connect, "Cassandra")

    # 1. Crear Keyspace (equivalente a Database en SQL)
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {cfg['keyspace']}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};
    """)
    session.set_keyspace(cfg["keyspace"])

    # 2. Crear Tabla Columnar (Column Family)
    # DISENO CLAVE EXPLICADO A LA CLASE:
    # - PARTITION KEY: ((distrito)) -> Determina mediante hash (Murmur3Partitioner) que nodo del cluster almacena el registro.
    # - CLUSTERING KEY: fecha_registro DESC -> Guarda las filas FISICAMENTE ORDENADAS en disco (SSTable) por timestamp descendente.
    # - MAP<text, text>: Columnas dinamicas y sparse sin desperdiciar almacenamiento en NULLs.
    session.execute("""
        CREATE TABLE IF NOT EXISTS avistamientos_amenazas (
            distrito text,
            fecha_registro timestamp,
            id_avistamiento uuid,
            tipo_amenaza text,
            tamano_estimado_metros double,
            cantidad_avistada int,
            nivel_peligro text,
            alquimista_o_comandante text,
            detalles_tacticos map<text, text>,
            PRIMARY KEY ((distrito), fecha_registro, id_avistamiento)
        ) WITH CLUSTERING ORDER BY (fecha_registro DESC);
    """)

    # Limpiar datos previos de la tabla para ejecucion limpia
    session.execute("TRUNCATE avistamientos_amenazas;")

    # 3. Inyeccion Masiva de Eventos de Amenazas (Fullmetal Alchemist / Ataque a los Titanes)
    ahora = datetime.now(timezone.utc)
    insert_stmt = session.prepare("""
        INSERT INTO avistamientos_amenazas (
            distrito, fecha_registro, id_avistamiento, tipo_amenaza,
            tamano_estimado_metros, cantidad_avistada, nivel_peligro,
            alquimista_o_comandante, detalles_tacticos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """)

    amenazas = [
        # Distrito Shiganshina (Frontera sur - Muro Maria)
        (
            "Distrito Shiganshina", ahora - timedelta(minutes=45), uuid.uuid4(),
            "Titan Colosal", 60.0, 1, "APOCALIPTICO",
            "Capitan Levi Ackerman",
            {"vulnerabilidad": "Nuca posterior", "clima": "Tormenta de Vapor", "orden": "Evacuacion inmediata de civiles"}
        ),
        (
            "Distrito Shiganshina", ahora - timedelta(minutes=30), uuid.uuid4(),
            "Titan Acorazado", 15.0, 1, "EXTREMO",
            "Comandante Erwin Smith",
            {"vulnerabilidad": "Articulaciones descubiertas", "resistencia": "Placas de blindaje oseo endurecido"}
        ),
        (
            "Distrito Shiganshina", ahora - timedelta(minutes=10), uuid.uuid4(),
            "Horda de Titanes Puros", 14.0, 8, "ALTO",
            "Edward Elric (Alquimista de Acero)",
            {"tactica": "Creacion de trincheras y lanzas de piedra transmutada"}
        ),

        # Distrito Central Amestris (Cuartel General del Este / Central)
        (
            "Distrito Central Amestris", ahora - timedelta(minutes=50), uuid.uuid4(),
            "Homunculo (Envy)", 2.5, 1, "CRITICO",
            "Coronel Roy Mustang (Alquimista de Fuego)",
            {"habilidad": "Transmutacion de forma humana", "contramedida": "Ignicion masiva con guantes de chispa"}
        ),
        (
            "Distrito Central Amestris", ahora - timedelta(minutes=20), uuid.uuid4(),
            "Quimera Transmutada Quimica", 3.8, 3, "ALTO",
            "Alphonse Elric",
            {"observacion": "Fusion de leon con reptil", "estado": "Contenidas con alquimia defensiva"}
        ),

        # Distrito Trost (Muro Rose)
        (
            "Distrito Trost", ahora - timedelta(minutes=15), uuid.uuid4(),
            "Titan Anomalico Saltaril", 12.0, 2, "CRITICO",
            "Mikasa Ackerman",
            {"velocidad": "Impredecible", "equipo": "Maniobras tridimensionales de alta velocidad"}
        )
    ]

    for a in amenazas:
        session.execute(insert_stmt, a)

    console.print(f"[green][OK] Keyspace '{cfg['keyspace']}' y Column Family 'avistamientos_amenazas' inicializados.[/]")
    console.print(f"[green][OK] Inyectados {len(amenazas)} eventos de alta escritura con Partition Key y Clustering Key ordenadas en disco.[/]\n")

    # 4. CONSULTA OPTIMA DE CASSANDRA: Busqueda por Partition Key exacta
    # EXPLICACION CLAVE: Cassandra va directo al nodo responsable del 'Distrito Shiganshina' y lee secuencialmente
    # en disco por fecha_registro descendente sin hacer full-table scan.
    cql_shiganshina = """
        SELECT distrito, fecha_registro, tipo_amenaza, tamano_estimado_metros,
               cantidad_avistada, nivel_peligro, alquimista_o_comandante, detalles_tacticos
        FROM avistamientos_amenazas
        WHERE distrito = 'Distrito Shiganshina'
        LIMIT 5;
    """
    filas_shiganshina = list(session.execute(cql_shiganshina))

    tabla_cass = Table(title="Cassandra: Query Optima por Partition Key ('Distrito Shiganshina') ordenada por Clustering Key", box=box.ROUNDED)
    tabla_cass.add_column("Fecha/Hora (Descendente)", style="white")
    tabla_cass.add_column("Tipo Amenaza", style="bold red")
    tabla_cass.add_column("Tamano (m)", justify="right", style="cyan")
    tabla_cass.add_column("Cant", justify="center", style="yellow")
    tabla_cass.add_column("Peligro", justify="center", style="bold magenta")
    tabla_cass.add_column("Alquimista / Comandante", style="green")
    tabla_cass.add_column("Detalles Wide-Column (Map)", style="dim white")

    for f in filas_shiganshina:
        f_hora = f.fecha_registro.strftime("%H:%M:%S")
        detalles_str = ", ".join([f"{k}: {v}" for k, v in f.detalles_tacticos.items()]) if f.detalles_tacticos else "-"
        tabla_cass.add_row(
            f_hora, f.tipo_amenaza, f"{f.tamano_estimado_metros:.1f}m",
            str(f.cantidad_avistada), f.nivel_peligro, f.alquimista_o_comandante,
            detalles_str[:45] + ("..." if len(detalles_str) > 45 else "")
        )

    console.print(tabla_cass)

    # Visualizacion didactica de como se almacena la Familia de Columnas internamente
    arbol_cf = Tree("[bold yellow]Visualizacion Interna: ¿Como almacena Cassandra la Familia de Columnas?[/]")
    nodo_part = arbol_cf.add("[bold cyan]Partition Key (RowKey): 'Distrito Shiganshina'[/] [dim](Hash Murmur3 -> Determina el Nodo en el Cluster)[/]")
    
    for f in filas_shiganshina:
        f_hora = f.fecha_registro.strftime("%H:%M:%S")
        nodo_row = nodo_part.add(f"[bold magenta]Clustering Key ({f_hora})[/] -> [bold red]{f.tipo_amenaza}[/] ({f.tamano_estimado_metros}m)")
        nodo_row.add(f"[dim]Columnas Fijas:[/] cantidad={f.cantidad_avistada}, nivel_peligro='{f.nivel_peligro}', comandante='{f.alquimista_o_comandante}'")
        if f.detalles_tacticos:
            nodo_cols = nodo_row.add("[bold green]Columnas Dinamicas (Wide-Columns / Sparse):[/]")
            for k, v in f.detalles_tacticos.items():
                nodo_cols.add(f"[yellow]{k}:[/] [white]'{v}'[/]")

    console.print(arbol_cf)
    console.print("")
    panel_pedagogico = Panel(
        "[bold cyan]¿Cual es el beneficio EXACTO de Apache Cassandra frente a Relacional y Mongo?[/]\n\n"
        "[bold yellow]1. Arquitectura Sin Maestro (Masterless P2P):[/] No hay un nodo lider que sea cuello de botella.\n"
        "[bold yellow]2. Escrituras Masivas Brutales (LSM-Tree):[/] Escribe en Memtable (RAM) y CommitLog secuencial en milisegundos sin locks.\n"
        "[bold yellow]3. Partition Key:[/] 'distrito' distribuye los petabytes de datos entre decenas de servidores.\n"
        "[bold yellow]4. Clustering Key:[/] 'fecha_registro DESC' almacena las filas en orden fisico en disco. Buscar por distrito y rango de fechas es un Seek O(1).\n"
        "[bold red]5. Regla de Oro:[/] No existe 'JOIN'. Las tablas se disenan segun las consultas exactas que hara la aplicacion.",
        title="[bold green]Leccion Teorico-Practica: Column Families (Wide-Column)[/]",
        border_style="yellow"
    )
    console.print(panel_pedagogico)

    cluster.shutdown()
    return True


# =============================================================================
# EJECUCION PRINCIPAL
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Laboratorio Multi-Paradigma de Bases de Datos para Clases")
    parser.add_argument("--all", action="store_true", default=True, help="Ejecutar demostracion completa")
    parser.add_argument("--engine", choices=["postgres", "mongodb", "redis", "neo4j", "influxdb", "cassandra"], help="Ejecutar solo un motor especifico")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold white on blue]  LABORATORIO PRACTICO DE BASES DE DATOS - CLASE EN VIVO  [/]\n"
        "[italic cyan]Demostracion de los 6 Paradigmas Principales con Casos Reales y Pop-Culture[/]\n"
        "[dim]PostgreSQL (SQL) | MongoDB (Doc) | Redis (K-V) | Neo4j (Grafos) | InfluxDB (TS) | Cassandra (Wide-Column)[/]",
        border_style="cyan"
    ))

    motores = {
        "postgres": ("1. Relacional (SQL) -> Tablas estructuradas fijas e integridad ACID", demo_postgresql),
        "mongodb": ("2. Documental (NoSQL) -> Schema Evolution / Los Simpsons", demo_mongodb),
        "redis": ("3. Clave-Valor -> Acceso puntual O(1) con TTL / Death Note", demo_redis),
        "neo4j": ("4. Grafos -> Red de relaciones interdimensionales / Rick y Morty", demo_neo4j),
        "influxdb": ("5. Series Temporales -> Telemetria magica continua / Harry Potter", demo_influxdb),
        "cassandra": ("6. Familias de Columnas -> Big Data masivo / Fullmetal Alchemist & Titanes", demo_cassandra)
    }

    seleccionados = [args.engine] if args.engine else list(motores.keys())
    resumen = {}

    for clave in seleccionados:
        titulo, func = motores[clave]
        try:
            func()
            resumen[titulo] = "[bold green]EXITO (Sembrado y Consultado)[/]"
        except Exception as e:
            resumen[titulo] = f"[bold red]ERROR ({type(e).__name__}: {e})[/]"

    # Reporte final
    tabla_reporte = Table(title="Resumen Final para la Catedra", box=box.HEAVY_EDGE)
    tabla_reporte.add_column("Paradigma Demostrado", style="white")
    tabla_reporte.add_column("Estado", justify="center")

    for tit, est in resumen.items():
        tabla_reporte.add_row(tit, est)

    console.print("\n")
    console.print(Panel(tabla_reporte, border_style="green", title="[bold green]Reporte de Estado de los Motores[/]"))


if __name__ == "__main__":
    main()
