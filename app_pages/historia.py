"""Página «historia». El contenido vive en vista_historia.py; el título y el paso del ACA los dibuja app.py."""

import vista_historia
from contexto import obtener

vista_historia.render(obtener())
