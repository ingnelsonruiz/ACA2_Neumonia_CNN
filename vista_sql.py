"""Página «Consultas SQL»: exploración de la base DuckDB construida en el notebook (solo lectura)."""

import re

import streamlit as st

from config import RUTA_DB
from ui import panel, seccion, tabla

CONSULTAS = {
    "Distribución por clase y subtipo": """
SELECT clase, subtipo, COUNT(*) AS imagenes, COUNT(DISTINCT paciente_id) AS pacientes
FROM imagenes_unicas
GROUP BY clase, subtipo
ORDER BY clase, subtipo""",
    "Resumen de particiones": """
SELECT split, COUNT(*) AS imagenes, COUNT(DISTINCT paciente_id) AS pacientes,
       ROUND(100.0 * AVG(CASE WHEN clase = 'NEUMONIA' THEN 1 ELSE 0 END), 1) AS pct_neumonia
FROM v_dataset
GROUP BY split
ORDER BY imagenes DESC""",
    "Verificación de fuga: pacientes en más de una partición": """
SELECT paciente_id, COUNT(DISTINCT split) AS particiones
FROM v_dataset
GROUP BY paciente_id
HAVING COUNT(DISTINCT split) > 1""",
    "Duplicados exactos por hash": """
SELECT hash_md5, COUNT(*) AS copias, ANY_VALUE(archivo) AS ejemplo
FROM imagenes
GROUP BY hash_md5
HAVING COUNT(*) > 1
ORDER BY copias DESC
LIMIT 50""",
    "Pacientes con más radiografías": """
SELECT paciente_id, clase, COUNT(*) AS radiografias
FROM imagenes_unicas
GROUP BY paciente_id, clase
ORDER BY radiografias DESC
LIMIT 20""",
    "Dimensiones originales por clase": """
SELECT clase, ROUND(AVG(ancho)) AS ancho_medio, ROUND(AVG(alto)) AS alto_medio,
       MIN(ancho) AS ancho_min, MAX(ancho) AS ancho_max, ROUND(AVG(bytes) / 1024) AS kb_medio
FROM imagenes_unicas
GROUP BY clase""",
    "Errores del modelo en prueba por subtipo": """
SELECT d.subtipo, COUNT(*) AS imagenes,
       SUM(1 - p.acierto) AS errores,
       ROUND(100.0 * AVG(p.acierto), 2) AS pct_acierto,
       ROUND(AVG(p.p_neumonia), 3) AS prob_media_neumonia
FROM predicciones_prueba p JOIN v_dataset d USING (idx_cache)
GROUP BY d.subtipo
ORDER BY d.subtipo""",
    "Falsos negativos más seguros (neumonías que el modelo descartó)": """
SELECT d.archivo, d.subtipo, ROUND(p.p_neumonia, 4) AS p_neumonia
FROM predicciones_prueba p JOIN v_dataset d USING (idx_cache)
WHERE d.clase = 'NEUMONIA' AND p.pred = 0
ORDER BY p.p_neumonia
LIMIT 20""",
}

PROHIBIDAS = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|ATTACH|DETACH|COPY|EXPORT|IMPORT|"
                        r"INSTALL|LOAD|PRAGMA|SET|CALL|CHECKPOINT)\b", re.IGNORECASE)


def _es_segura(sql: str) -> tuple[bool, str]:
    limpio = sql.strip().rstrip(";").strip()
    if ";" in limpio:
        return False, "Solo se permite una sentencia por ejecución."
    if not re.match(r"^\s*(SELECT|WITH|DESCRIBE|SHOW|SUMMARIZE)\b", limpio, re.IGNORECASE):
        return False, "Solo se permiten consultas de lectura (SELECT, WITH, DESCRIBE, SHOW, SUMMARIZE)."
    if PROHIBIDAS.search(limpio):
        return False, "La consulta contiene instrucciones de escritura o administración."
    return True, limpio


@st.cache_data(show_spinner=False, ttl=600)
def _ejecutar(sql: str):
    import duckdb
    with duckdb.connect(str(RUTA_DB), read_only=True) as con:
        return con.sql(sql).df().head(1000)


def render(ctx):
    seccion("BASE DE DATOS DUCKDB")
    if not ctx.hay_db:
        panel("No se encontró <code>chest_xray.duckdb</code> en la raíz del repositorio. Viene incluido en "
              "<code>artefactos_aca2.zip</code>; cópielo junto a <code>app.py</code> para habilitar esta página.")
        return
    panel("El notebook guarda el inventario de imágenes en una base analítica <b>DuckDB</b> (un solo archivo, "
          "sin servidor). Tablas: <code>imagenes</code> (todos los archivos), <code>imagenes_unicas</code> "
          "(deduplicadas), <code>particiones</code>, <code>predicciones_prueba</code> y la vista "
          "<code>v_dataset</code>. La conexión es de <b>solo lectura</b> y el resultado se limita a 1 000 filas.")

    with st.expander("Esquema de las tablas"):
        for t in ["imagenes_unicas", "particiones", "predicciones_prueba", "v_dataset"]:
            try:
                st.markdown(f"**{t}**")
                tabla(_ejecutar(f"DESCRIBE {t}")[["column_name", "column_type"]])
            except Exception as e:                       # tabla ausente en versiones antiguas del notebook
                st.caption(f"No disponible: {e}")

    nombre = st.selectbox("Consulta predefinida", list(CONSULTAS))
    sql = st.text_area("SQL (puede editarla)", CONSULTAS[nombre].strip(), height=180, key=f"sql_{nombre}")
    if st.button("Ejecutar consulta", type="primary", icon=":material/play_arrow:"):
        ok, resultado = _es_segura(sql)
        if not ok:
            st.error(resultado)
            return
        try:
            df = _ejecutar(resultado)
            st.success(f"{len(df):,} filas")
            tabla(df)
        except Exception as e:
            st.error(f"Error de SQL: {e}")
