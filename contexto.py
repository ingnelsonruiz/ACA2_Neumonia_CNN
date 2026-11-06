"""Acceso al contexto compartido (modelo ONNX + metadatos) desde cualquier página.

El modelo y los metadatos están en caché (`modelo.construir_contexto`), así que llamar a `obtener()`
en cada página es barato. El umbral activo vive en `st.session_state["umbral"]`, controlado por el
deslizador de la barra lateral que dibuja app.py.
"""

import streamlit as st

from modelo import Contexto, construir_contexto


def obtener() -> Contexto:
    ctx = construir_contexto()
    if ctx.listo:
        ctx.umbral = float(st.session_state.get("umbral", ctx.meta["umbral"]))
    return ctx
