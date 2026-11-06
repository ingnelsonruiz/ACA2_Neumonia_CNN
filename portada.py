"""Portada: titular, resultados en prueba, película del negatoscopio y recorrido del proyecto."""

import base64
import io

import numpy as np
import streamlit as st
from PIL import Image

from ayuda import ayuda, expansor_indicadores
from config import LEMA, TITULO_APP
from modelo import cargar_imagen_gris, construir_contexto, predecir, superponer
from paginas import SECCIONES


def _png_base64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def _pelicula_portada(ruta: str, _mtime: float):
    """Radiografía de prueba con su mapa de activación, para la portada."""
    ctx = construir_contexto()
    img = cargar_imagen_gris(ruta, ctx.meta["preprocesamiento"]["tam_cache"])
    r = predecir(ctx, img)
    base = img.convert("L").resize((448, 448), Image.BILINEAR)
    cam = np.asarray(Image.fromarray((r.cam * 255).astype(np.uint8)).resize((448, 448), Image.BILINEAR)) / 255
    h, w = r.cam.shape
    # Proporción del mapa que cae dentro de la región torácica central (no en bordes ni marcadores)
    masa_central = float(r.cam[int(.15 * h):int(.85 * h), int(.18 * w):int(.82 * w)].sum() / (r.cam.sum() + 1e-8))
    return _png_base64(base), _png_base64(superponer(base, cam, 0.62)), r.prob_neumonia, masa_central


def _elegir_portada(ctx):
    """Neumonía de ejemplo detectada con alta confianza cuyo mapa cae más dentro de los pulmones."""
    candidatos = [e for e in ctx.ejemplos if not e.name.startswith("normal")]
    if not candidatos:
        return None
    datos = {e: _pelicula_portada(str(e), e.stat().st_mtime) for e in candidatos}
    seguros = [e for e, d in datos.items() if d[2] >= 0.9] or list(datos)
    return datos[max(seguros, key=lambda e: datos[e][3])][:3]


def _coma(v, dec=1):
    return f"{v:.{dec}f}".replace(".", ",")


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def portada(ctx):
    r = ctx.principal
    n_img = r["vp"] + r["fp"] + r["vn"] + r["fn"]
    n_pac = next((p["pacientes"] for p in ctx.meta["dataset"]["particiones"] if p["split"] == "prueba"), None)

    texto, pelicula = st.columns([1.15, 1], gap="large", vertical_alignment="center")
    with texto:
        st.markdown(f'''
<div class="hero">
  <h1 class="hero-titulo">{TITULO_APP}</h1>
  <p class="hero-lema">{LEMA}</p>
  <p class="hero-bajada">Una red neuronal convolucional lee radiografías de tórax de niños, señala las que
  muestran neumonía y marca en la imagen la zona que motivó su decisión.</p>
</div>''', unsafe_allow_html=True)
        # Rejilla fija 2 × 2: en el celular las columnas se apilan y las cuatro quedan del mismo ancho
        indicadores = [
            ("Neumonías detectadas", f"{_coma(r['recall_sensibilidad'] * 100)} %",
             "**Sensibilidad.** " + ayuda("Sensibilidad (recall)")),
            ("Sanos bien descartados", f"{_coma(r['especificidad'] * 100)} %",
             "**Especificidad.** " + ayuda("Especificidad")),
            ("F1 macro", _coma(r["f1_macro"], 3), ayuda("F1")),
            ("ROC-AUC", _coma(r["roc_auc"], 3), ayuda("ROC-AUC")),
        ]
        for fila in (indicadores[:2], indicadores[2:]):
            for col, (etiqueta, valor, ayuda_kpi) in zip(st.columns(2, gap="small"), fila):
                col.metric(etiqueta, valor, help=ayuda_kpi, border=True)
        st.caption(f"Resultados sobre {_miles(n_img)} radiografías de prueba"
                   + (f" de {_miles(n_pac)} pacientes" if n_pac else "")
                   + " que no participaron en el entrenamiento, con el umbral elegido en validación.")

    elegida = _elegir_portada(ctx)
    if elegida:
        b64_base, b64_cam, prob = elegida
        with pelicula:
            st.markdown(f'''
<figure class="negatoscopio">
  <div class="pelicula" role="img" aria-label="Radiografía de tórax con el mapa de activación del modelo">
    <img src="data:image/png;base64,{b64_base}" alt="">
    <img class="cam" src="data:image/png;base64,{b64_cam}" alt="">
    <div class="barrido"></div>
    <div class="anot si"><b>Tórax AP</b><br>Paciente pediátrico<br>Conjunto de prueba</div>
    <div class="anot sd"><b>EfficientNet-B0</b><br>Entrada 224 × 224<br>ONNX en CPU</div>
    <div class="anot ii">Mapa de activación<br>clase neumonía</div>
    <div class="anot id">P(neumonía) <span class="alerta">{_coma(prob, 3)}</span><br>Umbral {_coma(ctx.meta["umbral"], 2)}</div>
  </div>
  <figcaption>Radiografía real que el modelo nunca vio. El color marca las regiones que más
  aumentaron la probabilidad de neumonía.</figcaption>
</figure>''', unsafe_allow_html=True)

    expansor_indicadores(["Sensibilidad (recall)", "Especificidad", "F1", "ROC-AUC"])


def recorrido():
    st.header("Recorrido del proyecto", icon=":material/route:")
    st.caption("Cada bloque agrupa las páginas de un paso del ACA. También están en el menú lateral.")
    with st.container(horizontal=True, gap="medium"):
        for seccion, paginas in SECCIONES.items():
            with st.container(border=True, width=300, height="stretch"):
                st.markdown(f"**{seccion}**")
                for p in paginas:
                    st.page_link(p.ruta, label=p.titulo, icon=p.icono, help=p.descripcion)
                    st.caption(f"{p.paso} · {p.criterio}")
