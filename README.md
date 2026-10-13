# Visión por Computadora - Evaluación Integradora

## Sistema Multicamara de Monitoreo Urbano y Deteccion Aerea con YOLOv8 y ByteTrack

Este repositorio contiene la solucion completa de la Evaluacion Integradora para la asignatura Vision por Computadora de la Licenciatura en Inteligencia Artificial (Universidad Blas Pascal).

El proyecto implementa un pipeline automatizado de extremo a extremo para la deteccion, clasificacion, filtrado cromatico (vehiculos rojos) y seguimiento (tracking) continuo de trafico urbano a traves de multiples vistas de camaras fijas y tomas aereas con dron.

---

## Caracteristicas Principales

* Normalizacion y Estandarizacion de Flujos: Preprocesamiento de secuencias de video multicamara corrigiendo discrepancias de frecuencia de cuadros (frame rate) a 15 FPS.
* Deteccion y Clasificacion con YOLOv8: Implementacion y ajuste fino (fine-tuning) de modelos YOLOv8 para categorizar actores urbanos (automovil, utilitario, pickup, camion, motorcycle, bicycle, person).
* Analisis Cromatico HSV: Filtro morfologico y de dispersion cromatica en el espacio de color HSV para aislar vehiculos rojos reduciendo falsos positivos causados por luces de freno o reflejos.
* Zonas de Exclusion y Referencias Espaciales: Mascaras de region de interes (ROIs) y marcos de referencia urbanos para delimitar calzadas y excluir veredas o areas fuera de transito.
* Seguimiento Multicamara (ByteTrack): Asignacion persistente de identificadores globales (track_ids) para evitar el doble conteo de vehiculos.
* Evaluacion en Perspectiva Aerea (Dron): Analisis de Dataset Drift frente a cambios de angulo cenital/oblicuo y estabilizacion de eventos.

---

## Estructura del Repositorio

```text
vision-computadora-integrador/
├── README.md                      # Portada y documentacion del proyecto
├── .gitignore                     # Filtros para evitar subir videos o pesos binarios
├── requirements.txt               # Lista de dependencias del entorno
├── configs/
│   └── data.yaml                  # Configuracion de clases y rutas para YOLOv8
├── notebooks/
│   ├── VC_EVALUACION_INTEGRADORA_PARTE1_FULL_corto.ipynb  # Deteccion y registro de eventos inicial
│   └── VC_EVALUACION_INTEGRADORA_PARTE2_FULL.ipynb  # Entrenamiento, tracking y validacion dron
└── scripts/
    ├── camara_rois.py             # Definicion de ROIs y mascaras urbanas
    ├── camara_rois_v2.py          # Zonas adaptadas para camaras fijas y dron
    ├── editor_yolo.py             # Ajustes y conversiones de etiquetas
    ├── pipeline_generico.py       # Motor de procesamiento de flujo de video
    ├── referencias_urbanas.py     # Puntos clave de referencia en calzada
    └── utils_color.py             # Mascaras de filtrado de color en espacio HSV
```


## Recursos completos


Los datasets, vídeos y modelos entrenados pueden descargarse desde:
 

https://drive.google.com/file/d/1LYbi_6j_vkI3yHYAu3ZWEFRjRxhW6PRt/view?usp=sharing
## Parte 1
https://colab.research.google.com/drive/1sWyzHxq3gmZsJPW4fz7NITCTGIDnjsXY?usp=sharing
## Parte 2
https://colab.research.google.com/drive/1pxAG8jvM5JQSteBnxhO06joNDnpY9i13?usp=sharing

## Instalación


```bash

pip install -r requirements.txt
```
