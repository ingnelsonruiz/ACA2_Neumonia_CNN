"""Hoja de estilos «negatoscopio». Editar aquí cambia el aspecto de todas las vistas.

Concepto: la caja de luz donde se lee la película radiográfica. Fondo luminoso frío,
tinta azul de película y un único acento rojo (los marcadores de plomo «R»).
Una sola familia tipográfica, Archivo, usando su eje de ancho: condensada para titulares
(como los rótulos impresos en la película) y ancho normal para lectura.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap');

:root {
    --luz: #EEF3F7; --luz-alta: #F9FCFE; --tinta: #0F2A3D; --tinta-2: #4A6274;
    --plomo: #C9D6DF; --plomo-suave: #E1E9EF; --azul: #1F5F8B; --rojo: #D93636; --verde: #1D8F7A;
    --monos: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}

/* ── Base ─────────────────────────────────────────────────────────────── */
.stApp { background: var(--luz); }
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button {
    font-family: 'Archivo', system-ui, sans-serif !important;
    font-stretch: 100%;
}
.stApp p, .stApp li { color: var(--tinta); line-height: 1.5; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; max-width: 1320px; }
h1, h2, h3, h4 { font-family: 'Archivo', sans-serif !important; color: var(--tinta); }
/* Streamlit fija su propia fuente en el contenedor de markdown: se reemplaza salvo en código y anotaciones */
.stApp [data-testid="stMarkdownContainer"] :not(code):not(pre):not(.anot):not(.anot *):not([data-testid="stIconMaterial"]),
.stApp [data-testid="stWidgetLabel"] *, .stApp [data-baseweb="tab"] p,
.stApp [data-testid="stExpander"] summary p {
    font-family: 'Archivo', system-ui, sans-serif !important;
}
/* Color de texto fijado aquí y no en el tema: la app se lee bien aunque config.toml siga en «dark» */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] h4, [data-testid="stMain"] h5, [data-testid="stMain"] h6 { color: var(--tinta) !important; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] td,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] th,
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] label { color: var(--tinta) !important; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"] table { background: #FFFFFF; border-collapse: collapse; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"] th { background: var(--plomo-suave); font-weight: 700; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"] td,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] th { border: 1px solid var(--plomo) !important; padding: 6px 12px; }
/* Las clases propias conservan sus colores (más específicas que las reglas anteriores) */
[data-testid="stMain"] .nav-card.activa .nav-titulo { color: #FFFFFF !important; }
[data-testid="stMain"] .nav-card.activa p { color: #C9D9E5 !important; }
[data-testid="stMain"] .veredicto-m, [data-testid="stMain"] .veredicto-b { color: #FFFFFF !important; }
[data-testid="stMain"] .hero .bajada, [data-testid="stMain"] .lectura .l, [data-testid="stMain"] .hero .nota,
[data-testid="stMain"] .pie-pelicula, [data-testid="stMain"] .nav-card p, [data-testid="stMain"] .card p,
[data-testid="stMain"] .demo-cab p, [data-testid="stMain"] .nav-cab p, [data-testid="stMain"] .sec-cab p,
[data-testid="stMain"] .kpi-l, [data-testid="stMain"] .member .rol { color: var(--tinta-2) !important; }
[data-testid="stMain"] .lectura .rojo .v, [data-testid="stMain"] .demo-paso { color: var(--rojo) !important; }
[data-testid="stMain"] .nav-paso, [data-testid="stMain"] .story .q, [data-testid="stMain"] .step b,
[data-testid="stMain"] .ayuda-kpi b { color: var(--azul) !important; }
[data-testid="stMain"] .nav-card.activa .nav-paso { color: #9FD1FF !important; }
[data-testid="stMain"] .nav-card.activa .nav-nota { color: #FFFFFF !important; }
[data-testid="stMain"] .anot, [data-testid="stMain"] .anot * { color: #D6E8F7 !important; }
[data-testid="stMain"] .anot b { color: #FFFFFF !important; }
[data-testid="stMain"] .anot .alerta { color: #FF8A80 !important; }

/* Ancho condensado: font-stretch + eje variable explícito (algunos navegadores solo respetan uno) */
.hero h1, .card .n { font-variation-settings: "wdth" 62; }
.veredicto-m, .veredicto-b { font-variation-settings: "wdth" 65; }
.lectura .v, .kpi-v { font-variation-settings: "wdth" 70; }
.sec { font-variation-settings: "wdth" 75; }
.card h4, .step b { font-variation-settings: "wdth" 78; }
.story .q { font-variation-settings: "wdth" 80; }
code { color: var(--azul) !important; background: var(--plomo-suave) !important; }
:focus-visible { outline: 3px solid var(--azul) !important; outline-offset: 2px; }

/* ── Portada: titular + negatoscopio con la película ───────────────────── */
.hero {
    display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: clamp(1.5rem, 4vw, 3.5rem); align-items: center;
    padding: 1.2rem 0 2rem; margin-bottom: 0.6rem;
}
.hero h1 {
    font-family: 'Archivo', 'Archivo Narrow', 'Roboto Condensed', 'Arial Narrow', sans-serif !important;
    font-stretch: 62%; font-weight: 850; letter-spacing: -0.005em;
    font-size: clamp(3.4rem, 6.8vw, 7rem); line-height: 0.88; margin: 0 0 1.1rem; padding: 0;
    overflow-wrap: normal; word-break: keep-all; hyphens: none; text-wrap: balance;
    color: var(--tinta);
}
.hero .bajada { font-size: 1.22rem; line-height: 1.45; color: var(--tinta-2); max-width: 38ch; margin: 0 0 1.8rem; }
.lectura {
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.2rem;
    border-top: 2px solid var(--tinta); padding-top: 0.9rem; max-width: 620px;
}
.lectura .v { white-space: nowrap; font-stretch: 70%; font-weight: 750; font-size: 2.3rem; line-height: 1; color: var(--tinta);
              font-variant-numeric: tabular-nums; }
.lectura .l { font-size: 0.9rem; color: var(--tinta-2); margin-top: 0.3rem; line-height: 1.25; }
.lectura .rojo .v { color: var(--rojo); }
.hero .nota { font-size: 0.85rem; color: var(--tinta-2); margin-top: 0.9rem; max-width: 60ch; }

.negatoscopio {
    position: relative; padding: clamp(14px, 2vw, 22px); border-radius: 10px;
    background: linear-gradient(180deg, #FFFFFF 0%, #E6EFF5 100%);
    box-shadow: 0 0 0 1px var(--plomo), 0 0 60px 6px rgba(255,255,255,0.9), 0 40px 70px -40px rgba(15,42,61,0.55);
}
.negatoscopio::before {           /* pinza que sujeta la película */
    content: ""; position: absolute; top: 6px; left: 50%; width: 64px; height: 8px; margin-left: -32px;
    border-radius: 3px; background: #9FB2C0;
}
.pelicula { position: relative; aspect-ratio: 1 / 1; overflow: hidden; border-radius: 3px; background: #000; }
.pelicula img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.pelicula .cam { clip-path: inset(0 0 100% 0); animation: revelar 3.2s cubic-bezier(.55,0,.25,1) .5s forwards; }
.pelicula .barrido {
    position: absolute; left: 0; right: 0; top: 0; height: 2px; opacity: 0;
    background: #FFE2A8; box-shadow: 0 0 16px 5px rgba(255,196,110,0.75);
    animation: barrer 3.2s cubic-bezier(.55,0,.25,1) .5s forwards;
}
@keyframes revelar { to { clip-path: inset(0 0 0 0); } }
@keyframes barrer { 0% { top: 0; opacity: 1; } 96% { top: 100%; opacity: 1; } 100% { top: 100%; opacity: 0; } }
.anot {
    position: absolute; font-family: var(--monos); font-size: 0.72rem; line-height: 1.4;
    color: #D6E8F7; text-shadow: 0 1px 2px #000; pointer-events: none;
}
.anot.si { top: 10px; left: 12px; } .anot.sd { top: 10px; right: 12px; text-align: right; }
.anot.ii { bottom: 10px; left: 12px; } .anot.id { bottom: 10px; right: 12px; text-align: right; }
.anot b { color: #FFFFFF; font-weight: 600; }
.anot .alerta { color: #FF8A80; font-weight: 700; }
.pie-pelicula { font-size: 0.85rem; color: var(--tinta-2); margin: 0.7rem 2px 0; line-height: 1.35; }

@media (prefers-reduced-motion: reduce) {
    .pelicula .cam { animation: none; clip-path: none; }
    .pelicula .barrido { display: none; }
}
@media (max-width: 900px) {
    .hero { grid-template-columns: 1fr; }
    .lectura { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

/* ── Indicadores ──────────────────────────────────────────────────────── */
.kpi {
    background: #FFFFFF; border: 1px solid var(--plomo); border-top: 4px solid var(--c);
    border-radius: 4px; padding: 0.9rem 1rem 0.8rem; height: 100%;
}
.kpi-v { font-stretch: 70%; font-weight: 750; font-size: 2rem; line-height: 1.05; color: var(--tinta);
         font-variant-numeric: tabular-nums; }
.kpi-l { color: var(--tinta-2); font-size: 0.92rem; margin-top: 4px; line-height: 1.25; }
.kpi[title] { cursor: help; }

/* ── Tarjetas, narrativa y paneles ────────────────────────────────────── */
.card {
    background: #FFFFFF; border: 1px solid var(--plomo); border-radius: 4px;
    padding: 1.1rem 1.2rem; height: 100%; position: relative;
}
.card::before { content: ""; position: absolute; left: -1px; top: 14px; bottom: 14px; width: 3px; background: var(--c); }
.card h4 { font-stretch: 78%; font-weight: 750; font-size: 1.15rem; margin: 0 0 6px; padding: 0; color: var(--tinta); }
.card p { color: var(--tinta-2); font-size: 1rem; margin: 0; line-height: 1.45; }
.card .n { font-stretch: 62%; font-weight: 850; font-size: 2.4rem; line-height: 1; color: var(--c); margin-bottom: 4px; }

.story {
    background: #FFFFFF; border: 1px solid var(--plomo); border-left: 4px solid var(--c);
    border-radius: 4px; padding: 1.3rem 1.6rem; margin-bottom: 0.8rem;
    color: var(--tinta); font-size: 1.1rem; line-height: 1.6; max-width: 900px;
}
.story b { color: var(--tinta); }
.story .q {
    display: block; margin-top: 1rem; padding-top: 0.9rem; border-top: 1px solid var(--plomo-suave);
    font-stretch: 80%; font-weight: 700; font-size: 1.45rem; line-height: 1.25; color: var(--azul);
}

.panel {
    background: var(--luz-alta); border: 1px solid var(--plomo); border-radius: 4px;
    padding: 1rem 1.3rem; color: var(--tinta); font-size: 1.02rem; line-height: 1.55; max-width: 1000px;
}
.panel b { color: var(--tinta); }

.sec {
    font-stretch: 75%; font-weight: 750; font-size: 1.55rem; color: var(--tinta);
    margin: 1.8rem 0 0.7rem; padding-bottom: 0.35rem; border-bottom: 1px solid var(--plomo);
}

/* ── Secuencias (pasos reales del flujo) ──────────────────────────────── */
.flow { display: flex; flex-wrap: wrap; gap: 8px; align-items: stretch; margin: 0.6rem 0 0.6rem; }
.step {
    flex: 1 1 140px; background: #FFFFFF; border: 1px solid var(--plomo); border-top: 3px solid var(--azul);
    border-radius: 4px; padding: 0.75rem 0.8rem;
}
.step b { display: block; font-stretch: 78%; font-weight: 750; font-size: 0.98rem; color: var(--azul); margin-bottom: 3px; }
.step span { color: var(--tinta); font-size: 0.93rem; line-height: 1.3; }
.step small { display: block; color: var(--tinta-2); font-size: 0.8rem; margin-top: 5px; }
.flecha { flex: 0 0 auto; align-self: center; color: #9FB2C0; font-size: 1.1rem; }

/* ── Integrantes ──────────────────────────────────────────────────────── */
.member {
    display: flex; align-items: center; gap: 14px; background: #FFFFFF; border: 1px solid var(--plomo);
    border-radius: 4px; padding: 0.8rem 1rem; margin-bottom: 10px;
}
.avatar {
    flex: 0 0 46px; width: 46px; height: 46px; border-radius: 4px; display: flex; align-items: center;
    justify-content: center; font-stretch: 70%; font-weight: 800; font-size: 1.15rem;
    color: #FFFFFF; background: var(--c);
}
.member .nom { color: var(--tinta); font-size: 1.08rem; font-weight: 650; }
.member .rol { color: var(--tinta-2); font-size: 0.9rem; }

/* ── Veredicto de la predicción ───────────────────────────────────────── */
.veredicto-m, .veredicto-b {
    padding: 1rem 1.2rem; border-radius: 4px; text-align: center; color: #FFFFFF;
    font-stretch: 65%; font-weight: 850; font-size: 2.4rem; line-height: 1;
}
.veredicto-m { background: var(--rojo); }
.veredicto-b { background: var(--verde); }

.ayuda-kpi { color: var(--tinta); font-size: 0.98rem; line-height: 1.5; }
.ayuda-kpi b { color: var(--azul); }
.aviso { color: var(--tinta-2); font-size: 0.85rem; text-align: center; margin-top: 2.5rem;
         padding-top: 1rem; border-top: 1px solid var(--plomo); }

/* ── Pestañas ─────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important; gap: 2px !important; flex-wrap: wrap !important;
    border-bottom: 1px solid var(--plomo) !important; overflow: visible !important;
}
[data-baseweb="tab"] {
    background: transparent !important; color: var(--tinta-2) !important; height: 42px !important;
    padding: 0 12px !important; border-radius: 4px 4px 0 0 !important; white-space: nowrap !important;
}
[data-baseweb="tab"] p { font-weight: 600 !important; font-size: 0.92rem !important; color: inherit !important; }
[data-baseweb="tab"]:hover { background: #FFFFFF !important; color: var(--tinta) !important; }
[data-baseweb="tab"][aria-selected="true"] { background: #FFFFFF !important; color: var(--tinta) !important; }
[data-baseweb="tab-highlight"] { background-color: var(--azul) !important; height: 3px !important; }
[data-baseweb="tab-border"] { display: none !important; }
[data-baseweb="tab-list"] > button:not([data-baseweb="tab"]) { display: none !important; }

/* ── Barra lateral: consola del visor ─────────────────────────────────── */
section[data-testid="stSidebar"] { background: var(--tinta); border-right: none; }
section[data-testid="stSidebar"] * { color: #DCE7EF !important; }
section[data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-stretch: 75%; font-weight: 750; font-size: 1.3rem; }
section[data-testid="stSidebar"] hr { border-color: rgba(220,231,239,0.18) !important; }
section[data-testid="stSidebar"] a { color: #9FD1FF !important; }

/* Expansores */
[data-testid="stExpander"] { background: #FFFFFF; border: 1px solid var(--plomo) !important; border-radius: 4px; }
[data-testid="stExpander"] summary p { font-weight: 600 !important; }
/* ── Bloque «Pruebe el modelo» (paso 5 en primer plano) ───────────────── */
.demo-cab { margin: 0.6rem 0 0.8rem; max-width: 900px; }
.demo-cab h2, .nav-cab h2, .sec-cab h2 {
    font-stretch: 68%; font-variation-settings: "wdth" 68; font-weight: 850; color: var(--tinta);
    font-size: clamp(2.2rem, 4vw, 3.2rem); line-height: 0.95; margin: 0.2rem 0 0.5rem; padding: 0;
}
.demo-cab p, .nav-cab p, .sec-cab p { color: var(--tinta-2); font-size: 1.08rem; max-width: 70ch; margin: 0; }
.demo-paso, .nav-paso { font-size: 0.85rem; font-weight: 700; color: var(--azul); }
.demo-paso { color: var(--rojo); }
.st-key-demo {
    background: #FFFFFF; border: 1px solid var(--plomo); border-top: 6px solid var(--rojo); border-radius: 6px;
    padding: 1.2rem 1.4rem 1.4rem; box-shadow: 0 24px 50px -34px rgba(15,42,61,0.55); margin-bottom: 2.6rem;
}

/* ── Recorrido: tarjetas que funcionan como botones ───────────────────── */
.nav-cab { margin: 1rem 0 0.9rem; padding-top: 1.2rem; border-top: 2px solid var(--tinta); }
[class*="st-key-nav_"] { position: relative; height: 100%; gap: 0 !important; }
[class*="st-key-nav_"] [data-testid="stElementContainer"]:has(.stButton),
[class*="st-key-nav_"] .stButton {
    position: absolute !important; inset: 0; margin: 0 !important; z-index: 3; height: 100%;
}
[class*="st-key-nav_"] .stButton button {
    width: 100%; height: 100%; min-height: 100%; opacity: 0; cursor: pointer; border: none;
}
.nav-card {
    background: #FFFFFF; border: 1px solid var(--plomo); border-radius: 6px; padding: 0.95rem 1.1rem 1rem;
    min-height: 212px; height: 100%; display: flex; flex-direction: column; gap: 0.25rem;
    transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease;
}
.nav-titulo {
    font-stretch: 70%; font-variation-settings: "wdth" 70; font-weight: 800; font-size: 1.65rem; line-height: 1.05;
    color: var(--tinta);
}
.nav-card p { color: var(--tinta-2); font-size: 0.93rem; line-height: 1.4; margin: 0.15rem 0 0.4rem; flex: 1; }
.nav-nota {
    align-self: flex-start; font-size: 0.78rem; font-weight: 600; color: var(--tinta);
    background: var(--plomo-suave); border-radius: 999px; padding: 2px 9px;
}
.st-key-nav_informe .nav-titulo { font-size: 2.1rem; }
[class*="st-key-nav_"]:hover .nav-card {
    border-color: var(--azul); transform: translateY(-2px); box-shadow: 0 14px 28px -18px rgba(15,42,61,0.55);
}
[class*="st-key-nav_"]:has(button:focus-visible) .nav-card { outline: 3px solid var(--azul); outline-offset: 2px; }
.nav-card.activa { background: var(--tinta); border-color: var(--tinta); }
.nav-card.activa .nav-titulo { color: #FFFFFF; }
.nav-card.activa p { color: #C9D9E5; }
.nav-card.activa .nav-paso { color: #9FD1FF; }
.nav-card.activa .nav-nota { background: rgba(255,255,255,0.14); color: #FFFFFF; }
@media (prefers-reduced-motion: reduce) { .nav-card { transition: none; } [class*="st-key-nav_"]:hover .nav-card { transform: none; } }

/* ── Encabezado de la sección abierta ─────────────────────────────────── */
.sec-cab { margin: 2.4rem 0 0.4rem; padding-top: 1.1rem; border-top: 2px solid var(--tinta); }
.sec-cab .nav-paso .nav-nota { margin-left: 0.5rem; font-weight: 600; }

/* ── Informe del proceso ──────────────────────────────────────────────── */
.st-key-informe { max-width: 920px; }
.st-key-informe p, .st-key-informe li { font-size: 1.04rem; line-height: 1.68; }
.st-key-informe h3 {
    font-stretch: 75%; font-variation-settings: "wdth" 75; font-weight: 800; font-size: 1.7rem;
    margin: 1.8rem 0 0.4rem; padding: 0; border-bottom: 1px solid var(--plomo); padding-bottom: 0.3rem;
}
.st-key-informe h4 { font-weight: 750; font-size: 1.15rem; margin-top: 1.2rem; }
.st-key-informe table { font-size: 0.95rem; background: #FFFFFF; }
.st-key-informe [data-testid="stImageCaption"], .st-key-informe [data-testid="caption"] {
    color: var(--tinta-2) !important; font-size: 0.9rem !important; text-align: left;
}
</style>
"""


def aplicar():
    """Inyecta la hoja de estilos en la página."""
    st.markdown(CSS, unsafe_allow_html=True)
