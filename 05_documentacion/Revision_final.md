# Revisión final de la metodología

Fecha: 21 de octubre de 2026.

La implementación y los resultados son coherentes con los criterios documentados para este ejercicio. La revisión reconstruyó los cálculos desde los insumos y el detalle por celda. Los controles verifican la implementación; no constituyen una validación externa de las fuentes ni de las capacidades predictivas de los modelos.

## Comprobaciones realizadas

- 971.376 celdas WorldPop positivas, sin duplicación y con conservación de 6.352.400,97 habitantes.
- Asignación municipal y asignación del punto RWI más cercano reconstruidas: cero discrepancias.
- Calibración municipal ponderada por habitantes y fracción común para empates: tasas originales preservadas y promedios imputados reproducidos.
- Cuatro máscaras de amenaza y sus coberturas reconstruidas: cero discrepancias. Las cuatro amenazas incluyen igualdad en el umbral.
- Pobre + no pobre = total; categorías 0–4 = población base; categorías 1–4 = unión; dos o más = categorías 2–4. Agregados nacionales y municipales consistentes, con diferencias numéricas inferiores a 0,00001 habitantes.
- Las 81 combinaciones de sensibilidad reproducen los totales de una o más y dos o más amenazas. El escenario base es único y utiliza PGA ≥0,10 g.
- Huellas SHA-256 de los insumos coincidentes. Seis pruebas unitarias satisfactorias.
- Explorador de calibración generado desde los valores reales del detalle por celda para 262 unidades con población; cuatro unidades sin población se muestran sin corte. Tasas imputadas en unidades pobladas: La Libertad y San Martín.

## Criterios que deben acompañar la presentación

1. **Pobreza estimada espacialmente.** El RWI ordena riqueza relativa dentro de cada municipio; la tasa municipal fija la cantidad de población pobre. No identifica personas u hogares pobres ni crea una línea nacional de pobreza. Se aplican tasas de 2019 a WorldPop 2025.
2. **Muestreo por centro de celda.** Se utiliza la grilla original de WorldPop, sin agregar a hexágonos ni repartir población por el área exacta de intersección. Esto es una aproximación puntual de la exposición.
3. **Ausencia de datos.** NoData y ausencia de cobertura se computan como cero exposición, conservando población. Esto no demuestra ausencia de peligro; puede reducir la exposición estimada. La cobertura figura en la metodología y en las descargas.
4. **Resoluciones distintas.** WBGT ronda 27 km y viento 2 km. Las celdas WorldPop de unos 100 m no añaden detalle real a esas fuentes.
5. **Definiciones adoptadas.** Las capas se utilizan como profundidad en m, PGA en g, velocidad del viento máxima en m/s y WBGT en °C, todas RP100. La revisión no verifica independientemente esas definiciones ni los modelos de origen. El archivo de calor tiene un nombre genérico; su identificación como WBGT procede de la definición adoptada para el ejercicio. El tratamiento previo de WBGT por vecino válido cercano se documenta entre las limitaciones.
6. **Exposición potencial.** La unión de mapas marginales RP100 no equivale a un evento conjunto RP100, simultaneidad temporal, probabilidad individual de daño ni población damnificada. No se han propagado incertidumbres de las fuentes.
7. **Geografía de la fuente.** Se conservan 266 polígonos, incluidos cuatro cuerpos de agua sin población asignada; no se representa una actualización de la división administrativa.

## Resultado del escenario base

Inundación ≥0,1 m; PGA ≥0,10 g; viento huracanado ≥20 m/s; WBGT ≥30 °C.

- Al menos una amenaza: 6.349.122,17 habitantes, **99,95%** de la población modelada.
- Dos o más amenazas: 5.351.946,16 habitantes, **84,25%**.

Los porcentajes de población pobre y no pobre usan como denominador la población de su propio grupo. Los conteos se calculan sin redondear; el dashboard redondea únicamente para presentación.

## Dictamen de la revisión integral del repositorio

**Fecha: 21 de octubre de 2026.** La carpeta de la herramienta se revisó en su ubicación GitHub y las verificaciones se ejecutaron sobre los insumos de ese repositorio.

**Conclusión:** la implementación es coherente y el método es aceptable para estimar población potencialmente expuesta que supera los umbrales operativos definidos, a escala nacional y municipal y con la aproximación por centro de celda. La distribución por condición de pobreza es una estimación condicionada al ranking RWI y a las tasas municipales; no constituye una observación individual ni una validación independiente de la localización de la pobreza.

### Estado de la herramienta

