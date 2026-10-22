# Metodología vigente

Área: El Salvador, con los 266 polígonos de la capa de pobreza suministrada. Incluye cuerpos de agua y no actualiza la división administrativa.

## Población y asignación espacial

Se conservan las celdas positivas del ráster WorldPop 2025 y su valor de habitantes por celda. Se asigna el municipio que contiene su centro; si queda fuera de los límites, se usa el más cercano. Las distancias se miden en UTM 16N. El punto RWI más cercano aporta el valor relativo de riqueza; los empates de distancia se resuelven por orden de fila del CSV.

Este muestreo puntual no equivale a repartir la población por el área exacta de intersección de cada celda. La información no se agrega previamente a hexágonos.

## Tasas municipales y pobreza por RWI

Se aceptan las tasas de 2019. Para una tasa faltante, se calcula el promedio simple de las tasas originales disponibles de unidades con un segmento de límite compartido; si no existen, se revisa contacto puntual. No se realimentan las imputaciones.

Dentro del municipio m se ordenan las celdas por RWI, de menor a mayor, ponderando por población Pᵢ:

Fₘ(r) = Σ[Pᵢ · 1(RWIᵢ ≤ r)] / ΣPᵢ.

El RWI de corte corresponde al percentil de la tasa qₘ. Bajo el corte, sᵢ = 1; sobre el corte, sᵢ = 0. En el corte, todos los empates reciben la misma fracción θ:

θ = (qₘPₘ − población bajo el corte) / población en el corte.

Pobreᵢ = Pᵢsᵢ; no pobreᵢ = Pᵢ(1 − sᵢ). Se verifica ΣPobreᵢ = qₘPₘ por municipio. Es una asignación espacial modelada, no una identificación individual.

## Máscaras de amenaza

El análisis utiliza los cuatro mapas como escenarios RP100; no verifica de forma independiente los modelos originales. Se consulta el píxel contenedor del centro WorldPop en cada grilla nativa. Se transforma el CRS cuando corresponde y no se recortan índices fuera de rango a los bordes.

| Amenaza | Escenario base |
|---|---|
| Inundación | Profundidad ≥0,1 m |
| Sismo | PGA ≥0,10 g |
| Viento huracanado | Viento huracanado ≥33 m/s |
| Calor | WBGT ≥30 °C |

Ausencia de cobertura o NoData se interpreta como cero exposición a esa amenaza, como criterio operativo. La población se conserva. Los indicadores de dato válido se mantienen en el detalle.

## Unión y número de amenazas

La unión es el máximo de las cuatro máscaras. El número de amenazas es su suma, entre 0 y 4. Por cada selector se suman población total, pobre y no pobre. No se suman los conteos individuales para construir la unión.

Los porcentajes de exposición de cada grupo usan su propia población total como denominador. Se verifica que las categorías 0–4 sumen la base y que las categorías 1–4 sumen la unión.

## Sensibilidad

Factorial completo: inundación 0,1/0,2/0,3 m; PGA 0,1/0,2/0,3 g; viento 20/25/33 m/s; WBGT ≥28/≥30/≥32 °C. Son 81 combinaciones. El escenario base está identificado; no se seleccionan resultados por un porcentaje objetivo.

## Interpretación

Exposición no significa daño o damnificación. Superponer cuatro mapas marginales RP100 no representa un evento conjunto RP100. La resolución de WBGT es aproximadamente 27 km y la de viento 2 km. Las tasas de pobreza de 2019 se aplican a población 2025. La ausencia de dato tratada como cero es una regla operativa y debe reconocerse al interpretar resultados.

## Explorador de calibración municipal

La sección Metodología muestra la distribución acumulada real de población por RWI en cada unidad. Cada escalón agrupa todas las celdas con el mismo RWI; el corte municipal y su fracción pobre se recuperan del detalle calculado. Las tasas son fijas. Se contrastan la tasa utilizada y la reproducida, antes del redondeo. Las unidades sin población no tienen corte. `calibracion.py`, ejecutado por `preparar_entrega.py`, regenera los datos y verifica cada grupo de empates, los totales y el corte.
