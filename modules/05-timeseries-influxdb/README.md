# Paradigma de Series Temporales y Columnar - InfluxDB 2.x

## 1. Concepto Pedagogico: "Muchos datos continuos para analizar"
En los motores relacionales (OLTP como PostgreSQL), los datos se leen fila por fila. Si tienes millones de eventos de telemetria continua y quieres calcular promedios o agregaciones, el motor sufre un cuello de botella brutal leyendo filas completas de disco.

InfluxDB y los motores de series temporales (con almacenamiento columnar) resuelven esto:
- **Almacenamiento por Columnas:** Solo lee de disco las columnas que entran en la consulta (ej. `presencia_dementores_pct` o `hechizos_por_minuto`).
- **Compresion Extrema (Gorilla):** Comprime hasta un 90% del espacio al tratar con numeros continuos sobre el tiempo.
- **Agregaciones Vectorizadas:** Diseñado para calcular medias, percentiles y sumas en microsegundos.

---

## 2. Ejemplo Divertido para la Clase: Telemetria Magica en Hogwarts (Harry Potter)
Modelamos sensores analiticos distribuidos en el castillo de Hogwarts monitoreando dos ambientes en disputa:
- **`Torre-Gryffindor`:** Practica clandestina de encantamientos del Ejercito de Dumbledore. Observamos curvas suaves crecientes de `hechizos_por_minuto` y niveles altos de energia luminosa (`energia_lumos_lux`).
- **`Mazmorras-Slytherin`:** Actividad calculada habitual, pero con una incursion abrupta de **Dementores** patrullando las mazmorras: la `presencia_dementores_pct` salta de 8% a mas de 75%, el nivel de Lumos colapsa y se registran hechizos defensivos desesperados.

---

## 3. Configuracion en el Laboratorio
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

## 4. Demostracion Visual en InfluxDB Data Explorer

Para proyectar las metricas en vivo a los alumnos dentro de [http://localhost:8086](http://localhost:8086):

1. Ve a la pestana **Data Explorer** (icono de graficos en el menu izquierdo).
2. En el panel inferior:
   - **FROM:** Selecciona `telemetry-bucket`.
   - **_measurement:** Selecciona `telemetria_hogwarts`.
   - **_field:** Selecciona `presencia_dementores_pct` (o `hechizos_por_minuto`).
   - **ubicacion:** Marca ambos casilleros (`Torre-Gryffindor` y `Mazmorras-Slytherin`).
3. En la esquina superior derecha, selecciona el rango de tiempo: **Past 2h** (o **Past 1h**).
4. Haz clic en el boton azul **SUBMIT**.

---

## 5. Consulta Directa con Lenguaje FLUX
```flux
from(bucket: "telemetry-bucket")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "telemetria_hogwarts")
  |> filter(fn: (r) => r["_field"] == "presencia_dementores_pct")
  |> yield(name: "alerta_dementores")
```
