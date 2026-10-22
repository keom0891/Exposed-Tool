# Población expuesta a amenazas RP100 — El Salvador

Fecha: 21 de octubre de 2026. Escenario base con los umbrales operativos documentados.

## Resultado principal

De 6.352.401 habitantes modelados por WorldPop 2025, **6.349.122 (99,95%)** se localizan en áreas expuestas a una o más amenazas. La unión cuenta cada habitante una sola vez.

Para dos o más amenazas, el resultado es **5.351.946 habitantes (84,25%)**. Ambas definiciones se mantienen separadas.

| Escenario | Total expuesta | Pobre expuesta | No pobre expuesta | % de población total |
|---|---:|---:|---:|---:|
| Inundación ≥0,1 m | 76.273 | 38.567 | 37.706 | 1,20% |
| PGA ≥0,10 g | 6.345.298 | 1.756.162 | 4.589.136 | 99,89% |
| Viento huracanado ≥20 m/s | 2.967.809 | 916.107 | 2.051.702 | 46,72% |
| WBGT ≥30 °C | 5.131.930 | 1.339.398 | 3.792.532 | 80,79% |
| Una o más amenazas | 6.349.122 | 1.757.989 | 4.591.133 | 99,95% |
| Exactamente 0 amenazas | 3.279 | 1.971 | 1.308 | 0,05% |
| Exactamente 1 amenazas | 997.176 | 337.699 | 659.477 | 15,70% |
| Exactamente 2 amenazas | 2.588.291 | 578.875 | 2.009.416 | 40,75% |
| Exactamente 3 amenazas | 2.707.070 | 810.877 | 1.896.193 | 42,61% |
| Exactamente 4 amenazas | 56.586 | 30.539 | 26.047 | 0,89% |

## Comparación por grupo poblacional

| Grupo | Población base | Una o más amenazas | % del propio grupo | Dos o más amenazas | % del propio grupo |
|---|---:|---:|---:|---:|---:|
| Total | 6.352.401 | 6.349.122 | 99,95% | 5.351.946 | 84,25% |
| Pobre | 1.759.960 | 1.757.989 | 99,89% | 1.420.290 | 80,70% |
| No pobre | 4.592.441 | 4.591.133 | 99,97% | 3.931.656 | 85,61% |

## Lectura del resultado

El mapa sísmico tiene un mínimo válido de 0,20139 g, superior al umbral base 0,10 g. Por eso el sismo por sí solo comprende 99,89% de la población. Esta característica de los datos y el criterio de exposición explica buena parte de la unión cercana a 100%; no equivale a que toda esa población sufrirá daños.

Los porcentajes representan exposición potencial a los mapas suministrados. No son probabilidades individuales de daño ni un evento multiamenaza conjunto RP100. Los totales son estimaciones modeladas; las tablas se redondean solo para presentación.

## Sensibilidad documentada

Se evaluaron las 81 combinaciones de profundidad 0,1/0,2/0,3 m; PGA 0,1/0,2/0,3 g; viento 20/25/33 m/s; y WBGT ≥28/≥30/≥32 °C. Se evalúan todas las combinaciones de los niveles documentados, sin seleccionar escenarios por el porcentaje obtenido.

Una o más amenazas: **83.18%–100.00%**. Dos o más amenazas: **6.29%–99.93%**. El extremo superior de una o más amenazas es 99,9954%, aunque al redondear a dos decimales aparezca 100,00%.

Los umbrales sísmicos 0,10 y 0,20 g están por debajo del mínimo válido del mapa (0,20139 g) y generan la misma máscara. El escenario base usa 0,10 g; el nivel de 0,30 g reduce la exposición sísmica. La sensibilidad no constituye una validación del modelo de amenaza.

## Reglas aplicadas

- Soporte: centros de las celdas WorldPop positivas, no hexágonos agregados. Muestreo de la celda contenedora en cada grilla nativa; es una aproximación puntual que no reparte por área las celdas fronterizas.
- Se conserva la suma nacional de WorldPop. Los centros fuera de límites se asignan al municipio más cercano en UTM 16N, con desempate determinista.
- RWI del punto más cercano, con distancia y error original conservados en el detalle. Ranking ponderado por población y fracción común para los empates en el corte de pobreza.
- Las tasas municipales originales se aceptan para población 2025. Las faltantes se imputan por promedio simple de vecinos con tasa original y segmento de límite compartido. No se promedian otras imputaciones.
- NoData o ausencia de cobertura de una amenaza implica cero exposición a esa amenaza, como criterio operativo del análisis; los indicadores de dato válido se conservan. No significa una comprobación independiente de ausencia de peligro.
- Se usan los 266 polígonos de la fuente territorial, incluidos cuatro cuerpos de agua sin población asignada. No se actualiza la división administrativa.

