"""Página de inicio: portada con resultados, la herramienta de predicción (paso 5) y el recorrido."""

import streamlit as st

import vista_prediccion
from contexto import obtener
from portada import portada, recorrido

ctx = obtener()
portada(ctx)

st.space("medium")
with st.container(border=True, key="demo"):
    st.badge("Paso 5 · despliegue, 15 % de la nota", icon=":material/rocket_launch:", color="red")
    st.header("Pruebe el modelo", icon=":material/lab_research:", anchor="probar")
    st.markdown("Elija una radiografía del conjunto de prueba o suba la suya. El modelo responde en milisegundos "
                "con la probabilidad de neumonía, la decisión según el umbral de la barra lateral y el mapa de "
                "calor de las zonas que motivaron su respuesta.")
    vista_prediccion.render(ctx)

st.space("large")
recorrido()
