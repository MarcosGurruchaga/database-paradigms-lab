# Paradigma de Series Temporales y Columnar - InfluxDB 2.x

## 1. Concepto Pedagogico: "Muchos datos para analizar" (Estilo BigQuery / TSDB)
En los sistemas transaccionales tradicionales (OLTP como PostgreSQL), los datos se leen fila por fila. Si tienes **10 millones de registros de telemetria o ventas** y quieres calcular el promedio o la suma de una columna, el motor tradicional sufre un cuello de botella brutal leyendo filas completas de disco.

### ¿Por que el Enfoque Columnar / Time-Series (InfluxDB / BigQuery)?
- **Almacenamiento por Columnas:** Solo se leen de disco las columnas que entran en la consulta (ej. `cpu_utilizada_pct` o `peticiones_por_seg`), ignorando el resto.
- **Compresion masiva:** Al tener millones de numeros continuos en una misma columna, algoritmos como *Gorilla* comprimen hasta un 90% el espacio.
- **Analitica Vectorizada:** Diseñado especificamente para agregaciones matematicas masivas (`mean()`, `sum()`, `max()`, `percentile()`) sobre grandes volumenes de series de tiempo.

---

## 2. Configuracion en el Laboratorio
- **Motor:** `InfluxDB 2.7 Alpine`
- **Puerto:** `8086`
- **Volumen local:** `./data/influxdb`
- **Organizacion:** `devops-lab`
- **Bucket:** `telemetry-bucket`
- **Token Admin:** `lab-super-secret-admin-token-2026`
- **Dashboard Web:** InfluxDB Web UI nativo en [http://localhost:8086](http://localhost:8086)
  - **Usuario:** `influxadmin`
  - **Contrasena:** `influxpassword123`

---

## 3. Demostracion Visual en InfluxDB Data Explorer

Para mostrar la comparacion en la clase en vivo dentro de [http://localhost:8086](http://localhost:8086):

1. Ve a la pestana **Data Explorer** (icono de graficos en el menu izquierdo).
2. En el panel inferior:
   - **FROM:** Selecciona `telemetry-bucket`.
   - **_measurement:** Selecciona `metricas_servidores`.
   - **_field:** Selecciona `cpu_utilizada_pct` (o `memoria_utilizada_pct` o `peticiones_por_seg`).
   - **host:** Marca ambos casilleros (`srv-prod-latam-01` y `srv-prod-latam-02`).
3. En la esquina superior derecha, selecciona el rango de tiempo: **Past 2h** (o **Past 1h**).
4. Haz clic en el boton azul **SUBMIT**.

### ¿Que veras en el Grafico? (Diferenciacion para los Alumnos)
* **`srv-prod-latam-01` (Linea azul/verde - Servidor Web API):** Curva suave y oscilatoria que refleja el flujo diario organico de trafico de usuarios (30% a 72% de CPU).
* **`srv-prod-latam-02` (Linea naranja/purpura - Servidor Batch Worker):** Linea base muy baja y fria (20% CPU) que repentinamente sufre un **pico abrupto sostenido al 88% de CPU** cuando se procesa un lote de tareas pesadas, y luego cae a reposo.

---

## 4. Consulta Directa con Lenguaje FLUX
```flux
from(bucket: "telemetry-bucket")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metricas_servidores")
  |> filter(fn: (r) => r["_field"] == "cpu_utilizada_pct")
  |> yield(name: "comparativa_cpu")
```
