"""Bloque «Pruebe el modelo» de Inicio: inferencia en tiempo real con mapa de activación."""

import plotly.graph_objects as go
import streamlit as st

from config import AMBER, CYAN, GREEN, PINK
from PIL import Image

from lectura import generar_lectura, texto_plano
from modelo import cargar_imagen_gris, clase_predicha, predecir, superponer
from ui import estilo, imagen, mostrar


def _medidor(prob, umbral):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=prob * 100, number=dict(suffix=" %", font=dict(size=40)),
        title=dict(text="Probabilidad de neumonía"),
        gauge=dict(axis=dict(range=[0, 100]), bar=dict(color=PINK if prob >= umbral else GREEN),
                   steps=[dict(range=[0, umbral * 100], color="rgba(29,143,122,0.14)"),
                          dict(range=[umbral * 100, 100], color="rgba(217,54,54,0.14)")],
                   threshold=dict(line=dict(color=AMBER, width=4), value=umbral * 100))))
    fig = estilo(fig, alto=300)
    fig.update_layout(margin=dict(l=35, r=35, t=40, b=10))
    return fig


def render(ctx):
    opciones = [":material/photo_library: Usar un ejemplo de prueba", ":material/upload: Subir mi radiografía"]
    eleccion = st.segmented_control("Origen de la imagen", opciones, default=opciones[0], required=True,
                                    key="origen_imagen")
    fuente = "Subir radiografía" if eleccion == opciones[1] else "Ejemplos del conjunto de prueba"
    if fuente == "Subir radiografía":
        archivo = st.file_uploader("Radiografía de tórax AP (JPG o PNG)", type=["jpg", "jpeg", "png"])
        if archivo is None:
            st.info("Suba una imagen para analizarla, o use los ejemplos.", icon=":material/upload:")
            return
        original = Image.open(archivo); original.load()
        archivo.seek(0)
        origen, etiqueta_real, nombre, es_ejemplo = archivo, None, archivo.name, False
    else:
        if not ctx.ejemplos:
            st.info("No hay ejemplos disponibles en artefactos/ejemplos.", icon=":material/info:")
            return
        nombres = [e.name for e in ctx.ejemplos]
        # Abre con un caso ilustrativo (activación dentro del pulmón) si existe
        inicial = next((nombres.index(n) for n in ("virus_2.jpeg", "bacteria_2.jpeg") if n in nombres), 0)
        nombre = st.selectbox("Radiografía", nombres, index=inicial)
        origen = next(e for e in ctx.ejemplos if e.name == nombre)
        etiqueta_real = "NORMAL" if nombre.startswith("normal") else "NEUMONIA"
        original, es_ejemplo = Image.open(origen), True

    img = cargar_imagen_gris(origen, ctx.meta["preprocesamiento"]["tam_cache"])
    r = predecir(ctx, img)
    lec = generar_lectura(r.prob_neumonia, ctx.umbral, r.cam, original, es_ejemplo)
    clase = clase_predicha(r.prob_neumonia, ctx.umbral)

    izq, centro, der = st.columns([1, 1, 1])
    with izq:
        imagen(img, "Radiografía (preprocesada)")
    with centro:
        opacidad = st.slider("Opacidad del mapa de calor", 0.0, 1.0, 0.5, 0.05)
        # En un caso negativo el mapa normalizado amplifica ruido: se atenúa según la probabilidad
        atenuacion = 1.0 if clase == "NEUMONIA" else min(1.0, r.prob_neumonia / max(ctx.umbral, 1e-6))
        pie = ("Mapa de activación (CAM) para «neumonía»" if atenuacion == 1.0 else
               "Mapa atenuado: el modelo no encuentra evidencia de neumonía")
        imagen(superponer(img, r.cam, opacidad * atenuacion), pie)
    with der:
        mostrar(_medidor(r.prob_neumonia, ctx.umbral))
        css = {"NEUMONÍA": "veredicto-m", "NORMAL": "veredicto-b"}.get(lec.resultado, "veredicto-i")
        st.markdown(f'<div class="{css}">{lec.resultado}</div>', unsafe_allow_html=True)
        st.caption(f"Umbral activo {ctx.umbral:.2f}, inferencia en {r.milisegundos:.0f} ms en CPU".replace(".", ","))
        if etiqueta_real:
            if etiqueta_real == clase:
                st.badge(f"Etiqueta real: {etiqueta_real}, coincide", icon=":material/check_circle:", color="green")
            else:
                st.badge(f"Etiqueta real: {etiqueta_real}, no coincide", icon=":material/cancel:", color="red")

    _informe(lec, nombre)


