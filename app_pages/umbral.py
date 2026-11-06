"""Página «umbral». El contenido vive en vista_umbral.py; el título y el paso del ACA los dibuja app.py."""

import vista_umbral
from contexto import obtener

vista_umbral.render(obtener())
