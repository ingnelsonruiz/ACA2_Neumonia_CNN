"""Página «El dataset»: origen, distribución, duplicados y partición por paciente."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CITA_DATASET, CITA_KAGGLE, COLOR_CLASE, CYAN, GREEN, PINK, VIOLET
from ui import estilo, kpi, mostrar, panel, seccion, tabla

NOMBRES_SPLIT = {"entrenamiento": "Entrenamiento", "validacion": "Validación", "prueba": "Prueba"}


def render(ctx):
    d = ctx.meta["dataset"]
    seccion("ORIGEN DE LOS DATOS")
    panel(f"<b>{d['nombre']}</b>. Radiografías anteroposteriores de tórax de pacientes pediátricos "
          "(1 a 5 años) del Guangzhou Women and Children's Medical Center, etiquetadas por médicos "
          "especialistas y revisadas por un tercer experto.<br><br>"
          f"<small>{CITA_DATASET}<br>{CITA_KAGGLE}</small>")

    c = st.columns(4)
    kpi(c[0], f"{d['archivos_totales']:,}", "Archivos descargados", CYAN)
    kpi(c[1], f"{d['duplicados']:,}", "Duplicados exactos", PINK,
                      "Archivos con el mismo hash MD5, eliminados antes de partir.")
    kpi(c[2], f"{d['imagenes_unicas']:,}", "Imágenes únicas", GREEN)
    # Total por partición: cada paciente está en una sola (sin fuga), y un mismo paciente puede
    # tener imágenes bacterianas y virales, así que sumar por subtipo lo contaría dos veces.
    pac = sum(r["pacientes"] for r in d["particiones"])
    kpi(c[3], f"{pac:,}", "Pacientes", VIOLET,
                      "Identificados a partir del nombre de archivo (personN / IM-NNNN).")

    dist = pd.DataFrame(d["distribucion"])
    izq, der = st.columns(2)
    with izq:
        seccion("DISTRIBUCIÓN POR CLASE Y SUBTIPO")
        fig = go.Figure(go.Bar(
            x=dist["subtipo"].str.capitalize(), y=dist["imagenes"],
            marker_color=[COLOR_CLASE[c] for c in dist["clase"]],
            text=[f"{n:,}<br>({p} %)" for n, p in zip(dist["imagenes"], dist["pct"])], textposition="outside"))
        fig.update_layout(yaxis_title="Imágenes", showlegend=False)
        mostrar(estilo(fig, alto=380))
        st.caption("Desbalance ≈ 3:1 a favor de neumonía → pesos de clase en la pérdida y métricas como F1 y "
                   "sensibilidad en lugar de solo exactitud.")
    with der:
        seccion("PARTICIÓN ESTRATIFICADA POR PACIENTE")
        part = pd.DataFrame(d["particiones"])
        part["split"] = part["split"].map(NOMBRES_SPLIT)
        fig = go.Figure()
        for col, nombre in [("normal", "NORMAL"), ("neumonia", "NEUMONIA")]:
            fig.add_trace(go.Bar(name=nombre, x=part["split"], y=part[col], marker_color=COLOR_CLASE[nombre]))
        fig.update_layout(barmode="stack", yaxis_title="Imágenes")
        mostrar(estilo(fig, alto=380))
        tabla(part.rename(columns={"split": "Partición", "imagenes": "Imágenes", "pacientes": "Pacientes",
                                   "neumonia": "Neumonía", "normal": "Normal", "pct_neumonia": "% neumonía"}))

    seccion("¿POR QUÉ PARTIR POR PACIENTE?")
    panel("Si dos radiografías del mismo niño caen una en entrenamiento y otra en prueba, el modelo puede "
          "reconocer rasgos del paciente (anatomía, posición, equipo) en lugar de la enfermedad, y las "
          "métricas de prueba quedan <b>infladas</b>. Con <code>StratifiedGroupKFold</code> cada paciente "
          "pertenece a una sola partición y la proporción de clases se mantiene en las tres; una consulta "
          "SQL en el notebook verifica que la intersección de pacientes sea vacía.")