## Tasas imputadas

| Unidad | Tasa imputada | Vecinos con tasa original |
|---|---:|---|
| Embalse Cerron Grande (SV0399) | 34.1123% | Cinquera, Jutiapa, Sensuntepeque, Azacualpa, Chalatenango, El Paraíso, La Reina, Nombre de Jesús, Nueva Concepción, Potonico, San Antonio de la Cruz, San Francisco Lempa, San Isidro Labrador, San José Cancasque, San Luis del Carmen, San Miguel de Mercedes, San Rafael, Santa Rita, Tejutla, Suchitoto, El Paisnal |
| La Libertad (SV0509) | 33.3041% | Comasagua, Huizúcar, Nueva San Salvador, San José Villanueva, Tamanique, Zaragoza, Olocuilta, San Luis Talpa, Panchimalco, Rosario de Mora |
| Lago de Llopango (SV1099) | 31.4108% | Candelaria, San Pedro Perulapán, San Emigdio, San Francisco Chinameca, San Miguel Tepezontes, Ilopango, Santiago Texacuangos |
| San Martín (SV1013) | 28.7577% | Oratorio de Concepción, San Bartolomé Perulapía, San José Guayabal, San Pedro Perulapán, Ilopango, Tonacatepeque |
| Lago de Coatepeque (SV1299) | 25.4593% | El Congo, Santa Ana |
| Lago de Guija (SV1298) | 23.6076% | Metapán, San Antonio Pajonal |

## Cobertura y controles

Asignación al municipio más cercano: 28.511 habitantes en 14.762 celdas. Distancia máxima: 6679.0 m.

Población sobre ausencia de dato válido de amenaza (tratada como cero exposición):
- Inundación ≥0,1 m: 6.276.128 habitantes; de ellos 16 fuera de la extensión del archivo.
- PGA ≥0,10 g: 7.103 habitantes; de ellos 34 fuera de la extensión del archivo.
- Viento huracanado ≥20 m/s: 72.883 habitantes; de ellos 898 fuera de la extensión del archivo.
- WBGT ≥30 °C: 0 habitantes; de ellos 0 fuera de la extensión del archivo.

Todos los balances pasaron con errores menores a 0,00001 personas: calibración municipal, pobre + no pobre = total, categorías 0–4 = población y categorías 1–4 = unión. Seis pruebas unitarias verificaron empates, ponderación poblacional, tasas extremas, operadores y conteo de la unión.

## Limitaciones

La resolución de WBGT es aproximadamente 27 km, de viento 2 km y de población/inundación unos 100 m. No deben interpretarse las diferencias municipales o el RWI asignado a 100 m como observaciones a esa escala. La capa WBGT registra un tratamiento previo por vecino válido cercano. Las fechas y definiciones originales de las amenazas proceden de los archivos y de las definiciones adoptadas para este ejercicio, sin validación independiente del modelo.

## Archivos entregados

- `index.html`: dashboard autónomo, funciona sin internet.
- `03_resultados/escenario_base/indicadores.csv`: resultados nacionales y por unidad, por amenaza, unión y 0–4 amenazas.
- `03_resultados/escenario_base/municipios.csv`: atributos completos por unidad.
- `03_resultados/escenario_base/sensibilidad.csv`: las 81 combinaciones completas.
- `03_resultados/escenario_base/resultados_municipales.gpkg`: resultados espaciales.
- `03_resultados/escenario_base/poblacion_y_exposicion.tif`: población total/pobre/no pobre, número de amenazas y combinación en bits.
- `03_resultados/escenario_base/celdas.csv.gz`: detalle por celda con RWI, distancias, grupo poblacional, exposición y cobertura.
- `03_resultados/escenario_base/auditoria.json`: parámetros, reglas, versiones, verificaciones y hashes de insumos.
- `03_resultados/escenario_base/tasas_imputadas.json` y `asignaciones_fuera_limites.csv`: trazabilidad de decisiones espaciales.

## Diseño

El dashboard utiliza la identidad visual del Grupo BID: logo oficial vectorial en español, fuente Inter incluida localmente con licencia SIL Open Font License, diseño editorial petróleo/cian , con superficies claras y escala secuencial petróleo/cian. Los mapas mostrados se simplifican solo para visualización; los cálculos usan las geometrías originales.
