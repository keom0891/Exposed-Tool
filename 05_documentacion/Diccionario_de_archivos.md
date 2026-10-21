# Archivos de resultados

Todos los resultados vigentes están en `03_resultados/escenario_base`.

- `indicadores.csv`: país y unidad territorial; categoría, población total/pobre/no pobre y porcentaje de cada grupo.
- `municipios.csv`: una fila por unidad territorial, tasas utilizadas y atributos de exposición.
- `resultados_municipales.gpkg`: la misma información con polígonos originales, sin simplificación de visualización.
- `celdas.csv.gz`: detalle de celdas positivas de WorldPop; fila/columna, coordenadas, municipio, total/pobre/no pobre, RWI, error original y distancias, indicadores de exposición, validez del dato y número de amenazas.
- `poblacion_y_exposicion.tif`: cinco bandas en la grilla WorldPop: total, pobre, no pobre, número de amenazas y combinación en bits (inundación 1, sismo 2, viento 4, calor 8). NoData = -99999. Se conserva precisión Float64 en los cálculos y CSV; el GeoTIFF exporta Float32.
- `sensibilidad.csv`: las 180 combinaciones nacionales y sus porcentajes por grupo.
- `sensibilidad_resumen.json`: niveles, escenario base y rangos de sensibilidad.
- `tasas_imputadas.json`: vecinos, tasas originales y promedio usado.
- `asignaciones_fuera_limites.csv`: centros asignados por municipio más cercano, población y distancia.
- `auditoria.json`: parámetros, reglas, suma poblacional, verificaciones, versiones y hashes de insumos.

El HTML autónomo incluye los resultados municipales agregados, geometrías simplificadas solo para visualización y la sensibilidad nacional. No necesita los archivos de detalle para abrirse.

## Actualización y controles

- `ACTUALIZAR_DASHBOARD.cmd`: reconstruye la presentación sin recalcular el análisis.
- `02_codigo/verificar.py`: reconstrucción independiente de población, calibración, asignaciones espaciales y exposición; verifica sensibilidad y ejecuta seis pruebas unitarias.
- `03_resultados/escenario_base/revision_independiente.json`: resultados de esos controles.
- `calibracion_municipal.json`: distribución real por RWI y corte por unidad territorial.
- `calibracion_datos.js`: copia generada para consulta en el dashboard.

## Entorno y presentación


