# Radiografía Inteligente — Detección de neumonía con CNN

**Proyecto ACA 2 · Grupo 3** · Aprendizaje Automático · Especialización en Inteligencia Artificial (CUN)

Clasifica radiografías de tórax pediátricas como NORMAL o NEUMONÍA con EfficientNet-B0 (transfer learning)
y muestra un mapa de activación (CAM) de cada predicción. Inferencia con ONNX Runtime en CPU.

## Puesta en marcha
1. Ejecutar `ACA2_Neumonia_CNN.ipynb` en Google Colab con GPU T4 y descargar `artefactos_aca2.zip`.
2. Descomprimir el zip en la raíz de este repositorio. Debe quedar:
   ```
   app.py
   chest_xray.duckdb
   artefactos/
       neumonia_effnetb0.onnx
       pesos_cam.npy
       metadatos.json
       ejemplos/*.jpeg
       figuras/*.png
   ```
3. Ejecutar:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Despliegue: subir a GitHub y crear la app en Streamlit Community Cloud apuntando a `app.py`.
   Después, completar `URL_APP`, `URL_VIDEO` y `URL_REPO` en `config.py`.

## Estructura
| Archivo | Responsabilidad |
|---|---|
| `app.py` | Orquestador: página, barra lateral (umbral global) y pestañas |
| `config.py` | Paleta, textos del curso, integrantes, rutas y enlaces |
| `modelo.py` | Carga de artefactos, preprocesamiento idéntico al notebook, inferencia ONNX, CAM |
| `ayuda.py` | Glosario de indicadores (tooltips) y manual descargable |
| `ui.py`, `estilos.py` | Componentes y CSS heredados del ACA 1 |
| `vista_historia.py` | Problema, pregunta orientadora, flujo metodológico |
| `vista_dataset.py` | Origen, distribución, duplicados, partición por paciente |
| `vista_sql.py` | Consultas SQL de solo lectura sobre DuckDB |
| `vista_pipeline.py` | Preprocesamiento y laboratorio interactivo de aumento de datos |
| `vista_arquitectura.py` | CNN base vs. EfficientNet-B0, dos fases, CAM |
| `vista_entrenamiento.py` | Curvas de aprendizaje |
| `vista_metricas.py` | Métricas en prueba, matriz de confusión, ROC, subtipos |
| `vista_umbral.py` | Efecto del umbral (validación) |
| `vista_prediccion.py` | Predicción con mapa de calor |
| `vista_equipo.py` | Integrantes y stack |
| `vista_documentacion.py` | Manual y glosario |

## Cómo modificar sin romper nada
| Quiero... | Toco solo... |
|---|---|
| Reentrenar el modelo | El notebook, y reemplazo `artefactos/` |
| Cambiar textos, integrantes o enlaces | `config.py` |
| Cambiar la explicación de un indicador | `ayuda.py` (`GLOSARIO`) |
| Agregar una consulta SQL | `vista_sql.py` (`CONSULTAS`) |
| Agregar una pestaña | Crear `vista_x.py` con `render(ctx)` y registrarla en `PESTANAS` de `app.py` |

> Prototipo académico. No es un dispositivo médico ni sustituye la lectura de un radiólogo.
