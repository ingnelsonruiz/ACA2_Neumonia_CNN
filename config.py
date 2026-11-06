"""Constantes del proyecto: paleta, metadatos académicos, rutas y enlaces.

Editar aquí cambia la identidad visual y los textos de toda la aplicación.
"""

from pathlib import Path

# ── Paleta (misma identidad visual del ACA 1) ────────────────────────────────
CYAN = "#00D4FF"
VIOLET = "#7B2FFF"
GREEN = "#00FF88"
PINK = "#FF2D78"
AMBER = "#FFD700"
NARANJA = "#FF6B35"

COLOR_MODELO = {"CNN base": VIOLET, "EffNet-B0": CYAN}
COLOR_CLASE = {"NORMAL": GREEN, "NEUMONIA": PINK}

# ── Metadatos académicos ─────────────────────────────────────────────────────
PROYECTO = "Proyecto ACA 2"
TITULO_APP = "RADIOGRAFÍA INTELIGENTE"
SUBTITULO = ("Detección de neumonía en radiografías de tórax con redes neuronales "
             "convolucionales y despliegue interactivo en Streamlit")
ASIGNATURA = "Aprendizaje Automático"
DOCENTE = "Hamilton Rivera Flor"
CODIGOS = ["54ES2", "SEGUNDO BLOQUE", "26ES4"]
PROGRAMA = "Especialización en Inteligencia Artificial"
INSTITUCION = "Corporación Unificada Nacional de Educación Superior (CUN)"
GRUPO = "Grupo 3"

# Verificar integrantes del ACA 2 antes de publicar
EQUIPO = [
    ("Lina María Cabezas Alvear", CYAN),
    ("Nelson Javier Ruiz Lozano", VIOLET),
    ("Yehimy Alexandra Cabrera", GREEN),
    ("Eliana Andrea Medina Forero", PINK),
]

# Completar al publicar (se muestran en la app y en el póster)
URL_APP = ""
URL_VIDEO = ""
URL_REPO = "https://github.com/ingnelsonruiz/ACA2_Neumonia_CNN"

# ── Rutas de artefactos (generados por el notebook ACA2_Neumonia_CNN.ipynb) ──
RAIZ = Path(__file__).parent
DIR_ARTEFACTOS = RAIZ / "artefactos"
RUTA_METADATOS = DIR_ARTEFACTOS / "metadatos.json"
RUTA_PESOS_CAM = DIR_ARTEFACTOS / "pesos_cam.npy"
DIR_EJEMPLOS = DIR_ARTEFACTOS / "ejemplos"
DIR_FIGURAS = DIR_ARTEFACTOS / "figuras"
RUTA_DB = RAIZ / "chest_xray.duckdb"

# ── Dataset ──────────────────────────────────────────────────────────────────
CITA_DATASET = ("Kermany, D. S., Goldbaum, M., Cai, W., et al. (2018). Identifying medical diagnoses "
                "and treatable diseases by image-based deep learning. Cell, 172(5), 1122–1131. "
                "https://doi.org/10.1016/j.cell.2018.02.010")
CITA_KAGGLE = ("Mooney, P. (2018). Chest X-Ray Images (Pneumonia) [Conjunto de datos]. Kaggle. "
               "https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia")
