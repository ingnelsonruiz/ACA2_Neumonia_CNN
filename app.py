"""Radiografía Inteligente — detección de neumonía con redes neuronales convolucionales.

Proyecto ACA 2 · Aprendizaje Automático · Especialización en Inteligencia Artificial (CUN)

Este archivo solo orquesta: configura la página, construye el contexto (modelo ONNX + metadatos)
y entrega cada pestaña a su módulo. Para agregar una pestaña: crear `vista_mi_vista.py` con
`render(ctx)` y registrarla en `PESTANAS`.
"""

import streamlit as st

st.set_page_config(
    page_title="Radiografía Inteligente · Neumonía",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)

import estilos                                                                   # noqa: E402
from ayuda import ayuda, expansor_indicadores                                    # noqa: E402
from config import (AMBER, ASIGNATURA, CODIGOS, CYAN, DOCENTE, EQUIPO, GREEN,     # noqa: E402
                    GRUPO, PINK, PROYECTO, SUBTITULO, TITULO_APP, URL_APP,
                    URL_REPO, URL_VIDEO, VIOLET)
from modelo import construir_contexto                                            # noqa: E402
from ui import kpi, panel                                                        # noqa: E402
import vista_arquitectura, vista_dataset, vista_documentacion, vista_entrenamiento  # noqa: E402
import vista_equipo, vista_historia, vista_metricas, vista_pipeline              # noqa: E402
import vista_prediccion, vista_sql, vista_umbral                                 # noqa: E402

PESTANAS = [
    ("📖 La historia", vista_historia),
    ("📘 El dataset", vista_dataset),
    ("🗄️ Consultas SQL", vista_sql),
    ("🧪 Pipeline", vista_pipeline),
    ("🧠 Arquitectura", vista_arquitectura),
    ("📈 Entrenamiento", vista_entrenamiento),
    ("📏 Métricas", vista_metricas),
    ("🎯 Umbral clínico", vista_umbral),
    ("🔮 Predicción", vista_prediccion),
    ("👥 Equipo", vista_equipo),
    ("📚 Documentación", vista_documentacion),
]


def barra_lateral(ctx):
    with st.sidebar:
        st.markdown("### 🫁 CENTRO DE CONTROL")
        if ctx.listo:
            ctx.umbral = st.slider("Umbral de decisión · P(neumonía)", 0.05, 0.95,
                                   float(ctx.meta["umbral"]), 0.01, help=ayuda("Umbral de decisión"))
            st.caption(f"Umbral óptimo en validación: **{ctx.meta['umbral']:.2f}**")
            st.markdown("---")
            m = ctx.meta["modelo"]
            st.markdown(f"**Modelo:** EfficientNet-B0  \n**Parámetros:** {m['parametros']:,}  \n"
                        f"**Formato:** ONNX · CPU  \n**Entrenado:** {ctx.meta['fecha_entrenamiento']}")
        st.markdown("---")
        st.markdown(f"**{PROYECTO}**  \n{ASIGNATURA}  \nDocente: {DOCENTE}  \n"
                    f"{' · '.join(CODIGOS).title()}")
        st.markdown(f"**{GRUPO}**  \n" + "  \n".join(n for n, _ in EQUIPO))
        enlaces = [(t, u) for t, u in [("Aplicación", URL_APP), ("Video", URL_VIDEO), ("Repositorio", URL_REPO)] if u]
        if enlaces:
            st.markdown("---")
            st.markdown("  \n".join(f"[{t}]({u})" for t, u in enlaces))


def encabezado(ctx):
    chips = "".join(f'<span class="chip">{c}</span>' for c in CODIGOS)
    st.markdown(f"""
<div class="hero">
    <div class="hero-tag">{PROYECTO.upper()} · {GRUPO.upper()}</div>
    <div class="chips"><span class="chip">{ASIGNATURA.upper()}</span>{chips}</div>
    <h1>{TITULO_APP}</h1>
    <p>{SUBTITULO}</p>
</div>
""", unsafe_allow_html=True)
    if not ctx.listo:
        return
    r = ctx.principal
    unicas = ctx.meta["dataset"]["imagenes_unicas"]
    cols = st.columns(5)
    cols[0].markdown(kpi(f"{unicas:,}", "Radiografías únicas", CYAN,
                         "Imágenes después de eliminar duplicados exactos por hash MD5."), unsafe_allow_html=True)
    cols[1].markdown(kpi(f"{r['recall_sensibilidad']*100:.1f}%", "Sensibilidad", PINK,
                         ayuda("Sensibilidad (recall)")), unsafe_allow_html=True)
    cols[2].markdown(kpi(f"{r['especificidad']*100:.1f}%", "Especificidad", GREEN,
                         ayuda("Especificidad")), unsafe_allow_html=True)
    cols[3].markdown(kpi(f"{r['f1_macro']:.3f}", "F1 macro", VIOLET, ayuda("F1")), unsafe_allow_html=True)
    cols[4].markdown(kpi(f"{r['roc_auc']:.3f}", "ROC-AUC", AMBER, ayuda("ROC-AUC")), unsafe_allow_html=True)
    st.caption("Métricas sobre el conjunto de **prueba** (pacientes nunca vistos), con el umbral elegido en validación.")
    expansor_indicadores(["Sensibilidad (recall)", "Especificidad", "F1", "ROC-AUC"])


def main():
    estilos.aplicar()
    with st.spinner("Cargando modelo y metadatos..."):
        ctx = construir_contexto()
    barra_lateral(ctx)
    encabezado(ctx)

    if not ctx.listo:
        panel("⚠️ <b>Faltan artefactos del modelo:</b> " + ", ".join(ctx.faltantes) +
              ".<br>Ejecute el notebook <code>ACA2_Neumonia_CNN.ipynb</code> en Colab, descargue "
              "<code>artefactos_aca2.zip</code> y descomprímalo en la raíz del repositorio.")
        st.write("")
        vista_documentacion.render(ctx)
        return

    pestanas = st.tabs([etiqueta for etiqueta, _ in PESTANAS])
    for contenedor, (_, modulo) in zip(pestanas, PESTANAS):
        with contenedor:
            modulo.render(ctx)

    st.markdown(f'<div class="aviso">{TITULO_APP.title()} · {PROYECTO} · {GRUPO} · Prototipo académico: '
                f'no sustituye el diagnóstico de un profesional de la salud.</div>', unsafe_allow_html=True)


main()
