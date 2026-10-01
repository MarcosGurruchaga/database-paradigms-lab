# Paradigma Clave-Valor - Redis

## 1. Concepto Pedagogico: "Recuperar datos facilmente puntuales"
El paradigma clave-valor no tiene tablas complejas ni indices multidimensionales: los datos estan indexados exclusivamente por una **Clave unica**.
Opera directamente en **memoria RAM**, logrando latencias inferiores a 1 milisegundo ($O(1)$).

### ¿Por que triunfa en datos puntuales?
Si tu aplicacion necesita consultar en cada peticion HTTP:
- "¿Cual es el usuario detras de este Token de Sesion?"
- "¿Esta habilitado el Feature Flag de Mantenimiento?"
- "¿Cuantas visitas tiene este articulo?"
Redis responde de forma instantanea sin sobrecargar la base de datos transaccional (SQL).

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
