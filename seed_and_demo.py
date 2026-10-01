#!/usr/bin/env python3
"""
=============================================================================
LABORATORIO MULTI-PARADIGMA DE BASES DE DATOS
Script de Sembrado (Seed) y Demostración Funcional

Paradigmas:
  1. Relacional (SQL): PostgreSQL (Usuarios, Órdenes y Relaciones FK)
  2. Documental (NoSQL): MongoDB (Perfiles polimórficos y anidados)
  3. Clave-Valor: Redis (Sesiones con TTL, Rate-Limiting y Leaderboard)
  4. Grafos: Neo4j (Nodos Microservicios/Equipos y Análisis de Impacto)
  5. Series Temporales: InfluxDB (Telemetría de Servidores en tiempo real)
=============================================================================
"""

import sys
import os
import time
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Librerías de presentación en terminal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich import box

# Drivers de bases de datos
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
import redis
from neo4j import GraphDatabase
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

console = Console()

# =============================================================================
# CONFIGURACIÓN POR DEFECTO
# =============================================================================
CONFIG = {
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
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


def retry_connection(func, engine_name: str, max_retries: int = 5, delay: int = 3):
    """Ejecuta una función de conexión con reintentos para tolerar el arranque de contenedores."""
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                console.print(f"[bold red]✘ Fallo crítico conectando a {engine_name}:[/] {e}")
                raise e
            console.print(f"[yellow]⏳ Esperando a {engine_name} (intento {attempt}/{max_retries})...[/]")
            time.sleep(delay)


# =============================================================================
# 1. PARADIGMA RELACIONAL (SQL): PostgreSQL
# =============================================================================
def demo_postgresql():
    console.rule("[bold cyan]1. PARADIGMA RELACIONAL (SQL) - PostgreSQL[/]")
    cfg = CONFIG["postgres"]

    def connect():
        return psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            dbname=cfg["dbname"]
        )

    conn = retry_connection(connect, "PostgreSQL")
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    console.print("[dim]Inicializando esquema DDL (users, orders con FK)...[/]")
    cursor.execute("""
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS users CASCADE;

        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product VARCHAR(100) NOT NULL,
            amount NUMERIC(10, 2) NOT NULL,
            status VARCHAR(30) DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    console.print("[green]✔ Tablas DDL creadas exitosamente.[/]")

    # Seed
    users_data = [
        ("Marcos Gurruchaga", "marcos@example.com", "DevOps Lead"),
        ("Ana Gómez", "ana@example.com", "Cloud Architect"),
        ("Carlos Silva", "carlos@example.com", "Backend Engineer"),
    ]
    cursor.executemany("INSERT INTO users (name, email, role) VALUES (%s, %s, %s);", users_data)

    orders_data = [
        (1, "Suscripción AWS Cloud", 450.00, "completed"),
        (1, "Licencia Datadog Enterprise", 280.50, "completed"),
        (2, "Kubernetes Masterclass", 120.00, "completed"),
        (2, "Monitor UltraWide 4K", 850.00, "pending"),
        (3, "Teclado Mecánico Keychron", 140.00, "completed"),
    ]
    cursor.executemany("INSERT INTO orders (user_id, product, amount, status) VALUES (%s, %s, %s, %s);", orders_data)
    console.print(f"[green]✔ Sembrados {len(users_data)} usuarios y {len(orders_data)} órdenes con integridad referencial.[/]")

    # Query relacional representativa: JOIN + GROUP BY + Agregación
    cursor.execute("""
        SELECT 
            u.id AS user_id,
            u.name,
            u.role,
            COUNT(o.id) AS total_orders,
            COALESCE(SUM(o.amount), 0) AS total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.name, u.role
        ORDER BY total_spent DESC;
    """)
    results = cursor.fetchall()

    table = Table(title="PostgreSQL: Agregación Analítica (JOIN + SUM)", box=box.ROUNDED)
    table.add_column("ID", justify="center", style="cyan")
    table.add_column("Usuario", style="white")
    table.add_column("Rol", style="magenta")
    table.add_column("Órdenes", justify="right", style="green")
    table.add_column("Total Facturado (USD)", justify="right", style="bold yellow")

    for r in results:
        table.add_row(str(r["user_id"]), r["name"], r["role"], str(r["total_orders"]), f"${r['total_spent']:,.2f}")

    console.print(table)
    cursor.close()
    conn.close()
    return True


# =============================================================================
# 2. PARADIGMA DOCUMENTAL (NoSQL): MongoDB
# =============================================================================
def demo_mongodb():
    console.rule("[bold green]2. PARADIGMA DOCUMENTAL (NoSQL) - MongoDB[/]")
    cfg = CONFIG["mongodb"]
    uri = f"mongodb://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/"

    def connect():
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        return client

    client = retry_connection(connect, "MongoDB")
    db = client[cfg["dbname"]]
    collection = db["developer_profiles"]

    collection.delete_many({})
    console.print("[dim]Colección 'developer_profiles' limpiada.[/]")

    # Documentos polimórficos con datos semi-estructurados y anidados
    documents = [
        {
            "username": "mgurruchaga",
            "name": "Marcos Gurruchaga",
            "role": "DevOps Engineer",
            "skills": ["Docker", "Kubernetes", "Python", "Terraform", "PostgreSQL"],
            "experience_years": 6,
            "active_projects": [
                {"name": "Infrastructure Modernization", "tier": "mission-critical", "cloud": "AWS"},
                {"name": "NoSQL Database Lab", "tier": "internal", "cloud": "Hybrid"}
            ],
            "settings": {"dark_mode": True, "notifications": {"slack": True, "email": False}}
        },
        {
            "username": "agomez",
            "name": "Ana Gómez",
            "role": "Solutions Architect",
            "skills": ["Kubernetes", "AWS", "Go", "Distributed Systems", "MongoDB"],
            "experience_years": 8,
            "certifications": ["AWS Solution Architect Pro", "CKA"],
            "active_projects": [
                {"name": "Multi-region Failover", "tier": "mission-critical", "cloud": "GCP"}
            ],
            "settings": {"dark_mode": True}
        },
        {
            "username": "csilva",
            "name": "Carlos Silva",
            "role": "Full-Stack Dev",
            "skills": ["Node.js", "TypeScript", "React", "Redis", "Docker"],
            "experience_years": 3,
            "github_stats": {"public_repos": 35, "contributions_year": 1240}
        }
    ]

    res = collection.insert_many(documents)
    console.print(f"[green]✔ Insertados {len(res.inserted_ids)} perfiles polimórficos JSON BSON.[/]")

    # Query documental: Búsqueda flexible con operador `$all` en arrays y proyección
    query = {"skills": {"$all": ["Docker"]}}
    results = list(collection.find(query, {"name": 1, "role": 1, "skills": 1, "active_projects": 1, "_id": 0}))

    table = Table(title="MongoDB: Consulta Flexible sobre Campos Anidados (Filtro: skills con 'Docker')", box=box.ROUNDED)
    table.add_column("Nombre", style="white")
    table.add_column("Rol", style="magenta")
    table.add_column("Skills (Array)", style="cyan")
    table.add_column("Proyectos Activos (JSON Anidado)", style="yellow")

    for doc in results:
        skills_str = ", ".join(doc.get("skills", []))
        projects_count = len(doc.get("active_projects", []))
        proj_names = ", ".join([p["name"] for p in doc.get("active_projects", [])]) if projects_count else "N/A"
        table.add_row(doc["name"], doc["role"], skills_str, proj_names)

    console.print(table)
    client.close()
    return True


# =============================================================================
# 3. PARADIGMA CLAVE-VALOR: Redis
# =============================================================================
def demo_redis():
    console.rule("[bold red]3. PARADIGMA CLAVE-VALOR - Redis[/]")
    cfg = CONFIG["redis"]

    def connect():
        r = redis.Redis(host=cfg["host"], port=cfg["port"], password=cfg["password"], decode_responses=True)
        r.ping()
        return r

    r = retry_connection(connect, "Redis")

    # Caso de Uso A: Sesión de Usuario en Hash con TTL (Expiración automática)
    session_key = "session:usr_9942"
    r.hset(session_key, mapping={
        "user_id": "9942",
        "username": "mgurruchaga",
        "role": "admin",
        "ip_address": "192.168.1.45",
        "auth_timestamp": str(int(time.time()))
    })
    r.expire(session_key, 3600)  # TTL de 1 hora
    session_ttl = r.ttl(session_key)

    # Caso de Uso B: Rate Limiting / Contador atómico
    counter_key = "ratelimit:ip_192.168.1.45"
    r.delete(counter_key)
    r.incrby(counter_key, 1)
    r.incrby(counter_key, 3)
    r.expire(counter_key, 60)
    current_counter = r.get(counter_key)

    # Caso de Uso C: Leaderboard en tiempo real con Sorted Sets (ZSET)
    leaderboard_key = "leaderboard:devops_challenges"
    r.delete(leaderboard_key)
    r.zadd(leaderboard_key, {
        "Marcos Gurruchaga": 985.5,
        "Ana Gómez": 940.0,
        "Carlos Silva": 860.2,
        "David Tester": 720.0
    })
    top_leaders = r.zrevrange(leaderboard_key, 0, 2, withscores=True)

    # Mostrar resultados
    console.print(f"[green]✔ Sesión Hash guardada ({session_key}) con TTL: {session_ttl} segundos.[/]")
    console.print(f"[green]✔ Contador atómico ({counter_key}): {current_counter} peticiones registradas.[/]")

    session_data = r.hgetall(session_key)
    tree = Tree("[bold cyan]Redis: Inspección de Estructuras en Memoria[/]")
    s_node = tree.add(f"[bold yellow]Hash: {session_key} (TTL: {session_ttl}s)[/]")
    for k, v in session_data.items():
        s_node.add(f"[dim]{k}:[/] [white]{v}[/]")

    l_node = tree.add(f"[bold yellow]Sorted Set: {leaderboard_key} (Top 3)[/]")
    for rank, (player, score) in enumerate(top_leaders, start=1):
        l_node.add(f"#{rank} [green]{player}[/] -> [bold magenta]{score} pts[/]")

    console.print(tree)
    r.close()
    return True


# =============================================================================
# 4. PARADIGMA DE GRAFOS: Neo4j
# =============================================================================
def demo_neo4j():
    console.rule("[bold blue]4. PARADIGMA DE GRAFOS - Neo4j[/]")
    cfg = CONFIG["neo4j"]

    def connect():
        driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
        driver.verify_connectivity()
        return driver

    driver = retry_connection(connect, "Neo4j")

    with driver.session() as session:
        # Limpieza previa del grafo
        session.run("MATCH (n) DETACH DELETE n")
        console.print("[dim]Grafo anterior limpiado en Neo4j.[/]")

        # Creación de Nodos y Relaciones mediante Cypher
        # Caso de uso: Mapeo de microservicios, equipos de ingeniería y dependencias de arquitectura
        cypher_seed = """
        CREATE (devops:Team {name: 'DevOps & SRE', lead: 'Marcos Gurruchaga'})
        CREATE (backend:Team {name: 'Core Platform', lead: 'Ana Gómez'})
        CREATE (frontend:Team {name: 'Frontend Apps', lead: 'Carlos Silva'})

        CREATE (msAuth:Microservice {name: 'Auth-Service', tier: 'critical', language: 'Go'})
        CREATE (msPayment:Microservice {name: 'Payment-Gateway', tier: 'critical', language: 'Java'})
        CREATE (msCatalog:Microservice {name: 'Catalog-API', tier: 'standard', language: 'Python'})
        CREATE (msWeb:Microservice {name: 'Web-Portal', tier: 'frontend', language: 'TypeScript'})

        // Relaciones de Propiedad / Mantenimiento
        CREATE (devops)-[:MANAGES_INFRA]->(msAuth)
        CREATE (devops)-[:MANAGES_INFRA]->(msPayment)
        CREATE (backend)-[:OWNS_CODE]->(msAuth)
        CREATE (backend)-[:OWNS_CODE]->(msCatalog)
        CREATE (frontend)-[:OWNS_CODE]->(msWeb)

        // Relaciones de Dependencia entre Microservicios (DAG)
        CREATE (msWeb)-[:DEPENDS_ON {protocol: 'REST', latency_ms: 12}]->(msCatalog)
        CREATE (msWeb)-[:DEPENDS_ON {protocol: 'GraphQL', latency_ms: 25}]->(msAuth)
        CREATE (msWeb)-[:DEPENDS_ON {protocol: 'gRPC', latency_ms: 8}]->(msPayment)
        CREATE (msPayment)-[:DEPENDS_ON {protocol: 'gRPC', latency_ms: 5}]->(msAuth)
        """
        session.run(cypher_seed)
        console.print("[green]✔ Nodos (:Team, :Microservice) y Relaciones (:DEPENDS_ON, :OWNS_CODE) creados.[/]")

        # Consulta de Grafo: Análisis de Impacto en Cascada
        # "¿Si falla Auth-Service, qué servicios dependientes directa o indirectamente se ven afectados?"
        impact_query = """
        MATCH (target:Microservice {name: 'Auth-Service'})<-[:DEPENDS_ON*1..2]-(affected:Microservice)
        OPTIONAL MATCH (team:Team)-[:OWNS_CODE]->(affected)
        RETURN DISTINCT affected.name AS service, affected.tier AS tier, team.name AS team, team.lead AS lead
        ORDER BY affected.tier DESC
        """
        results = session.run(impact_query).data()

        table = Table(
            title="Neo4j: Análisis de Impacto en Cascada (Servicios afectados por fallo en Auth-Service)",
            box=box.ROUNDED
        )
        table.add_column("Servicio Afectado", style="cyan")
        table.add_column("Nivel de Criticidad", style="red")
        table.add_column("Equipo Responsable", style="yellow")
        table.add_column("Líder de Equipo", style="white")

        for row in results:
            table.add_row(row["service"], row["tier"], row["team"] or "N/A", row["lead"] or "N/A")

        console.print(table)

    driver.close()
    return True


# =============================================================================
# 5. PARADIGMA DE SERIES TEMPORALES: InfluxDB 2.x
# =============================================================================
def demo_influxdb():
    console.rule("[bold magenta]5. PARADIGMA SERIES TEMPORALES - InfluxDB 2.x[/]")
    cfg = CONFIG["influxdb"]

    def connect():
        client = InfluxDBClient(url=cfg["url"], token=cfg["token"], org=cfg["org"], timeout=5000)
        health = client.health()
        if health.status != "pass":
            raise ConnectionError(f"InfluxDB no saludable: {health.message}")
        return client

    client = retry_connection(connect, "InfluxDB")
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Inyección de Serie Temporal de Telemetría (con timestamps ordenados)
    console.print("[dim]Generando puntos de telemetría de infraestructura (pasadas 2 horas)...[/]")
    now = datetime.now(timezone.utc)

    # Generamos 10 puntos temporales con métricas de CPU, Memoria y Temperatura
    points = []
    base_cpu = 35.0
    base_mem = 60.0
    base_temp = 48.0

    for i in range(10):
        t = now - timedelta(minutes=(10 - i) * 6)
        cpu_val = round(base_cpu + (i * 2.5) + (i % 3), 2)
        mem_val = round(base_mem + (i * 1.8), 2)
        temp_val = round(base_temp + (i * 0.7), 2)

        point = (
            Point("server_telemetry")
            .tag("host", "srv-prod-docker-01")
            .tag("region", "sa-east-1")
            .tag("environment", "production")
            .field("cpu_usage_pct", cpu_val)
            .field("mem_usage_pct", mem_val)
            .field("temp_celsius", temp_val)
            .time(t, WritePrecision.NS)
        )
        points.append(point)

    write_api.write(bucket=cfg["bucket"], org=cfg["org"], record=points)
    console.print(f"[green]✔ Inyectados {len(points)} puntos temporales en el bucket '{cfg['bucket']}'.[/]")

    # Consulta con FLUX: Filtro por rango temporal, medición y campos
    query_api = client.query_api()
    flux_query = f"""
    from(bucket: "{cfg['bucket']}")
      |> range(start: -2h)
      |> filter(fn: (r) => r["_measurement"] == "server_telemetry")
      |> filter(fn: (r) => r["_field"] == "cpu_usage_pct" or r["_field"] == "mem_usage_pct")
      |> tail(n: 6)
    """
    tables = query_api.query(flux_query, org=cfg["org"])

    table = Table(
        title=f"InfluxDB: Registros de Serie Temporal recientes (Host: srv-prod-docker-01)",
        box=box.ROUNDED
    )
    table.add_column("Timestamp (UTC)", style="white")
    table.add_column("Métrica (_field)", style="cyan")
    table.add_column("Valor Registrado", justify="right", style="bold yellow")
    table.add_column("Región", style="magenta")

    for tbl in tables:
        for record in tbl.records:
            t_str = record.get_time().strftime("%H:%M:%S")
            table.add_row(t_str, record.get_field(), f"{record.get_value():.2f}", record.values.get("region", "N/A"))

    console.print(table)
    client.close()
    return True


# =============================================================================
# EJECUCIÓN PRINCIPAL Y RESUMEN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Laboratorio Multi-Paradigma de Bases de Datos")
    parser.add_argument("--all", action="store_true", default=True, help="Ejecutar demostración de las 5 bases de datos")
    parser.add_argument("--engine", choices=["postgres", "mongodb", "redis", "neo4j", "influxdb"], help="Ejecutar sólo un motor específico")
    args = parser.parse_args()

    console.print(Panel.fit(
        "[bold white on blue]  LABORATORIO MULTI-PARADIGMA DE BASES DE DATOS  [/]\n"
        "[italic cyan]Verificación de Integración, Sembrado y Consulta Funcional[/]",
        border_style="cyan"
    ))

    engines = {
        "postgres": ("Relacional (SQL)", demo_postgresql),
        "mongodb": ("Documental (NoSQL)", demo_mongodb),
        "redis": ("Clave-Valor", demo_redis),
        "neo4j": ("Grafos", demo_neo4j),
        "influxdb": ("Series Temporales", demo_influxdb)
    }

    selected = [args.engine] if args.engine else list(engines.keys())
    results_summary = {}

    for eng in selected:
        title, func = engines[eng]
        try:
            success = func()
            results_summary[title] = "[bold green]OK (Sembrado & Validado)[/]"
        except Exception as e:
            results_summary[title] = f"[bold red]ERROR ({type(e).__name__})[/]"

    # Resumen final en tabla
    summary_table = Table(title="Resumen General del Laboratorio", box=box.HEAVY_EDGE)
    summary_table.add_column("Paradigma / Motor", style="white")
    summary_table.add_column("Estado de Verificación", justify="center")

    for title, status in results_summary.items():
        summary_table.add_row(title, status)

    console.print(Panel(summary_table, border_style="green", title="[bold green]Reporte de Ejecución[/]"))


if __name__ == "__main__":
    main()
