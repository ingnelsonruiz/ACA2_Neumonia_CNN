"""Sección «Póster»: la infografía del proyecto (entregable 2 del ACA).

Para actualizarla basta con reemplazar artefactos/poster.png en el repositorio.
"""

import streamlit as st

from config import RUTA_POSTER
from ui import imagen, panel


def render(ctx):
    if not RUTA_POSTER.exists():
        panel("Todavía no hay póster. Súbalo al repositorio como <code>artefactos/poster.png</code> "
              "y aparecerá aquí automáticamente.")
        return
    imagen(str(RUTA_POSTER), "Póster tipo infografía del proyecto.")
    st.download_button("Descargar póster (PNG)", RUTA_POSTER.read_bytes(),
                       file_name="Poster_Negatoscopio_IA.png", mime="image/png")