def _informe(lec, nombre):
    clase_res = {"NEUMONÍA": "res-m", "NORMAL": "res-b"}.get(lec.resultado, "res-i")
    campos = [("Probabilidad de neumonía", f"{lec.probabilidad * 100:.1f}".replace(".", ",") + " %"),
              ("Confianza del modelo", lec.confianza.capitalize()),
              ("Umbral operativo", f"{lec.umbral * 100:.0f} %")]
    if lec.localizacion:
        campos.append(("Localización de la evidencia", lec.localizacion))
    if lec.extension:
        tipo, _, detalle = lec.extension.partition(" (")
        campos.append(("Extensión", f"{tipo.capitalize()}<small>{detalle.rstrip(')')}</small>"))
    campos_html = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in campos)
    hallazgos = "".join(f"<li>{h}</li>" for h in lec.hallazgos)
    calidad = "".join(f'<li class="{n}">{t}</li>' for n, t in lec.calidad)
    st.markdown(f'''
<div class="lectura-ia">
  <div class="lia-cab">
    <div><div class="lia-tit">Lectura asistida por IA</div>
         <div class="lia-sub">Radiografía de tórax AP, {nombre}</div></div>
    <div class="lia-res {clase_res}">{lec.resultado}</div>
  </div>
  <dl class="lia-campos">{campos_html}</dl>
  <div class="lia-cuerpo">
    <div class="lia-bloque"><h5>Hallazgos</h5><ul>{hallazgos}</ul></div>
    <div class="lia-bloque lia-conclusion"><h5>Conclusión</h5><p>{lec.conclusion}</p></div>
    <div class="lia-bloque"><h5>Sugerencia</h5><p>{lec.sugerencia}</p></div>
    <div class="lia-bloque"><h5>Control de calidad</h5><ul class="lia-qc">{calidad}</ul></div>
  </div>
  <div class="lia-pie">Prototipo académico entrenado con radiografías pediátricas (1 a 5 años) de un único
  hospital. No es un dispositivo médico ni sustituye la lectura de un radiólogo.</div>
</div>''', unsafe_allow_html=True)
    st.download_button("Descargar esta lectura (.txt)", icon=":material/download:", data= texto_plano(lec, nombre).encode("utf-8"),
                       file_name=f"lectura_{nombre.rsplit('.', 1)[0]}.txt", mime="text/plain")
    with st.expander("¿Cómo se genera esta lectura?", icon=":material/help:"):
        st.markdown(
            "- **Resultado y confianza** salen de la probabilidad del modelo frente al umbral elegido en validación. "
            "Si la probabilidad queda a menos de 5 puntos del umbral, el caso se declara indeterminado.\n"
            "- **Localización** se calcula sobre el mapa de activación: qué hemitórax concentra la activación alta y "
            "en qué tercio vertical está su centro. En la imagen, la izquierda corresponde al lado derecho del "
            "paciente (marcador «R»).\n"
            "- **Extensión** es la proporción del campo torácico con activación alta (focal < 12 %, extensa > 30 %).\n"
            "- **Control de calidad** revisa color, resolución, proporción y contraste de la imagen, y si la "
            "activación cae dentro del tórax o en bordes y marcadores.\n"
            "- El modelo es binario: **no distingue neumonía bacteriana de viral ni estima gravedad**, y sus "
            "probabilidades no están calibradas como riesgo clínico.")
