# Guía rápida · Exposed Tool

La documentación principal de instalación, módulos, metodología y limitaciones está en [README.md](README.md).

## Accesos

- **index.html**: consulta local de los resultados, sin instalar Python ni iniciar un servidor.
- **EJECUTAR_ANALISIS.cmd**: recalcula exposición y sensibilidad, verifica los resultados y reconstruye los entregables. Se detiene ante cualquier error.
- **ACTUALIZAR_DASHBOARD.cmd**: reconstruye presentación e informe desde los resultados existentes; no recalcula exposición.

Los dos accesos de ejecución comparten `02_codigo/configurar_entorno.cmd`. Ajuste allí `GAIA_ENV` si el entorno Python está en otra ubicación. Instale las dependencias con `python -m pip install -r requirements.txt`.

## Dónde trabajar

| Carpeta | Función |
|---|---|
| 01_insumos | Fuentes originales. La cartografía de `limites` se conserva como referencia; la geometría usada por el cálculo está en `pobreza`. |
| 02_codigo | Motor, verificaciones y fuentes editables de la interfaz. |
| 03_resultados/escenario_base | Tablas, capas, detalle por celda y auditoría de la corrida. |
| 04_dashboard | Entregables generados: ZIP para compartir o publicar y guía de entrega. |
| 05_documentacion | Metodología, informe y revisión del caso de estudio. |

Edite el diseño y los textos en `02_codigo/dashboard`; después reconstruya la presentación. Los HTML de consulta son salidas, no fuentes de cálculo.

## Operación

La ejecución completa sustituye los resultados anteriores. Cierre las capas de resultados abiertas en QGIS antes de recalcular. Conserve juntos todos los componentes de los shapefiles. La revisión matemática se regenera mediante `02_codigo/verificar.py`.

Escenario vigente: inundación ≥0,1 m; PGA ≥0,10 g; viento huracanado ≥33 m/s; WBGT ≥30 °C. Los metadatos RP100, WBGT, velocidad del viento máxima y las tasas de pobreza de personas fueron confirmados para este caso. La distribución intramunicipal de pobreza por RWI es un supuesto de modelación; la exposición potencial no equivale a daño.
