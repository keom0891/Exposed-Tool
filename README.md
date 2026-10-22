# Exposed Tool: estimación de población total, pobre y no pobre expuesta a amenazas naturales

**Exposed Tool** es una herramienta de análisis geoespacial en Python para estimar la población potencialmente expuesta a amenazas naturales y explorar su distribución territorial y socioeconómica. Combina población de **WorldPop**, riqueza relativa de **Meta RWI**, tasas municipales de pobreza y mapas de intensidad de amenazas.

La implementación actual corresponde al caso de estudio de **El Salvador** en el contexto de GaIA. Evalúa inundación, sismo, viento y calor extremo mediante escenarios individuales de período de retorno de 100 años (**RP100**). Los resultados incluyen exposición por amenaza, exposición a una o más amenazas sin doble conteo y categorías según el número de amenazas presentes.

---

## ✨ Descripción

La herramienta permite:

- Conservar la población de la grilla original de WorldPop y asignarla a unidades municipales.
- Distribuir la población pobre y no pobre dentro de cada municipio mediante un ordenamiento por RWI, calibrado a su tasa de pobreza.
- Consultar la intensidad de cada amenaza en el centro de las celdas de población y aplicar umbrales operativos.
- Estimar población total, pobre y no pobre expuesta a cada amenaza, a su unión y a exactamente cero, una, dos, tres o cuatro amenazas.
- Comparar **81 combinaciones de umbrales** mediante un análisis de sensibilidad.
- Generar tablas, capas geoespaciales, trazabilidad de insumos y un dashboard interactivo autónomo.
- Verificar la conservación de población, la calibración municipal y la consistencia de los resultados mediante una reconstrucción independiente y pruebas unitarias.

La herramienta estima **exposición potencial**. No calcula daños, pérdidas económicas, mortalidad ni población damnificada.

## 📁 Organización del proyecto

```text
01_insumos/
├── amenazas/                    mapas de intensidad RP100
├── poblacion/                   población WorldPop
├── pobreza/                     geometrías y tasas municipales
├── rwi/                         puntos de riqueza relativa Meta RWI
└── limites/                     cartografía de referencia
02_codigo/
├── analizar.py                  población, pobreza y exposición
├── sensibilidad.py              escenarios alternativos de intensidad
├── verificar.py                 reconstrucción independiente y pruebas
├── calibracion.py               datos del explorador de calibración
├── preparar_entrega.py          dashboard, informe y paquete web
├── requisitos.txt               dependencias de Python
├── configurar_entorno.cmd       entorno compartido de los accesos Windows
├── dashboard/                   fuentes y recursos de la interfaz
└── tests/                       pruebas del método
03_resultados/
└── escenario_base/              resultados y controles de la corrida
04_dashboard/                   paquete ZIP para compartir y publicar
05_documentacion/               metodología, informe y revisión
index.html                      dashboard autónomo generado
EJECUTAR_ANALISIS.cmd            ejecución completa en Windows
ACTUALIZAR_DASHBOARD.cmd         actualización de la presentación
LEEME.md                        guía operativa local
requirements.txt                instalación de dependencias
```

Las geometrías utilizadas para la asignación municipal proceden de `01_insumos/pobreza`. La carpeta `limites` conserva cartografía de referencia y no interviene en esa asignación.

## ⚙️ Prerrequisitos

El flujo de cálculo se ha comprobado con **Python 3.12** y las siguientes bibliotecas:

```text
numpy
pandas
geopandas
rasterio
scipy
```

Desde la carpeta principal del proyecto, instale las dependencias en un entorno Python con soporte geoespacial:

```bash
python -m pip install -r requirements.txt
```

GeoPandas y Rasterio requieren dependencias geoespaciales compatibles, incluidas GDAL y PROJ. Los accesos de Windows utilizan un entorno Miniforge ya configurado; para ejecutarlos en otro equipo debe ajustarse la variable `GAIA_ENV` en `02_codigo/configurar_entorno.cmd` a la ubicación del entorno correspondiente.

La consulta del dashboard generado solo requiere un navegador actualizado; no necesita Python ni conexión a internet.

## 🚀 Uso

### Ejecutar el flujo completo

Desde la carpeta principal:

```bash
cd 02_codigo
python analizar.py
python sensibilidad.py
python verificar.py
python preparar_entrega.py
```

Ejecute los pasos en ese orden y continúe únicamente si el anterior termina correctamente. En Windows, **EJECUTAR_ANALISIS.cmd** ejecuta la secuencia y se detiene si falla alguno de los pasos.

