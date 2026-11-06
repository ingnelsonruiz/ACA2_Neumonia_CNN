"""Componentes reutilizables de interfaz, construidos con elementos nativos de Streamlit.

Todas las vistas usan estas funciones, así que un cambio aquí se refleja en toda la aplicación.
Los colores y la tipografía vienen del tema (.streamlit/config.toml), no de CSS.
"""

import re

import streamlit as st


# ── Figuras, tablas e imágenes ───────────────────────────────────────────────
def mostrar(fig, alt: str | None = None):
    """Dibuja una figura de Plotly ocupando todo el ancho disponible."""
    titulo = fig.layout.title.text if fig.layout.title and fig.layout.title.text else None
    st.plotly_chart(fig, width="stretch", alt=alt or titulo or "Gráfico interactivo",
                    config={"displaylogo": False})


def tabla(df, ocultar_indice=True, alt: str | None = None):
    """Dibuja un DataFrame ocupando todo el ancho disponible."""
    st.dataframe(df, width="stretch", hide_index=ocultar_indice, alt=alt or "Tabla de datos")


def imagen(img, pie=None, alt: str | None = None):
    """Muestra una imagen ocupando el ancho de su columna."""
    st.image(img, caption=pie, width="stretch", alt=alt or pie or "Radiografía de tórax")


def estilo(fig, alto=420, titulo=None):
    """Aplica el tema «negatoscopio» (claro, tinta azul película) a una figura de Plotly."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        height=alto,
        margin=dict(l=20, r=20, t=55 if titulo else 25, b=20),
        font=dict(family="Archivo, system-ui, sans-serif", size=14, color="#0F2A3D"),
        title=dict(text=oracion(titulo), font=dict(size=17, color="#0F2A3D")) if titulo else None,
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#C9D6DF", borderwidth=1),
        hoverlabel=dict(bgcolor="#0F2A3D", font_color="#FFFFFF"),
        separators=",.",
    )
    fig.update_xaxes(gridcolor="#E1E9EF", zerolinecolor="#C9D6DF", linecolor="#C9D6DF")
    fig.update_yaxes(gridcolor="#E1E9EF", zerolinecolor="#C9D6DF", linecolor="#C9D6DF")
    return fig


# ── Texto ────────────────────────────────────────────────────────────────────
# Las vistas escriben algunos títulos en mayúsculas; aquí se convierten a tipo oración
# conservando siglas y nombres propios.
_PROPIOS = {
    "sql": "SQL", "duckdb": "DuckDB", "cnn": "CNN", "f1": "F1", "roc": "ROC", "auc": "AUC",
    "roc-auc": "ROC-AUC", "cam": "CAM", "efficientnet-b0": "EfficientNet-B0", "efficientnet": "EfficientNet",
    "aca": "ACA", "ia": "IA", "onnx": "ONNX", "mbconv": "MBConv", "mbconv1": "MBConv1", "mbconv6": "MBConv6",
    "gap": "GAP", "imagenet": "ImageNet", "streamlit": "Streamlit", "softmax": "Softmax",
    "stem": "Stem", "cun": "CUN", "1×1": "1×1",
}


def oracion(texto):
    if not texto or not texto.isupper():
        return texto
    palabras = []
    for p in texto.lower().split(" "):
        nucleo = p.strip("(),.:")
        palabras.append(p.replace(nucleo, _PROPIOS[nucleo]) if nucleo in _PROPIOS else p)
    salida = " ".join(palabras).replace(" · ", ": ", 1).replace(" · ", ", ")
    return salida[:1].upper() + salida[1:]


_HTML_A_MD = [
    (r"<br\s*/?>\s*<br\s*/?>", "\n\n"), (r"<br\s*/?>", "  \n"),
    (r"</?b>", "**"), (r"</?i>", "*"), (r"</?code>", "`"),
    (r"(\w)<sub>([\w,]+)</sub>", r"$\1_{\2}$"),
]


def md(texto: str) -> str:
    """Convierte el HTML básico de los textos (<b>, <i>, <code>, <br>, <sub>) a Markdown."""
    texto = texto.replace("~", r"\~")          # evita que «~400 … ~2 900» se lea como tachado
    for patron, reemplazo in _HTML_A_MD:
        texto = re.sub(patron, reemplazo, texto)
    return texto


def _con_notas(texto: str):
    """Separa el texto principal de las notas en <small> (citas), que se muestran como pie."""
    notas = re.findall(r"<small>(.*?)</small>", texto, flags=re.S)
    return re.sub(r"<small>.*?</small>", "", texto, flags=re.S).strip(), notas


# ── Bloques de contenido ─────────────────────────────────────────────────────
def seccion(texto):
    """Encabezado de sección."""
    st.subheader(oracion(texto))


def panel(texto):
    """Bloque de texto explicativo enmarcado."""
    cuerpo, notas = _con_notas(texto)
    with st.container(border=True):
        st.markdown(md(cuerpo))
        for n in notas:
            st.caption(md(n))


def historia(texto, color=None, pregunta=None):
    """Bloque narrativo con la pregunta orientadora destacada."""
    with st.container(border=True):
        st.markdown(md(texto))
        if pregunta:
            st.info(pregunta, icon=":material/help:", title="Pregunta orientadora")


def es(texto: str) -> str:
    """Formato numérico en español: «11,712» → «11.712» y «0.974» → «0,974»."""
    return re.sub(r"\d[\d,.]*\d", lambda m: m.group().translate(str.maketrans(",.", ".,")), str(texto))


def kpi(contenedor, valor, etiqueta, color=None, ayuda=None):
    """Indicador con borde. `ayuda` se muestra en el icono de información junto a la etiqueta."""
    contenedor.metric(etiqueta, es(valor), help=ayuda, border=True)


def tarjeta(contenedor, titulo, texto, color=None, numero=None):
    """Tarjeta con título y texto; todas las de una fila comparten altura.

    `color` y `numero` se aceptan por compatibilidad con las vistas; el título ya lleva el número.
    """
    with contenedor.container(border=True, height="stretch"):
        st.markdown(f"**{oracion(titulo)}**")
        st.markdown(md(texto))


def miembro(contenedor, nombre, color=None, rol=""):
    """Ficha de integrante del equipo."""
    with contenedor.container(border=True):
        st.markdown(f":material/person: **{nombre}**")
        st.caption(rol)


def flujo(pasos, ancho=170):
    """Secuencia real de pasos (preprocesamiento, capas, metodología): una fila que se ajusta al ancho.

    `pasos` es una lista de tuplas (título, descripción) o (título, descripción, nota).
    """
    with st.container(horizontal=True, gap="small"):
        for paso in pasos:
            titulo, texto, *nota = paso
            with st.container(border=True, width=ancho, height="stretch"):
                st.markdown(f"**{oracion(titulo)}**")
                st.markdown(md(texto))
                if nota:
                    st.caption(nota[0])
