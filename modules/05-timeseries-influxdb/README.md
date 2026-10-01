# Paradigma de Series Temporales - InfluxDB 2.x

## 1. Concepto y Filosofía
Una base de datos de series temporales (TSDB) está optimizada para almacenar y consultar pares de datos `(timestamp, valor)` a velocidades masivas de ingestión. Cuenta con algoritmos de compresión específicos (como Gorilla o delta-of-delta) y políticas de retención automática de datos (downsampling / data lifecycle).

### ¿Cuándo usarlo?
- Monitoreo de infraestructura y DevOps (CPU, memoria, latencias, throughput, logs de red).
- Internet de las Cosas (IoT) y telemetría de sensores industriales (temperatura, presión, vibración).
- Análisis de mercados financieros (precios de acciones tick-by-tick, crypto).
- Métricas de uso de producto y análisis de eventos continuos.

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
