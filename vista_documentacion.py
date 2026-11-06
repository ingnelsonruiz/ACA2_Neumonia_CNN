"""Pestaña «Documentación»: manual de uso, glosario y descarga del manual."""

import streamlit as st

from ayuda import manual_markdown
from ui import seccion


def render(ctx):
    seccion("MANUAL DE USO")
    manual = manual_markdown(ctx.meta)
    st.download_button("⬇️ Descargar manual (Markdown)", manual.encode("utf-8"),
                       file_name="Manual_Radiografia_Inteligente.md", mime="text/markdown", type="primary")
    st.markdown(manual)