Los resultados se escriben en `03_resultados/escenario_base`. Cada corrida sustituye las salidas anteriores; conserve una copia si necesita comparar ejecuciones. Cierre las capas de resultados abiertas en QGIS u otros programas antes de recalcular.

### Consultar resultados

Abra **index.html** en la raíz del repositorio. La interfaz permite explorar resultados por territorio y grupo poblacional, consultar la calibración municipal y comparar escenarios nacionales de sensibilidad.

### Actualizar solo la presentación

Si los resultados ya existen y únicamente se modificaron textos o diseño:

```bash
cd 02_codigo
python preparar_entrega.py
```

En Windows puede utilizarse **ACTUALIZAR_DASHBOARD.cmd**. Este paso reconstruye la presentación y los datos del explorador de calibración, sin recalcular la exposición a amenazas.

### Ejecutar las pruebas del método

```bash
cd 02_codigo
python -m unittest discover -s tests -v
```

Las pruebas cubren ponderación por habitantes, empates en el corte de RWI, tasas extremas, operadores de exposición, datos faltantes y categorías de amenazas. `verificar.py` también ejecuta estas pruebas después de reconstruir los resultados.

## 📥 Archivos de entrada

| Insumo | Formato | Uso |
|---|---|---|
| WorldPop 2025 | GeoTIFF con habitantes por celda | Distribución espacial de población; se conservan las celdas positivas válidas. |
| Meta RWI | CSV con `longitude`, `latitude`, `rwi` y `error` | Asignación del punto de riqueza relativa más cercano a cada centro WorldPop. |
| Límites municipales | Shapefile con `ADM1_EN`, `ADM2_EN` y `ADM2_PCODE` | Asignación territorial y agregación municipal. |
| Tasas de pobreza 2019 | CSV con `ADM2_PCODE` y `POVERTY_RATE` | Proporción de personas pobres, expresada entre 0 y 100. |
| Inundación RP100 | GeoTIFF, profundidad en metros | Intensidad de inundación. |
| Sismo RP100 | GeoTIFF, PGA en g | Aceleración máxima del terreno. |
| Viento RP100 | GeoTIFF, m/s | Velocidad del viento máxima. |
| Calor RP100 | GeoTIFF, WBGT en °C | Índice de estrés térmico. |

Los nombres de los archivos se encuentran definidos en `analizar.py`. Los componentes de cada shapefile deben conservarse juntos. Las definiciones de las variables, sus unidades y RP100 corresponden a las confirmadas para este caso de estudio.

Las fuentes editables de la interfaz se conservan en `02_codigo/dashboard`; el HTML de la raíz y el paquete de `04_dashboard` son entregables generados. El paquete ZIP de `04_dashboard` contiene el mismo HTML autónomo y la licencia de la tipografía, sin una segunda versión web separada. Las salidas actuales se mantienen para facilitar la consulta y la reproducción del caso. Los registros de publicación y carpetas del motor anterior no forman parte del flujo.

El caso actual utiliza mapas de amenaza en **EPSG:4326**. El motor principal transforma coordenadas al CRS de cada amenaza, mientras que la sensibilidad y su verificación están implementadas para los insumos actuales en EPSG:4326; al incorporar mapas con otro CRS deben adaptarse esos pasos. Las distancias para asignación por cercanía se calculan en **UTM 16N, EPSG:32616**, apropiado para este caso.

## 📐 Metodología

### 1. Asignación territorial de la población

Se obtiene el centro de cada celda positiva de WorldPop y se asigna al polígono municipal que lo contiene. Los centros fuera de los polígonos se asignan al municipio más cercano para conservar la población nacional. Estas asignaciones y sus distancias quedan registradas.

### 2. Calibración de pobreza mediante RWI

Se conserva el valor original de Meta RWI del punto más cercano a cada centro WorldPop. Ese punto puede encontrarse al otro lado de un límite municipal.

Dentro de cada municipio, las celdas se ordenan de menor a mayor RWI, ponderando por habitantes. La población pobre objetivo es:

```text
población pobre objetivo = tasa municipal × población WorldPop del municipio
```

Se asigna como pobre a la población bajo el corte de RWI y como no pobre a la situada sobre él. Cuando el objetivo cae dentro de un grupo de celdas empatadas en el corte, todas reciben la misma fracción pobre:

```text
fracción en el corte = (pobres objetivo − población bajo el corte)
                      / población del grupo en el corte

pobres por celda    = población × fracción pobre
no pobres por celda = población × (1 − fracción pobre)
```

