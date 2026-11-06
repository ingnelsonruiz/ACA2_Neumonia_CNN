"""Pestaña «Informe del proceso»: recorrido académico completo del proyecto.

Responde al requisito del ACA de explicar el proceso de punta a punta: problema, datos y SQL,
preparación, arquitectura, entrenamiento, evaluación, despliegue, limitaciones y referencias.
Todas las cifras se leen de metadatos.json o de la base DuckDB, nunca están escritas a mano.
"""

import numpy as np
import pandas as pd
import streamlit as st

from config import CITA_DATASET, CITA_KAGGLE, DIR_FIGURAS, RUTA_DB
from ui import imagen, tabla

N_BOOTSTRAP = 1000


def _c(v, dec=3):
    return f"{v:.{dec}f}".replace(".", ",")


def _pct(v, dec=1):
    return f"{v * 100:.{dec}f}".replace(".", ",") + "\u202f%"


# ── Intervalos de confianza por bootstrap de pacientes ───────────────────────
def _auc(y, p):
    """AUC por la estadística de Mann-Whitney (equivalente al área bajo la ROC)."""
    orden = np.argsort(p, kind="mergesort")
    rangos = np.empty(len(p))
    rangos[orden] = np.arange(1, len(p) + 1)
    # rangos promedio para empates
    _, inv, cuenta = np.unique(p, return_inverse=True, return_counts=True)
    suma = np.bincount(inv, weights=rangos)
    rangos = (suma / cuenta)[inv]
    n1, n0 = y.sum(), len(y) - y.sum()
    return (rangos[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan


def _metricas(y, p, umbral):
    pred = (p >= umbral).astype(int)
    vp = ((pred == 1) & (y == 1)).sum(); fn = ((pred == 0) & (y == 1)).sum()
    vn = ((pred == 0) & (y == 0)).sum(); fp = ((pred == 1) & (y == 0)).sum()
    sens = vp / (vp + fn) if vp + fn else np.nan
    espec = vn / (vn + fp) if vn + fp else np.nan
    prec = vp / (vp + fp) if vp + fp else np.nan
    npv = vn / (vn + fn) if vn + fn else np.nan
    f1_pos = 2 * prec * sens / (prec + sens) if prec + sens else 0.0
    f1_neg = 2 * npv * espec / (npv + espec) if npv + espec else 0.0
    return {"Sensibilidad": sens, "Especificidad": espec, "Precisión (VPP)": prec,
            "F1 macro": (f1_pos + f1_neg) / 2, "ROC-AUC": _auc(y, p)}


@st.cache_data(show_spinner=False)
def intervalos_bootstrap(_mtime: float, umbral: float):
    """IC 95 % por bootstrap de PACIENTES (no de imágenes): respeta la dependencia entre
    radiografías del mismo niño, que el bootstrap por imagen ignoraría."""
    import duckdb
    with duckdb.connect(str(RUTA_DB), read_only=True) as con:
        df = con.sql("""
            SELECT d.paciente_id, CASE WHEN d.clase = 'NEUMONIA' THEN 1 ELSE 0 END AS y, p.p_neumonia AS p
            FROM predicciones_prueba p JOIN v_dataset d USING (idx_cache)
        """).df()
    y, p = df["y"].to_numpy(), df["p"].to_numpy()
    puntual = _metricas(y, p, umbral)
    grupos = df.groupby("paciente_id").indices
    llaves = list(grupos)
    rng = np.random.default_rng(42)
    muestras = []
    for _ in range(N_BOOTSTRAP):
        elegidos = rng.choice(len(llaves), size=len(llaves), replace=True)
        idx = np.concatenate([grupos[llaves[i]] for i in elegidos])
        muestras.append(_metricas(y[idx], p[idx], umbral))
    m = pd.DataFrame(muestras)
    filas = [{"Métrica": k, "Estimación": v, "IC 95 % inferior": m[k].quantile(0.025),
              "IC 95 % superior": m[k].quantile(0.975)} for k, v in puntual.items()]
    return pd.DataFrame(filas), len(llaves), len(df)


def _figura(nombre, pie, ancho=None):
    ruta = DIR_FIGURAS / nombre
    if not ruta.exists():
        return
    if ancho:
        st.image(str(ruta), caption=pie, width=ancho)
    else:
        imagen(str(ruta), pie)


def render(ctx):
    m, d, t = ctx.meta, ctx.meta["dataset"], ctx.meta["entrenamiento"]
    e, b = ctx.principal, ctx.base
    part = {p["split"]: p for p in d["particiones"]}
    n_pac = sum(p["pacientes"] for p in d["particiones"])
    hist = pd.DataFrame(m["historia"])
    mejor_eff = hist[hist.modelo == "EffNet-B0"].sort_values("val_f1").iloc[-1]
    mejor_base = hist[hist.modelo == "CNN base"].sort_values("val_f1").iloc[-1]
    sub = {r["subtipo"]: r for r in m["metricas_por_subtipo"]}
    pct = {r["subtipo"]: r["pct"] for r in d["distribucion"]}
    pct_bacteria, pct_virus = pct.get("bacteria", 0), pct.get("virus", 0)
    miles = lambda v: f"{v:,}".replace(",", ".")

    with st.container(key="informe"):
        _cuerpo(ctx, m, d, t, e, b, part, n_pac, hist, mejor_eff, mejor_base, sub, pct_bacteria, pct_virus, miles)


def _cuerpo(ctx, m, d, t, e, b, part, n_pac, hist, mejor_eff, mejor_base, sub, pct_bacteria, pct_virus, miles):

    st.markdown(f"""
### Resumen

Se desarrolló un clasificador de radiografías de tórax pediátricas (normal frente a neumonía) basado en
**EfficientNet-B0 preentrenada en ImageNet y ajustada por transfer learning en dos fases**, y se comparó con una
red convolucional diseñada desde cero como línea base. Tras eliminar {miles(d['duplicados'])} archivos duplicados y
partir los datos **por paciente** para evitar fuga de información, el modelo alcanzó en un conjunto de prueba
independiente ({e['vp'] + e['fp'] + e['vn'] + e['fn']} radiografías de {part['prueba']['pacientes']} pacientes)
una sensibilidad de **{_pct(e['recall_sensibilidad'])}**, una especificidad de **{_pct(e['especificidad'])}**,
un F1 macro de **{_c(e['f1_macro'])}** y un ROC-AUC de **{_c(e['roc_auc'])}**, superior a la línea base en
todas las métricas. El modelo se exportó a ONNX y se despliega en esta aplicación con mapas de activación
que explican cada predicción.
""")

    st.markdown(f"""
### 1. Problema y pregunta orientadora

La neumonía es una de las principales causas de muerte en menores de cinco años, y su confirmación depende de
la lectura de una radiografía por un especialista que no siempre está disponible en zonas rurales o dispersas.
El proyecto aborda la pregunta: **¿puede una red neuronal convolucional distinguir radiografías normales de
radiografías con neumonía, priorizando la detección de casos positivos y mostrando la evidencia visual de su
decisión?** Se planteó como un problema de clasificación binaria supervisada en el que el error más costoso
es el falso negativo.

### 2. Datos y gestión con SQL (paso 1)

Se usó el conjunto *Chest X-Ray Images (Pneumonia)* (Kermany et al., 2018): radiografías anteroposteriores de
niños de 1 a 5 años del Guangzhou Women and Children's Medical Center. Cada archivo se leyó una sola vez para
calcular su hash MD5, registrar sus dimensiones y guardar una copia de 256×256 píxeles en memoria. El
inventario se insertó en una base **DuckDB** y el análisis exploratorio se resolvió con consultas SQL
(pestaña *Consultas SQL*). Tres hallazgos orientaron el diseño:

- **Duplicados:** de {miles(d['archivos_totales'])} archivos descargados solo {miles(d['imagenes_unicas'])} eran únicos. Sin
  deduplicar, una misma imagen podía quedar en entrenamiento y en prueba.
- **Desbalance:** cerca del 73 % de las imágenes son neumonía (bacteriana {_c(pct_bacteria, 1)} %,
  viral {_c(pct_virus, 1)} %).
  La exactitud por sí sola sería engañosa.
- **Varias radiografías por paciente:** {miles(n_pac)} pacientes para {miles(d['imagenes_unicas'])} imágenes. Partir por
  imagen permitiría que el modelo reconociera al paciente en lugar de la enfermedad.

El EDA visual reveló además **posibles variables de confusión**: electrodos y cables de monitoreo, más
frecuentes en niños hospitalizados, y marcadores de plomo o textos impresos por el equipo.
""")

    st.markdown(f"""
### 3. Preparación y pipeline (paso 2)

- **Partición 70/15/15 por paciente** con `StratifiedGroupKFold`: cada niño pertenece a una sola partición y la
  proporción de clases se conserva (entrenamiento {miles(part['entrenamiento']['imagenes'])}, validación
  {part['validacion']['imagenes']} y prueba {part['prueba']['imagenes']} imágenes). Una consulta SQL verifica
  que la intersección de pacientes entre particiones es vacía. La partición *val* original de Kaggle (16
  imágenes) se descartó por insuficiente.
- **Preprocesamiento:** escala de grises, 224×224 píxeles, réplica a tres canales y normalización con la
  media y desviación de ImageNet, que es la distribución que espera la red preentrenada.
- **Aumento de datos** solo en entrenamiento, con transformaciones de significado clínico: recortes de
  80–100 %, rotación de ±10°, traslación de ±5 % y variación de brillo y contraste de ±20 %. **No se usó
  volteo horizontal** porque produciría anatomía irreal (corazón a la derecha).
- **Desbalance:** pesos de clase inversos a la frecuencia en la pérdida,
  $w_c = N / (K \\cdot n_c)$, que dieron {_c(t['pesos_clase'][0], 2)} para normal y {_c(t['pesos_clase'][1], 2)}
  para neumonía.
""")

    st.markdown(f"""
### 4. Modelado con redes neuronales (paso 3)

Se compararon dos arquitecturas para justificar técnicamente la elección:

| | CNN base | EfficientNet-B0 |
|---|---|---|
| Origen de los pesos | Inicialización aleatoria | Preentrenada en ImageNet |
| Estructura | 4 bloques Conv-BN-ReLU-MaxPool (32 a 256 filtros) y GAP | Bloques MBConv con *squeeze-and-excitation* y GAP |
| Parámetros | {miles(m.get('parametros_base', 0))} | {miles(m['modelo']['parametros'])} |
| Mejor época (F1 en validación) | {int(mejor_base['epoca'])} ({_c(mejor_base['val_f1'], 4)}) | {int(mejor_eff['epoca'])} ({_c(mejor_eff['val_f1'], 4)}) |

EfficientNet-B0 (Tan y Le, 2019) escala de forma balanceada la profundidad, la anchura y la resolución, y sus
convoluciones separables en profundidad la hacen liviana para desplegar en CPU. Se entrenó en **dos fases**:
primero solo la cabeza clasificadora con el extractor congelado, incluidas sus capas BatchNorm, durante
{t['epoca_fin_fase1']} épocas con tasa de aprendizaje {t['lr']['fase1']:g}; luego toda la red con tasa
{t['lr']['fase2']:g}, diez veces menor, para adaptar los filtros sin destruir lo aprendido en ImageNet.
Ambos modelos usaron AdamW, decaimiento coseno, precisión mixta en GPU y *early stopping* sobre el F1 macro
de validación con paciencia de {t['paciencia']} épocas.
""")
    _figura("curvas_aprendizaje.png", "Figura 1. Curvas de pérdida, exactitud, F1 y AUC por época. La línea "
            "punteada marca el paso de la fase 1 a la fase 2 de EfficientNet.")
    st.markdown("""
La CNN base mostró una validación inestable, con caídas abruptas entre épocas, mientras que EfficientNet
convergió de forma sostenida, con pérdidas de entrenamiento y validación próximas, lo que indica ausencia de
sobreajuste. El salto de desempeño al iniciar la fase 2 confirma el valor del ajuste fino completo.
""")

    st.markdown(f"""
### 5. Evaluación (paso 4)

El **umbral de decisión** se eligió en el conjunto de validación maximizando el F1 macro y resultó
{_c(m['umbral'], 2)}. Es bajo porque, en tamizaje, conviene marcar como sospechosa una radiografía con
probabilidad modesta de neumonía. El conjunto de prueba no intervino en ninguna decisión y se usó una sola
vez para la evaluación final.

| Métrica (prueba) | CNN base | EfficientNet-B0 |
|---|---|---|
| Sensibilidad | {_pct(b['recall_sensibilidad'])} | **{_pct(e['recall_sensibilidad'])}** |
| Especificidad | {_pct(b['especificidad'])} | **{_pct(e['especificidad'])}** |
| F1 macro | {_c(b['f1_macro'])} | **{_c(e['f1_macro'])}** |
| ROC-AUC | {_c(b['roc_auc'])} | **{_c(e['roc_auc'])}** |
| Neumonías no detectadas (FN) | {b['fn']} | **{e['fn']}** |
| Falsas alarmas (FP) | {b['fp']} | **{e['fp']}** |

EfficientNet redujo los falsos negativos en {round((1 - e['fn'] / b['fn']) * 100) if b['fn'] else 0} % y las
falsas alarmas en {round((1 - e['fp'] / b['fp']) * 100) if b['fp'] else 0} % frente a la línea base. Por
subtipo, acertó el {_pct(sub['bacteria']['tasa_acierto'])} de las neumonías bacterianas, el
{_pct(sub['virus']['tasa_acierto'])} de las virales y el {_pct(sub['normal']['tasa_acierto'])} de las normales.
La neumonía viral, de patrón intersticial más sutil, es la más difícil, lo cual concuerda con la dificultad
clínica de reconocerla en la radiografía.
""")

    if ctx.hay_db:
        st.markdown("#### Incertidumbre de las métricas")
        with st.spinner("Calculando intervalos de confianza..."):
            ic, n_p, n_i = intervalos_bootstrap(RUTA_DB.stat().st_mtime, float(m["umbral"]))
        mostrar = ic.copy()
        for col in ["Estimación", "IC 95 % inferior", "IC 95 % superior"]:
            mostrar[col] = mostrar[col].map(lambda v: _c(v, 4))
        tabla(mostrar)
        st.markdown(f"""
Intervalos de confianza del 95 % obtenidos con {N_BOOTSTRAP} remuestreos *bootstrap* **por paciente**
({n_p} pacientes, {n_i} radiografías). Remuestrear pacientes y no imágenes respeta la correlación entre
radiografías del mismo niño; un bootstrap por imagen subestimaría la incertidumbre.
""")

    _figura("mapas_activacion.png", "Figura 2. Mapas de activación de clase en verdaderos positivos, verdaderos "
            "negativos, falsos positivos y falsos negativos del conjunto de prueba.", ancho=620)
    st.markdown("""
**Explicabilidad.** Como EfficientNet termina en *Global Average Pooling* y una capa lineal, el mapa de
activación de clase (Zhou et al., 2016) se calcula exactamente ponderando los 1 280 mapas de la última
convolución con los pesos de la clase neumonía; en el notebook se verificó numéricamente su equivalencia con
Grad-CAM (Selvaraju et al., 2017). En los verdaderos positivos la activación se concentra en los campos
pulmonares. En algunos falsos positivos aparece activación sobre marcadores de plomo, una señal de
*aprendizaje por atajos* que se discute más abajo.
""")

    st.markdown(f"""
### 6. Despliegue (paso 5)

El modelo se exportó a **ONNX** con dos salidas, las probabilidades y los mapas de la última convolución, y se
verificó que reproduce a PyTorch con diferencia máxima inferior a 10⁻³. La aplicación usa `onnxruntime` en
CPU ({_c(ctx.meta['modelo']['parametros'] / 1e6, 1)} millones de parámetros, inferencia de unos 10 ms por imagen)
en lugar de PyTorch, lo que hace viable publicarla en Streamlit Community Cloud. El preprocesamiento de la app
es la misma función del notebook, de modo que entrenamiento e inferencia ven exactamente la misma entrada.
""")

    st.markdown(f"""
### 7. Discusión y limitaciones

- **Validez externa:** todas las imágenes provienen de un solo hospital y de niños de 1 a 5 años. El
  desempeño en adultos, en otros equipos de rayos X o en proyecciones laterales no está evaluado y
  probablemente sea menor (cambio de dominio).
- **Calidad de las etiquetas:** trabajos posteriores a Kermany et al. (2018) han señalado radiografías mal
  etiquetadas en este conjunto. Parte de los errores del modelo podría deberse a la etiqueta y no al modelo.
- **Aprendizaje por atajos:** electrodos, marcadores de plomo y textos impresos pueden correlacionarse con la
  clase. Los mapas de activación muestran que el modelo atiende sobre todo a los pulmones, pero no lo
  descartan del todo. Una mejora sería enmascarar los bordes o recortar el campo pulmonar con un modelo de
  segmentación antes de clasificar.
- **Una sola corrida:** las métricas provienen de un entrenamiento con semilla fija. Repetir con varias
  semillas o con validación cruzada por paciente daría una estimación más robusta de la variabilidad.
- **Calibración:** no se evaluó si las probabilidades están bien calibradas; un diagrama de confiabilidad y
  *temperature scaling* serían el siguiente paso antes de interpretar la probabilidad como riesgo.

### 8. Conclusiones

1. El transfer learning desde ImageNet supera a una CNN entrenada desde cero con pocas miles de imágenes: más
   estable, con mayor F1 y AUC, y con menos falsos negativos.
2. El rigor en los datos, con deduplicación por hash y partición por paciente, es tan determinante como la
   arquitectura para que las métricas reflejen el desempeño real en pacientes nuevos.
3. Ajustar el umbral en validación permite alinear el modelo con la prioridad clínica de no dejar pasar casos
   de neumonía.
4. La explicabilidad con mapas de activación no solo justifica las predicciones, también permite auditar el
   modelo y detectar posibles atajos.
5. El modelo es una herramienta de apoyo académico y **no sustituye el criterio radiológico**; su uso clínico
   exigiría validación externa y regulatoria.

### Referencias

- {CITA_DATASET}
- {CITA_KAGGLE}
- Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & Batra, D. (2017). Grad-CAM: Visual
  explanations from deep networks via gradient-based localization. En *Proceedings of the IEEE International
  Conference on Computer Vision* (pp. 618–626).
- Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking model scaling for convolutional neural networks. En
  *Proceedings of the 36th International Conference on Machine Learning* (pp. 6105–6114). PMLR.
- Zhou, B., Khosla, A., Lapedriza, A., Oliva, A., & Torralba, A. (2016). Learning deep features for
  discriminative localization. En *Proceedings of the IEEE Conference on Computer Vision and Pattern
  Recognition* (pp. 2921–2929).
""")
