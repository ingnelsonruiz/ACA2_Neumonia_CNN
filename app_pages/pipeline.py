"""Página «pipeline». El contenido vive en vista_pipeline.py; el título y el paso del ACA los dibuja app.py."""

import vista_pipeline
from contexto import obtener

vista_pipeline.render(obtener())