El procedimiento reproduce la tasa municipal antes del redondeo. Las tasas faltantes se completan con el promedio simple de vecinos con tasa original y un segmento de límite compartido; si no existen, el código revisa contacto puntual. No se utilizan otras tasas imputadas para calcular el promedio.

**Esta calibración es una asignación espacial modelada:** no identifica hogares pobres ni estima una línea nacional única de pobreza. Un mismo valor RWI puede recibir una asignación distinta en municipios diferentes. La coincidencia con la tasa municipal es una propiedad del método, no una validación de la localización de la pobreza.

### 3. Intensidad y exposición por amenaza

Para cada centro WorldPop se consulta el píxel contenedor en la grilla nativa de cada amenaza. No se interpolan intensidades ni se reparte población por la fracción de área intersectada. Toda la población de la celda recibe el mismo indicador de exposición a cada amenaza.

| Amenaza | Escenario base |
|---|---|
| Inundación | Profundidad **≥0,1 m** |
| Sismo | PGA **≥0,10 g** |
| Viento huracanado | Velocidad del viento máxima **≥33 m/s** |
| Calor | WBGT **≥30 °C** |

La ausencia de cobertura y NoData se computan como cero exposición a esa amenaza, conservando la población. Los indicadores de cobertura se guardan para reconocer esta limitación.

### 4. Unión y categorías multiamenaza

Las cuatro máscaras binarias se combinan por celda:

```text
número de amenazas = inundación + sismo + viento + calor
una o más amenazas = número de amenazas ≥ 1
dos o más amenazas = número de amenazas ≥ 2
```

La unión cuenta la población una sola vez, aunque supere varios umbrales. Para cada selector se suman población total, pobre y no pobre. El porcentaje de exposición de cada grupo utiliza como denominador la población de ese mismo grupo en el territorio analizado.

### 5. Sensibilidad a umbrales

Se evalúa el producto cartesiano completo de los siguientes niveles:

| Amenaza | Niveles |
|---|---|
| Inundación | ≥0,10 / ≥0,20 / ≥0,30 m |
| Sismo | ≥0,10 / ≥0,20 / ≥0,30 g |
| Viento huracanado | ≥20 / ≥25 / ≥33 m/s |
| Calor | ≥28 / ≥30 / ≥32 °C WBGT |

Se generan **81 combinaciones**, incluido el escenario base. Se conservan los mapas RP100 y se modifican sus umbrales de intensidad. La comparación de sensibilidad es nacional; los mapas y resultados municipales del dashboard corresponden al escenario base.

### Modificar parámetros

Los umbrales base se definen en `HAZARDS`, dentro de `02_codigo/analizar.py`. Los niveles de sensibilidad están en `02_codigo/sensibilidad.py`. Al cambiarlos deben revisarse también las etiquetas de la interfaz, el informe y las comprobaciones de `verificar.py`, y ejecutarse nuevamente el flujo completo.

La implementación contiene nombres de archivo, proyección de distancias y referencias específicas de El Salvador. Su aplicación a otro país requiere adaptar esas definiciones y comprobar la compatibilidad de los nuevos insumos.

## 📤 Resultados

| Archivo o carpeta | Contenido |
|---|---|
| `03_resultados/escenario_base/indicadores.csv` | Población nacional y municipal por grupo, amenaza, unión y categorías 0–4. |
| `municipios.csv` | Atributos municipales, población, exposición, tasas utilizadas y cortes RWI. |
| `celdas.csv.gz` | Detalle de población, pobreza, RWI, distancias, cobertura y exposición por celda. |
| `resultados_municipales.gpkg` | Geometrías municipales y resultados en GeoPackage. |
| `poblacion_y_exposicion.tif` | Cinco bandas: población total, pobre, no pobre, número de amenazas y combinación de máscaras en bits. |
| `sensibilidad.csv` | Resultados de las 81 combinaciones para los tres grupos poblacionales. |
| `sensibilidad_resumen.json` | Niveles, escenario base y rangos nacionales de sensibilidad. |
| `calibracion_municipal.json` | Distribución de población por RWI y detalle del corte municipal. |
| `tasas_imputadas.json` | Tasas completadas, método y vecinos utilizados. |
| `asignaciones_fuera_limites.csv` | Centros asignados por cercanía y distancias. |
| `auditoria.json` | Parámetros, controles, versiones y huellas SHA-256 de los insumos. |
| `revision_independiente.json` | Resultados de la reconstrucción independiente y pruebas. |
| `index.html` | Dashboard autónomo con datos y recursos incluidos. |
| `04_dashboard/Dashboard_para_publicar.zip` | Paquete estático de presentación. |
| `05_documentacion/` | Informe, metodología, revisión y diccionario de archivos. |