- Se conserva un único dashboard generado, `index.html`, en la raíz. El paquete ZIP contiene exactamente ese archivo, junto con la licencia de la tipografía.
- Las fuentes editables, insumos, resultados y documentación están separados. No permanecen las carpetas del motor anterior ni el acceso duplicado.
- Ambos accesos Windows comparten `02_codigo/configurar_entorno.cmd`; se comprobó su ejecución en el entorno disponible.
- La sintaxis de los módulos Python y de los scripts de interacción es válida. Las seis pruebas unitarias pasaron.
- El HTML es autónomo, sus identificadores son únicos y sus datos coinciden con las fuentes generadas y la auditoría. Los porcentajes y las categorías de las 81 combinaciones son consistentes.
- La reconstrucción independiente verificó 971.376 celdas, las asignaciones municipales y RWI, las cuatro máscaras y coberturas, los agregados y la sensibilidad. No se detectaron discrepancias de clasificación; las diferencias numéricas son inferiores a 0,00001 habitantes.
- Se corrigió el control de huellas para comprobar los insumos locales del repositorio, conservando las rutas históricas del registro como procedencia. Se añadió una comprobación explícita de EPSG:4326 en sensibilidad para rechazar insumos incompatibles, en lugar de procesarlos silenciosamente. Ninguna corrección modifica las cifras actuales.

### Justificación conceptual

El indicador se expresa como suma de habitantes por celda multiplicados por una máscara binaria de intensidad. La unión lógica cuenta una vez cada celda y la suma de máscaras identifica el número de amenazas. Esta formulación responde a la localización de población en áreas de amenaza definidas por un umbral. La distinción entre exposición, vulnerabilidad e impactos es consistente con el [glosario del IPCC](https://www.ipcc.ch/report/ar6/wg2/chapter/annex-ii/).

Los valores de WorldPop utilizados son conteos de habitantes por celda: no se multiplican de nuevo por el área del píxel. La aproximación espacial asigna la intensidad en su centro a toda su población y no debe describirse como una intersección exacta de superficies. Las resoluciones de las amenazas limitan la interpretación local, especialmente para viento y WBGT.

El RWI ordena riqueza relativa, según la [descripción del proyecto original](https://cega.berkeley.edu/article/micro-estimates-of-wealth-for-all-low-and-middle-income-countries/). En esta herramienta se utiliza ese orden dentro de cada municipio para asignar la cantidad de población pobre determinada por su tasa. La calibración exacta asegura coherencia contable, no precisión de la distribución espacial de pobreza. Esta aproximación se aceptó explícitamente para el caso de estudio.

### Condiciones e interpretación

Las definiciones WBGT, velocidad del viento máxima, RP100 y tasas de pobreza referidas a personas fueron confirmadas para el ejercicio. Esa confirmación permite aplicar los insumos conforme a sus definiciones; no supone una auditoría independiente de los modelos que generaron los mapas.

Se mantienen visibles las siguientes condiciones: tasas de pobreza de 2019 sobre población de 2025; asignación al municipio más cercano de los centros fuera de límites; uso del RWI más cercano; imputación de tasas con vecinos; cero exposición cuando no hay dato válido; incertidumbre de las fuentes no propagada. NoData no debe interpretarse como ausencia de peligro demostrada.

Los umbrales son criterios operativos de exposición y no umbrales universales de daño. La superposición de cuatro mapas RP100 no representa un evento conjunto RP100 ni simultaneidad de amenazas. La población expuesta no equivale a damnificados, pérdidas ni probabilidades individuales de daño.

Con PGA ≥0,10 g, casi toda la población con dato sísmico válido supera el umbral: el mapa tiene un mínimo válido de 0,20139 g. Esto explica que la unión sea 99,95%. En este escenario. el viento huracanado ≥20 m/s comprende aproximadamente 2.967.809 habitantes y el WBGT ≥30 °C comprende 80,79% de la población. Las categorías dependen de estas distribuciones y de los umbrales; el número de amenazas no es una escala de severidad o daño.

El resultado es apropiado para diagnóstico territorial, comparación exploratoria y discusión de prioridades, manteniendo estas definiciones. Las decisiones sobre impactos, hogares individuales o inversiones que requieran estimación de pérdidas necesitan análisis adicionales de vulnerabilidad y validación específica.

Los comprobantes de esta revisión se conservan en `03_resultados/escenario_base/revision_independiente.json` y `revision_estructura.json`. Los cambios del repositorio deben incorporarse mediante commit y push para quedar disponibles en GitHub.

