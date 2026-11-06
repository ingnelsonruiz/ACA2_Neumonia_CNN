"""Página «poster». El contenido vive en vista_poster.py; el título y el paso del ACA los dibuja app.py."""

import vista_poster
from contexto import obtener

vista_poster.render(obtener())
