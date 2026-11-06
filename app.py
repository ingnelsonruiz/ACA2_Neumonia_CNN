"""Negatoscopio IA — detección de neumonía con redes neuronales convolucionales.

Proyecto ACA 2 · Aprendizaje Automático · Especialización en Inteligencia Artificial (CUN)

Punto de entrada: configura la página, dibuja la barra lateral (umbral y datos del proyecto) y
entrega el control a la página elegida con `st.navigation`. Las páginas viven en `app_pages/` y
su registro (título, icono, paso del ACA y criterio de la rúbrica) en `paginas.py`.
"""

import streamlit as st

st.set_page_config(
    page_title="Negatoscopio IA · Lectura asistida de radiografías",
    page_icon=":material/radiology:",
    layout="wide",
)

import estilos                                                       # noqa: E402
from ayuda import ayuda                                              # noqa: E402
from config import (ASIGNATURA, CODIGOS, DOCENTE, EQUIPO, GRUPO,     # noqa: E402
                    PROYECTO, TITULO_APP, URL_APP, URL_REPO, URL_VIDEO)
from contexto import obtener                                         # noqa: E402
from paginas import INICIO, POR_TITULO, SECCIONES, Pagina            # noqa: E402


def _st_page(p: Pagina) -> st.Page:
    return st.Page(p.ruta, title=p.titulo, icon=p.icono, help=p.descripcion, default=p is INICIO)


def _restablecer_umbral(valor: float):
    st.session_state.umbral = valor


def barra_lateral(ctx):
    with st.sidebar:
        if ctx.listo:
            optimo = float(ctx.meta["umbral"])
            st.session_state.setdefault("umbral", optimo)
            st.subheader("Visor", icon=":material/tune:")
            st.slider("Umbral de decisión sobre P(neumonía)", 0.05, 0.95, step=0.01, key="umbral",
                      format="%.2f", help=ayuda("Umbral de decisión"))
            with st.container(horizontal=True, vertical_alignment="center", gap="small"):
                st.caption(f"Óptimo en validación: **{optimo:.2f}**".replace(".", ","))
                st.button("Restablecer", icon=":material/restart_alt:", type="tertiary",
                          on_click=_restablecer_umbral, args=(optimo,),
                          disabled=abs(st.session_state.umbral - optimo) < 1e-9)
            m = ctx.meta["modelo"]
            st.caption(f"EfficientNet-B0 · {m['parametros']:,} parámetros".replace(",", ".")
                       + f"  \nONNX en CPU · entrenado {ctx.meta['fecha_entrenamiento'][:10]}")

        with st.expander("Proyecto y equipo", icon=":material/school:"):
            st.markdown(f"**{PROYECTO}** · {ASIGNATURA}  \nDocente: {DOCENTE}  \n"
                        f"{CODIGOS[0]}, {CODIGOS[1].lower()}, {CODIGOS[2]}")
            st.markdown(f"**{GRUPO}**  \n" + "  \n".join(n for n, _ in EQUIPO))
        enlaces = [(t, i, u) for t, i, u in [("Aplicación", ":material/open_in_new:", URL_APP),
                                             ("Video", ":material/smart_display:", URL_VIDEO),
                                             ("Repositorio", ":material/code:", URL_REPO)] if u]
        for texto, icono, url in enlaces:
            st.markdown(f"{icono} [{texto}]({url})")


def encabezado(p: Pagina):
    """Título, paso del ACA y criterio de la rúbrica de las páginas internas."""
    st.title(p.titulo, icon=p.icono)
    with st.container(horizontal=True, gap="small"):
        st.badge(p.paso, color="blue")
        st.badge(p.criterio, icon=":material/grading:", color="gray")
    st.caption(p.descripcion)


def main():
    estilos.aplicar()
    ctx = obtener()

    if ctx.listo:
        paginas = {"": [_st_page(INICIO)]} | {sec: [_st_page(p) for p in grupo] for sec, grupo in SECCIONES.items()}
    else:   # sin artefactos solo tiene sentido el manual, que explica cómo generarlos
        doc = next(p for grupo in SECCIONES.values() for p in grupo if p.archivo == "documentacion.py")
        paginas = [_st_page(doc)]
    actual = st.navigation(paginas, position="sidebar", expanded=True)
    barra_lateral(ctx)

    if not ctx.listo:
        st.error("Ejecute el notebook `ACA2_Neumonia_CNN.ipynb` en Colab, descargue `artefactos_aca2.zip` y "
                 "descomprímalo en la raíz del repositorio. Faltan: " + ", ".join(ctx.faltantes),
                 icon=":material/error:", title="Faltan artefactos del modelo")

    pagina = POR_TITULO.get(actual.title, INICIO)
    if pagina is not INICIO:
        encabezado(pagina)
    actual.run()

    st.space("large")
    st.caption(f":material/info: {TITULO_APP}, {PROYECTO}, {GRUPO}. Prototipo académico: no sustituye el "
               "diagnóstico de un profesional de la salud.", text_alignment="center")


main()
