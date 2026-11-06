"""Página «Arquitectura»: CNN base vs. EfficientNet-B0, transfer learning y CAM."""

import pandas as pd
import streamlit as st

from config import AMBER, CYAN, DIR_ARTEFACTOS, GREEN, PINK, VIOLET
from ui import flujo, kpi, panel, seccion, tabla, tarjeta

CAPAS_EFFNET = [
    ("ENTRADA", "224×224×3"), ("STEM", "Conv 3×3 · 32"), ("MBConv1", "16 canales"),
    ("MBConv6 ×2", "24"), ("MBConv6 ×2", "40"), ("MBConv6 ×3", "80"), ("MBConv6 ×3", "112"),
    ("MBConv6 ×4", "192"), ("MBConv6", "320"), ("CONV 1×1", "1 280 mapas 7×7"),
    ("GAP", "vector 1 280"), ("CABEZA", "Dropout 0,3 → Linear 2"), ("SOFTMAX", "P(normal), P(neumonía)"),
]
CAPAS_BASE = [
    ("ENTRADA", "224×224×3"), ("BLOQUE 1", "2×Conv 32 + MaxPool"), ("BLOQUE 2", "2×Conv 64 + MaxPool"),
    ("BLOQUE 3", "2×Conv 128 + MaxPool"), ("BLOQUE 4", "2×Conv 256 + MaxPool"), ("GAP", "vector 256"),
    ("CABEZA", "Dropout 0,3 → Linear 2"),
]


def _flujo(capas):
    flujo(capas, ancho=140)


def render(ctx):
    m, e, b = ctx.meta["modelo"], ctx.principal, ctx.base
    seccion("MODELO DESPLEGADO · EFFICIENTNET-B0 (TRANSFER LEARNING)")
    _flujo(CAPAS_EFFNET)
    panel("EfficientNet (Tan y Le, 2019) escala de forma balanceada la <b>profundidad</b>, la <b>anchura</b> y la "
          "<b>resolución</b> de la red. Sus bloques <b>MBConv</b> combinan convoluciones separables en profundidad "
          "(mucho más baratas que una convolución estándar) con <b>squeeze-and-excitation</b>, que aprende a "
          "ponderar cada canal según su relevancia. Se parte de pesos aprendidos en ImageNet (1,2 millones de "
          "imágenes): los primeros filtros ya detectan bordes y texturas, útiles también en radiografías.")

    seccion("ENTRENAMIENTO EN DOS FASES")
    t = ctx.meta["entrenamiento"]
    a, c = st.columns(2)
    tarjeta(a, "FASE 1 · CABEZA", f"Extractor congelado (incluidas sus capas BatchNorm). Solo se entrena la "
                       f"capa final con lr = {t['lr']['fase1']:g} durante {t['epoca_fin_fase1']} épocas. Evita que "
                       "los gradientes de una capa aleatoria destruyan los filtros preentrenados.", CYAN, "1")
    tarjeta(c, "FASE 2 · FINE-TUNING", f"Se descongela toda la red y se ajusta con lr = {t['lr']['fase2']:g} "
                       "(10 veces menor) y decaimiento coseno, con early stopping sobre el F1 macro de validación.",
                       VIOLET, "2")
    st.caption(f"Pérdida: {t['perdida']} · Optimizador: {t['optimizador']} · Scheduler: {t['scheduler']} · "
               f"Batch: {t['batch']} · Semilla: {t['semilla']}")

    seccion("LÍNEA BASE · CNN DISEÑADA DESDE CERO")
    _flujo(CAPAS_BASE)

    seccion("¿POR QUÉ EFFICIENTNET? COMPARACIÓN EN PRUEBA")
    comp = pd.DataFrame({
        "Modelo": ["CNN base (desde cero)", "EfficientNet-B0 (transfer learning)"],
        "Parámetros": [f"{ctx.meta.get('parametros_base', 0):,}", f"{m['parametros']:,}"],
        "Sensibilidad": [b["recall_sensibilidad"], e["recall_sensibilidad"]],
        "Especificidad": [b["especificidad"], e["especificidad"]],
        "F1 macro": [b["f1_macro"], e["f1_macro"]],
        "ROC-AUC": [b["roc_auc"], e["roc_auc"]],
    })
    for col in ["Sensibilidad", "Especificidad", "F1 macro", "ROC-AUC"]:
        comp[col] = comp[col].map(lambda v: f"{v:.4f}")
    tabla(comp)
    k = st.columns(3)
    kpi(k[0], f"{(e['f1_macro'] - b['f1_macro'])*100:+.1f} pp", "Ganancia en F1 macro", GREEN)
    kpi(k[1], f"{(e['roc_auc'] - b['roc_auc']):+.3f}", "Ganancia en AUC", AMBER)
    mb = (DIR_ARTEFACTOS / m["archivo"]).stat().st_size / 1e6
    kpi(k[2], f"{mb:.1f} MB", "Tamaño del modelo ONNX", PINK,
                      "Formato abierto servido con onnxruntime en CPU, sin PyTorch.")

    seccion("EXPLICABILIDAD · MAPAS DE ACTIVACIÓN DE CLASE (CAM)")
    st.latex(r"\mathrm{CAM}_{c}(i,j)=\max\Big(0,\;\sum_{k=1}^{1280} w_{c,k}\,A_k(i,j)\Big)")
    panel("Como la red termina en <i>Global Average Pooling</i> + una capa lineal, el mapa de activación se obtiene "
          "exactamente ponderando los 1 280 mapas A<sub>k</sub> de la última convolución con los pesos "
          "w<sub>c,k</sub> de la clase «neumonía» (Zhou et al., 2016). Para esta arquitectura coincide con Grad-CAM "
          "salvo una constante (el notebook lo verifica numéricamente), y no requiere calcular gradientes: el modelo "
          f"ONNX expone directamente los mapas como segunda salida ({' × '.join(map(str, m['forma_mapas']))}).")
