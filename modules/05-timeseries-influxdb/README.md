# Paradigma de Series Temporales y Columnar - InfluxDB 2.x

## 1. Concepto Pedagogico: "Muchos datos para analizar" (Estilo BigQuery / TSDB)
En los sistemas transaccionales tradicionales (OLTP como PostgreSQL), los datos se leen fila por fila. Si tienes **10 millones de registros de telemetria o ventas** y quieres calcular el promedio o la suma de una columna, el motor tradicional sufre un cuello de botella brutal leyendo filas completas de disco.

### ¿Por que el Enfoque Columnar / Time-Series (InfluxDB / BigQuery)?
- **Almacenamiento por Columnas:** Solo se leen de disco las columnas que entran en la consulta (ej. `cpu_utilizada` o `peticiones_por_seg`), ignorando el resto.
- **Compresion masiva:** Al tener millones de numeros del mismo tipo en una misma columna, algoritmos como *Gorilla* o *Delta-of-Delta* comprimen los datos hasta un 90%.
- **Analitica Vectorizada:** Diseñado especificamente para aggregations masivas (`mean()`, `sum()`, `max()`, `percentile()`) sobre inmensos volumenes de informacion.

---

## 2. Configuración en el Laboratorio
- **Motor:** `InfluxDB 2.7 Alpine`
- **Puerto:** `8086`
- **Volumen local:** `./data/influxdb`
- **Organización:** `devops-lab`
- **Bucket:** `telemetry-bucket`
- **Token Admin:** `lab-super-secret-admin-token-2026`
- **Dashboard Web:** InfluxDB Web UI nativo en [http://localhost:8086](http://localhost:8086)
  - **Usuario:** `influxadmin`
  - **Contraseña:** `influxpassword123`

---

## 3. Modelo de Datos Influx Line Protocol
```text
server_telemetry,host=srv-prod-docker-01,region=sa-east-1 cpu_usage_pct=42.5,mem_usage_pct=64.2 1727788800000000000
```

### Consulta con Lenguaje Flux
```flux
from(bucket: "telemetry-bucket")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "server_telemetry")
  |> filter(fn: (r) => r["_field"] == "cpu_usage_pct" or r["_field"] == "mem_usage_pct")
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```
En el Data Explorer de InfluxDB (`http://localhost:8086`), puedes graficar en tiempo real líneas de tendencia, histogramas y medidores (gauges).
