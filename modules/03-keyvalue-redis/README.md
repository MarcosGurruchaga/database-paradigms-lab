# Paradigma Clave-Valor - Redis

## 1. Concepto Pedagogico: "Recuperar datos facilmente puntuales"
El paradigma clave-valor almacena datos directamente en **memoria RAM** indexados unicamente por una **Clave unica**, permitiendo tiempos de respuesta en sub-milisegundos ($O(1)$).

### ¿Por que triunfa en datos puntuales?
Permite resolver consultas criticas y frecuentes sin sobrecargar la base de datos relacional (PostgreSQL):
- Sesiones de usuarios con tiempo de vida (TTL).
- Feature flags y variables globales del sistema.
- Contadores atómicos masivos sin bloqueos de tabla.
- Rankings o tablas de puntuaciones ordenadas en tiempo real (*Sorted Sets*).

---

## 2. Ejemplo Divertido para la Clase: Death Note
Para explicar las estructuras y los tiempos de expiracion (TTL), usamos la tematica del anime **Death Note**:

1. **Hash con TTL de 40 Segundos (Regla Fundamental del Death Note):**
   > *"Si la causa de la muerte no es especificada en 40 segundos, la persona morira de un paro cardiaco."*
   ```text
   HSET deathnote:victima:kuro_otoishi nombre "Kuro Otoishi" crimen "Secuestro" causa "Paro cardiaco"
   EXPIRE deathnote:victima:kuro_otoishi 40
   ```
   En RedisInsight se puede observar la barra de tiempo regresiva de la clave consumiendose segundo a segundo.

2. **Strings Puntuales (Reglas del Shinigami Ryuk):**
   ```text
   SET deathnote:regla:01 "La persona cuyo nombre sea escrito en esta libreta morira."
   GET deathnote:regla:01
   ```

3. **Contador Atomico (INCRBY):**
   ```text
   INCRBY kira:contador:criminales_eliminados 1
   ```
   Opera en nanosegundos en memoria sin transacciones costosas.

4. **Sorted Set - ZSET (Probabilidades de sospechosos de L):**
   ```text
   ZADD cuartel_l:probabilidad_ser_kira 96.8 "Light Yagami" 88.5 "Misa Amane" 0.05 "Matsuda"
   ZREVRANGE cuartel_l:probabilidad_ser_kira 0 2 WITHSCORES
   ```

---

## 3. Configuracion en el Laboratorio
- **Motor:** `Redis 7.4 Alpine`
- **Puerto:** `6379`
- **Volumen local:** `./data/redis`
- **Dashboard Web:** RedisInsight en [http://localhost:5540](http://localhost:5540)
  - Datos de conexion directa:
    - **Host:** `redis` (o `127.0.0.1`)
    - **Puerto:** `6379`
    - **Password:** `redispassword`
    - **Connection URL:** `redis://default:redispassword@localhost:6379`
