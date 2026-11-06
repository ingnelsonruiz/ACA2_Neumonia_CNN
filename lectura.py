"""Lectura asistida: convierte la salida del modelo en un informe estructurado de estilo radiológico.

Todo lo que dice el informe se deriva de dos salidas reales del modelo: la probabilidad de neumonía
y el mapa de activación (CAM). No se infiere nada que el modelo no produzca: no distingue neumonía
bacteriana de viral ni estima gravedad, y el informe lo declara.

Convención radiológica: en una proyección AP/PA el lado DERECHO del paciente aparece a la IZQUIERDA
de la imagen (por eso el marcador «R» está a la izquierda).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from PIL import Image

# Región torácica aproximada en la imagen de 224×224 (fracciones de alto y ancho)
TORAX_FILAS = (0.10, 0.90)
TORAX_COLS = (0.08, 0.92)
UMBRAL_ACTIVACION = 0.5          # activación «alta» del CAM normalizado
MARGEN_DUDOSO = 0.05             # |p − umbral| por debajo del cual el caso es indeterminado


@dataclass
class Lectura:
    resultado: str               # "NEUMONÍA", "NORMAL" o "INDETERMINADO"
    confianza: str               # "alta", "moderada", "baja"
    probabilidad: float
    umbral: float
    conclusion: str
    hallazgos: list[str] = field(default_factory=list)
    calidad: list[tuple[str, str]] = field(default_factory=list)   # (nivel, texto): ok | alerta
    sugerencia: str = ""
    localizacion: str | None = None
    extension: str | None = None
    activacion_en_torax: float | None = None


def _pct(v: float, dec: int = 1) -> str:
    return f"{v * 100:.{dec}f}".replace(".", ",") + "\u202f%"


def _region_torax(cam: np.ndarray) -> tuple[slice, slice]:
    h, w = cam.shape
    return (slice(int(TORAX_FILAS[0] * h), int(TORAX_FILAS[1] * h)),
            slice(int(TORAX_COLS[0] * w), int(TORAX_COLS[1] * w)))


def analizar_mapa(cam: np.ndarray) -> dict:
    """Describe dónde y cuánto se concentra la activación del modelo."""
    filas, cols = _region_torax(cam)
    torax = cam[filas, cols]
    total = cam.sum() + 1e-8
    en_torax = float(torax.sum() / total)

    alta = torax >= UMBRAL_ACTIVACION
    extension = float(alta.mean())
    if not alta.any():
        return {"en_torax": en_torax, "extension": 0.0, "lado": None, "zona": None}

    # Lado: masa de activación alta en cada mitad de la imagen (izquierda de la imagen = derecha del paciente)
    pesos = np.where(alta, torax, 0)
    mitad = pesos.shape[1] // 2
    izq_imagen, der_imagen = pesos[:, :mitad].sum(), pesos[:, mitad:].sum()
    frac_derecho_paciente = izq_imagen / (izq_imagen + der_imagen + 1e-8)
    if frac_derecho_paciente >= 0.65:
        lado = "hemitórax derecho"
    elif frac_derecho_paciente <= 0.35:
        lado = "hemitórax izquierdo"
    else:
        lado = "ambos hemitórax"

    # Zona vertical: centroide de la activación alta en tercios del campo pulmonar
    fila_c = float((pesos.sum(axis=1) * np.arange(pesos.shape[0])).sum() / (pesos.sum() + 1e-8)) / pesos.shape[0]
    zona = "campo superior" if fila_c < 1 / 3 else ("campo medio" if fila_c < 2 / 3 else "campo inferior y bases")
    return {"en_torax": en_torax, "extension": extension, "lado": lado, "zona": zona}


def control_calidad(img_original: Image.Image | None, es_ejemplo: bool) -> list[tuple[str, str]]:
    """Verificaciones simples de la imagen de entrada (no reemplazan un control de calidad clínico)."""
    salida = []
    if es_ejemplo:
        salida.append(("ok", "Radiografía del conjunto de prueba: el modelo nunca la vio durante el entrenamiento."))
    if img_original is None or es_ejemplo:   # los ejemplos ya vienen normalizados a 256×256 por el notebook
        return salida
    ancho, alto = img_original.size
    rgb = np.asarray(img_original.convert("RGB").resize((128, 128)), dtype=np.float32)
    saturacion = float(np.asarray(Image.fromarray(rgb.astype(np.uint8)).convert("HSV"))[..., 1].mean() / 255)
    gris = rgb.mean(axis=2)
    if saturacion > 0.12:
        salida.append(("alerta", "La imagen tiene color: no parece una radiografía. El resultado no es válido."))
    if min(ancho, alto) < 300:
        salida.append(("alerta", f"Resolución baja ({ancho}×{alto} px): pueden perderse detalles finos."))
    relacion = ancho / alto
    if not 0.6 <= relacion <= 1.7:
        salida.append(("alerta", "Proporción inusual para una radiografía de tórax AP: verifique el recorte."))
    if gris.std() < 25:
        salida.append(("alerta", "Contraste bajo: la imagen puede estar sobre o subexpuesta."))
    if not es_ejemplo and len(salida) == 0:
        salida.append(("ok", "Imagen en escala de grises con resolución y contraste adecuados."))
    return salida


def generar_lectura(prob: float, umbral: float, cam: np.ndarray, img_original: Image.Image | None = None,
                    es_ejemplo: bool = False) -> Lectura:
    mapa = analizar_mapa(cam)
    calidad = control_calidad(img_original, es_ejemplo)
    margen = prob - umbral

    if abs(margen) < MARGEN_DUDOSO:
        resultado, confianza = "INDETERMINADO", "baja"
    elif margen > 0:
        resultado = "NEUMONÍA"
        confianza = "alta" if prob >= 0.90 else ("moderada" if prob >= 0.50 else "baja")
    else:
        resultado = "NORMAL"
        confianza = "alta" if prob < 0.02 else "moderada"

    lectura = Lectura(resultado=resultado, confianza=confianza, probabilidad=prob, umbral=umbral,
                      conclusion="", calidad=calidad, activacion_en_torax=mapa["en_torax"])

    if resultado == "NEUMONÍA":
        if mapa["lado"]:
            lectura.localizacion = f"{mapa['lado'].capitalize()}, {mapa['zona']}"
        ext = mapa["extension"]
        lectura.extension = ("focal" if ext < 0.12 else "extensa" if ext > 0.30 else "moderada") + \
            f" ({_pct(ext, 0)} del campo torácico con activación alta)"
        lectura.hallazgos = [
            f"El modelo asigna una probabilidad de neumonía de {_pct(prob)}, por encima del umbral operativo "
            f"de {_pct(umbral, 0)}.",
            (f"La evidencia que impulsa la predicción se localiza en {lectura.localizacion.lower()}, "
             f"con una distribución {lectura.extension}.") if lectura.localizacion else
            "La activación es difusa y no se concentra en una región definida.",
            "El modelo no diferencia etiología bacteriana o viral ni estima la gravedad.",
        ]
        lectura.conclusion = {
            "alta": "Hallazgos compatibles con neumonía, con alta confianza del modelo.",
            "moderada": "Hallazgos sugestivos de neumonía, con confianza moderada del modelo.",
            "baja": "Posible neumonía con evidencia débil: el modelo apenas supera el umbral.",
        }[confianza]
        lectura.sugerencia = (
            "Priorizar la lectura por radiología y correlacionar con la evaluación clínica (fiebre, frecuencia "
            "respiratoria, signos de dificultad respiratoria y saturación de oxígeno)."
            if confianza == "alta" else
            "Incluir en la lista de lectura prioritaria por radiología; la decisión depende de la correlación clínica."
        )
    elif resultado == "NORMAL":
        lectura.hallazgos = [
            f"El modelo asigna una probabilidad de neumonía de {_pct(prob)}, por debajo del umbral operativo "
            f"de {_pct(umbral, 0)}.",
            "No se identifican regiones que el modelo asocie con neumonía.",
        ]
        lectura.conclusion = ("Sin hallazgos que el modelo asocie con neumonía."
                              if confianza == "alta" else
                              "Probablemente normal, aunque con alguna evidencia débil a favor de neumonía.")
        lectura.sugerencia = ("Un resultado negativo no descarta la enfermedad. Si existe sospecha clínica, "
                              "la lectura por radiología y el criterio médico prevalecen.")
    else:
        lectura.hallazgos = [
            f"La probabilidad de neumonía ({_pct(prob)}) está muy cerca del umbral operativo ({_pct(umbral, 0)}).",
            "El modelo no tiene evidencia suficiente para clasificar el caso con seguridad.",
        ]
        lectura.conclusion = "Resultado indeterminado."
        lectura.sugerencia = "Remitir a lectura por radiología: el apoyo automatizado no es concluyente en este caso."

    # Control del propio mapa: ¿la evidencia está dentro del tórax?
    if resultado != "NORMAL" and mapa["en_torax"] < 0.6:
        lectura.calidad.append(("alerta", f"Solo el {_pct(mapa['en_torax'], 0)} de la activación cae dentro del "
                                "tórax: el modelo podría estar usando marcadores, electrodos o bordes. "
                                "Interprete con cautela."))
    elif resultado != "NORMAL":
        lectura.calidad.append(("ok", f"El {_pct(mapa['en_torax'], 0)} de la activación cae dentro del campo torácico."))
    return lectura


def texto_plano(lectura: Lectura, nombre_imagen: str) -> str:
    """Versión descargable del informe."""
    lineas = [
        "LECTURA ASISTIDA POR INTELIGENCIA ARTIFICIAL (PROTOTIPO ACADÉMICO)",
        "=" * 66,
        f"Estudio:        Radiografía de tórax AP ({nombre_imagen})",
        "Modelo:         EfficientNet-B0 con transfer learning",
        f"Resultado:      {lectura.resultado}",
        f"Probabilidad:   {_pct(lectura.probabilidad)} (umbral {_pct(lectura.umbral, 0)})",
        f"Confianza:      {lectura.confianza}",
    ]
    if lectura.localizacion:
        lineas.append(f"Localización:   {lectura.localizacion}")
    if lectura.extension:
        lineas.append(f"Extensión:      {lectura.extension}")
    lineas += ["", "HALLAZGOS"] + [f"- {h}" for h in lectura.hallazgos]
    lineas += ["", "CONCLUSIÓN", lectura.conclusion, "", "SUGERENCIA", lectura.sugerencia, "", "CONTROL DE CALIDAD"]
    lineas += [f"- [{'OK' if n == 'ok' else 'ALERTA'}] {t}" for n, t in lectura.calidad]
    lineas += ["", "Este informe lo genera un prototipo académico entrenado con radiografías pediátricas de un único",
               "hospital. No es un dispositivo médico ni sustituye la lectura de un radiólogo."]
    return "\n".join(lineas)
