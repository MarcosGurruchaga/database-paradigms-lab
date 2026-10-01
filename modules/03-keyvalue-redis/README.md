# Paradigma Clave-Valor - Redis

## 1. Concepto y Filosofía
El paradigma clave-valor almacena datos indexados exclusivamente por una clave única. Redis opera primordialmente **en memoria RAM**, ofreciendo latencias de lectura/escritura en sub-milisegundos con persistencia opcional (RDB / AOF). Soporta estructuras de datos avanzadas (Strings, Hashes, Lists, Sets, Sorted Sets, Bitmaps, HyperLogLogs).

### ¿Cuándo usarlo?
- Caché de resultados computacionalmente costosos o consultas lentas.
- Almacenamiento de sesiones web con tiempo de vida (TTL / Expiración automática).
- Rate-Limiting para prevenir ataques DDoS o abusos de API.
- Tablas de clasificación en tiempo real (Leaderboards) usando Sorted Sets.
- Mensajería pub/sub y colas de tareas ligeras.

---

## 2. Configuración en el Laboratorio
- **Motor:** `Redis 7.4 Alpine`
- **Puerto:** `6379`
- **Volumen local:** `./data/redis`
- **Dashboard Web:** RedisInsight en [http://localhost:5540](http://localhost:5540)
  - En RedisInsight, añade la conexión con:
    - **Host:** `redis` (o `localhost`)
    - **Port:** `6379`
    - **Password:** `redispassword`

---

## 3. Estructuras y Comandos Demostrados
1. **Hash con TTL (Sesión de Usuario):**
   ```text
   HSET session:usr_9942 user_id "9942" username "mgurruchaga" role "admin"
   EXPIRE session:usr_9942 3600
   TTL session:usr_9942
   ```

2. **Contador Atómico (Rate Limiter):**
   ```text
   INCRBY ratelimit:ip_192.168.1.45 1
   EXPIRE ratelimit:ip_192.168.1.45 60
   ```

3. **Sorted Set (Leaderboard en Tiempo Real):**
   ```text
   ZADD leaderboard:devops_challenges 985.5 "Marcos Gurruchaga" 940.0 "Ana Gómez"
   ZREVRANGE leaderboard:devops_challenges 0 2 WITHSCORES
   ```
