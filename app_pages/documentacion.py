"""Página «documentacion». El contenido vive en vista_documentacion.py; el título y el paso del ACA los dibuja app.py."""

import vista_documentacion
from contexto import obtener

vista_documentacion.render(obtener())