Los archivos sin ruta explícita en esta tabla se guardan dentro de `03_resultados/escenario_base`.

## 🧩 Módulos

| Módulo | Responsabilidad |
|---|---|
| `analizar.py` | Lee insumos, asigna población y RWI, completa tasas, calibra pobreza, construye máscaras, agrega resultados y registra trazabilidad. |
| `sensibilidad.py` | Evalúa las combinaciones de intensidad para población total, pobre y no pobre. |
| `verificar.py` | Reconstruye asignaciones y resultados desde los insumos, verifica agregados y sensibilidad y ejecuta las pruebas unitarias. |
| `calibracion.py` | Agrupa el detalle por nivel RWI y prepara las distribuciones reales para el explorador municipal. |
| `preparar_entrega.py` | Genera el dashboard autónomo, el informe y el paquete web a partir de los resultados existentes. |
| `dashboard/app.js` | Interacción con mapas, tablas, grupos poblacionales, sensibilidad y descargas. |
| `dashboard/calibracion.js` | Consulta gráfica del corte y de la fracción pobre por municipio. |

## ✅ Controles de consistencia

- Celdas de población sin duplicación y conservación de la suma WorldPop.
- Población pobre + no pobre = población total.
- Población pobre municipal = tasa utilizada × población municipal.
- Fracción común para las celdas empatadas en el corte RWI.
- Categorías 0–4 = población base; categorías 1–4 = unión.
- Reconstrucción de asignaciones municipales y del RWI más cercano.
- Reconstrucción de máscaras y coberturas desde los rásteres originales.
- Comparación de agregados nacionales, municipales y escenarios de sensibilidad.
- Correspondencia de las huellas SHA-256 de los insumos.

Los controles numéricos utilizan una tolerancia inferior a **0,00001 habitantes**. Las cifras visibles se redondean únicamente para su presentación.

## Alcance y limitaciones

- **Fechas distintas:** las tasas de pobreza de 2019 se aplican a la población WorldPop 2025; no se estiman nuevas tasas municipales de pobreza para 2025.
- **Asignación de pobreza:** el ranking RWI supone mayor concentración de pobreza en áreas de menor riqueza relativa. La exactitud espacial de esa distribución no queda demostrada por la calibración.
- **Escala de los datos:** población e inundación tienen resolución nominal cercana a 100 m; sismo, aproximadamente 110 m; viento, 2 km; y WBGT, 27 km. La grilla poblacional no aumenta el detalle de las otras fuentes.
- **Cobertura:** tratar NoData como cero exposición no demuestra ausencia de peligro y puede reducir los conteos.
- **Aproximación puntual:** la exposición depende de la intensidad en el centro de celda, no de su intersección exacta por área.
- **Geografía:** se conservan los 266 polígonos de la fuente territorial, incluidos cuatro cuerpos de agua sin población asignada. No se actualiza la división administrativa.
- **Incertidumbre:** se conserva el error original del RWI, pero no se propaga junto con los errores de población, pobreza o amenazas para construir intervalos de confianza.
- **Interpretación de RP100:** la superposición espacial de mapas individuales RP100 no representa un evento conjunto RP100 ni implica simultaneidad temporal.
- **Exposición e impacto:** los conteos no equivalen a daños ni a personas afectadas. La verificación del código comprueba su implementación y coherencia, sin validar independientemente los modelos originales de amenaza.

La metodología completa y las comprobaciones del caso de estudio se encuentran en [`05_documentacion/Metodologia.md`](05_documentacion/Metodologia.md) y [`05_documentacion/Revision_final.md`](05_documentacion/Revision_final.md).

## 📑 Licencia

Copyright © 2026. Banco Interamericano de Desarrollo ("BID"). Uso autorizado.

La herramienta se distribuye bajo la **licencia de software BID AM-331-A3**. Consulte los términos completos en [LICENSE.md](LICENSE.md). Esta licencia autoriza los usos allí establecidos para fines no comerciales. Los componentes e insumos de terceros conservan sus respectivas licencias y condiciones de uso.

Los procedimientos y resultados obtenidos en base a la ejecución de este software son los programados por los desarrolladores y no necesariamente reflejan el punto de vista del BID, de su Directorio Ejecutivo ni de los países que representa.

La Documentación de Soporte y Uso se rige por la disposición correspondiente de la licencia AM-331-A3: salvo indicación en contrario, Creative Commons IGO 3.0 Atribución-NoComercial-SinObraDerivada (CC-IGO 3.0 BY-NC-ND).
