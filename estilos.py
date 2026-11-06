"""CSS mínimo de la identidad «negatoscopio».

Colores, tipografías, bordes y barra lateral se configuran en .streamlit/config.toml (tema nativo).
Aquí solo queda lo que Streamlit no ofrece como elemento nativo, y todo se dirige a clases propias
o a contenedores con `key=` (clase `.st-key-<key>`), nunca a clases internas de Streamlit:

- la portada con la película en el negatoscopio (titular condensado, revelado del mapa de calor);
- el veredicto de la predicción y la «Lectura asistida por IA» con estilo de informe radiológico;
- el ancho de lectura del informe del proceso.
"""

import streamlit as st

CSS = """
<style>
:root {
    --tinta: #0F2A3D; --tinta-2: #4A6274; --plomo: #C9D6DF; --plomo-suave: #E1E9EF;
    --luz-alta: #F9FCFE; --azul: #1F5F8B; --rojo: #D93636; --verde: #1D8F7A; --ambar: #C98A12;
    --monos: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
}
:focus-visible { outline: 3px solid var(--azul); outline-offset: 2px; }

/* ── Portada: titular condensado, como los rótulos impresos en la película ── */
.hero .hero-titulo {
    font-family: Archivo, system-ui, sans-serif; font-variation-settings: "wdth" 62; font-stretch: 62%;
    font-weight: 850; font-size: clamp(3rem, 5.6vw, 5.6rem); line-height: 0.9; letter-spacing: -0.005em;
    color: var(--tinta); margin: 0 0 0.9rem; padding: 0; text-wrap: balance;
}
.hero .hero-lema {
    font-variation-settings: "wdth" 80; font-weight: 650; font-size: 1.3rem; line-height: 1.25;
    color: var(--azul); margin: 0 0 0.8rem; max-width: 32ch;
}
.hero .hero-bajada { font-size: 1.15rem; line-height: 1.5; color: var(--tinta-2); max-width: 44ch; margin: 0 0 0.6rem; }

/* ── El negatoscopio con la película ───────────────────────────────────── */
.negatoscopio {
    position: relative; margin: 0; padding: clamp(14px, 2vw, 22px); border-radius: 10px;
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
.negatoscopio figcaption { font-size: 0.85rem; color: var(--tinta-2); margin: 0.7rem 2px 0; line-height: 1.4; }
@media (max-width: 640px) { .anot { font-size: 0.6rem; } }
@media (prefers-reduced-motion: reduce) {
    .pelicula .cam { animation: none; clip-path: none; }
    .pelicula .barrido { display: none; }
}

/* ── Bloque «Pruebe el modelo»: el paso 5 en primer plano ──────────────── */
.st-key-demo { border-top: 6px solid var(--rojo) !important; background: #FFFFFF;
               box-shadow: 0 24px 50px -34px rgba(15,42,61,0.55); }

/* ── Veredicto de la predicción ────────────────────────────────────────── */
.veredicto-m, .veredicto-b, .veredicto-i {
    padding: 0.9rem 1.2rem; border-radius: 6px; text-align: center; color: #FFFFFF;
    font-variation-settings: "wdth" 65; font-weight: 850; font-size: 2.3rem; line-height: 1;
}
.veredicto-m { background: var(--rojo); } .veredicto-b { background: var(--verde); }
.veredicto-i { background: var(--ambar); font-size: 2rem; }

/* ── Lectura asistida por IA (informe de estilo radiológico) ───────────── */
.lectura-ia { margin-top: 1.4rem; border: 1px solid var(--plomo); border-radius: 6px; background: #FFFFFF; overflow: hidden; }
.lia-cab { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 1rem 1.3rem;
           background: var(--tinta); flex-wrap: wrap; }
.lia-tit { color: #FFFFFF; font-variation-settings: "wdth" 72; font-weight: 800; font-size: 1.6rem; line-height: 1.1; }
.lia-sub { color: #AFC4D3; font-size: 0.9rem; }
.lia-res { color: #FFFFFF; font-variation-settings: "wdth" 65; font-weight: 850; font-size: 1.5rem;
           padding: 0.35rem 0.9rem; border-radius: 4px; white-space: nowrap; }
.lia-res.res-m { background: var(--rojo); } .lia-res.res-b { background: var(--verde); } .lia-res.res-i { background: var(--ambar); }
.lia-campos { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 0;
              border-bottom: 1px solid var(--plomo); }
.lia-campos > div { padding: 0.75rem 1.3rem; border-right: 1px solid var(--plomo-suave); }
.lia-campos dt { font-size: 0.8rem; color: var(--tinta-2); font-weight: 600; }
.lia-campos dd { margin: 0.15rem 0 0; font-size: 1.05rem; font-weight: 700; line-height: 1.3; color: var(--tinta); }
.lia-campos dd small { display: block; font-size: 0.8rem; font-weight: 500; color: var(--tinta-2); }
.lia-cuerpo { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.lia-bloque { padding: 0.9rem 1.3rem 1rem; border-bottom: 1px solid var(--plomo-suave); }
.lia-bloque:nth-child(odd) { border-right: 1px solid var(--plomo-suave); }
.lia-bloque h5 { margin: 0 0 0.35rem; padding: 0; font-size: 0.82rem; font-weight: 750; color: var(--azul); }
.lia-bloque p, .lia-bloque li { font-size: 0.98rem; line-height: 1.5; margin: 0; }
.lia-bloque ul { margin: 0; padding-left: 1.1rem; }
.lia-bloque li + li { margin-top: 0.3rem; }
.lia-conclusion p { font-weight: 700; font-size: 1.08rem; }
.lia-qc { list-style: none; padding-left: 0 !important; }
.lia-qc li { position: relative; padding-left: 1.4rem; }
.lia-qc li::before { position: absolute; left: 0; top: 0; font-weight: 800; }
.lia-qc li.ok::before { content: "✓"; color: var(--verde); }
.lia-qc li.alerta::before { content: "!"; color: var(--ambar); }
.lia-qc li.alerta { color: #7A5300; }
.lia-pie { padding: 0.7rem 1.3rem; font-size: 0.85rem; color: var(--tinta-2); background: var(--luz-alta); }
@media (max-width: 900px) { .lia-cuerpo { grid-template-columns: 1fr; } .lia-bloque:nth-child(odd) { border-right: none; } }

/* ── Informe del proceso: ancho y ritmo de lectura ─────────────────────── */
.st-key-informe { max-width: 920px; }
.st-key-informe p, .st-key-informe li { font-size: 1.04rem; line-height: 1.68; }
</style>
"""


def aplicar():
    """Inyecta la hoja de estilos en la página."""
    st.html(CSS)
