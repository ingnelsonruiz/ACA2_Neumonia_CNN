"""Página «entrenamiento». El contenido vive en vista_entrenamiento.py; el título y el paso del ACA los dibuja app.py."""

import vista_entrenamiento
from contexto import obtener

vista_entrenamiento.render(obtener())
