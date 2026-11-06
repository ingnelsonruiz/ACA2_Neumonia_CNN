"""Página «Documentación»: manual de uso, glosario y descarga del manual."""

import re

import streamlit as st

from ayuda import manual_markdown


def render(ctx):
    manual = manual_markdown(ctx.meta)
    st.download_button("Descargar manual (Markdown)", manual.encode("utf-8"), icon=":material/download:",
                       file_name="Manual_Radiografia_Inteligente.md", mime="text/markdown", type="primary")
    # En pantalla el título de la página ya hace de H1: se baja un nivel cada encabezado del manual
    en_pantalla = re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + 1) + " ", manual, flags=re.M)
    with st.container(border=True, key="manual"):
        st.markdown(en_pantalla)
