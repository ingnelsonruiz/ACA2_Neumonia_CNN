"""Registro de páginas: título, icono, paso del ACA, criterio de la rúbrica y descripción.

app.py construye la navegación con este registro y la portada lo usa para el recorrido del proyecto.
Para agregar una página: crear app_pages/mi_pagina.py y añadir una entrada aquí.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pagina:
    archivo: str        # ruta dentro de app_pages/
    titulo: str
    icono: str          # Material Symbols
    paso: str           # paso del ACA al que pertenece
    criterio: str       # criterio de la rúbrica que evidencia
    descripcion: str    # una o dos frases: qué muestra y qué se puede hacer

    @property
    def ruta(self) -> str:
        return f"app_pages/{self.archivo}"


INICIO = Pagina("inicio.py", "Inicio", ":material/radiology:", "Paso 5", "Despliegue, 15 %",
                "Portada con los resultados del modelo y la herramienta para probarlo con una radiografía.")

# Secciones en el orden metodológico del ACA
SECCIONES: dict[str, list[Pagina]] = {
    "Proyecto": [
        Pagina("informe.py", "Informe del proceso", ":material/article:", "Documento completo", "Todos los criterios",
               "El proyecto de punta a punta: decisiones, resultados con intervalos de confianza, "
               "limitaciones y referencias."),
        Pagina("historia.py", "La historia", ":material/auto_stories:", "Contexto", "Pregunta orientadora",
               "El problema clínico, la pregunta orientadora y el flujo de cinco pasos."),
    ],
    "Datos": [
        Pagina("dataset.py", "El dataset", ":material/dataset:", "Paso 1", "Calidad de datos, 20 %",
               "Origen de las radiografías, duplicados eliminados, desbalance y partición por paciente."),
        Pagina("sql.py", "Consultas SQL", ":material/database:", "Paso 1", "Calidad de datos, 20 %",
               "La base DuckDB del proyecto: consultas en vivo de solo lectura sobre imágenes, particiones y errores."),
        Pagina("pipeline.py", "Pipeline", ":material/tune:", "Paso 2", "Preprocesamiento, 20 %",
               "Preprocesamiento y laboratorio: altere una radiografía y vea si el modelo cambia de opinión."),
    ],
    "Modelo": [
        Pagina("arquitectura.py", "Arquitectura", ":material/account_tree:", "Paso 3", "Arquitectura neuronal, 20 %",
               "CNN desde cero frente a EfficientNet-B0, transfer learning en dos fases y mapas de activación."),
        Pagina("entrenamiento.py", "Entrenamiento", ":material/model_training:", "Paso 3",
               "Arquitectura neuronal, 20 %", "Curvas de pérdida, exactitud, F1 y AUC por época, y la época elegida."),
    ],
    "Evaluación": [
        Pagina("metricas.py", "Métricas", ":material/monitoring:", "Paso 4", "Métricas de evaluación, 15 %",
               "Resultados en prueba: matriz de confusión, curva ROC, comparación de modelos y subtipos."),
        Pagina("umbral.py", "Umbral clínico", ":material/stacked_line_chart:", "Paso 4",
               "Métricas de evaluación, 15 %", "Cómo cambian sensibilidad y especificidad al mover el punto de corte."),
    ],
    "Entregables": [
        Pagina("poster.py", "Póster", ":material/image:", "Entregable", "Póster tipo infografía, 15 %",
               "La infografía del proyecto para la sustentación, con descarga en alta calidad."),
        Pagina("equipo.py", "Equipo", ":material/group:", "Créditos", "Póster y video",
               "Integrantes, alcance y tecnologías del proyecto."),
        Pagina("documentacion.py", "Documentación", ":material/menu_book:", "Manual", "Reproducibilidad",
               "Manual de uso descargable y glosario de cada indicador."),
    ],
}

TODAS = [INICIO] + [p for grupo in SECCIONES.values() for p in grupo]
POR_TITULO = {p.titulo: p for p in TODAS}
