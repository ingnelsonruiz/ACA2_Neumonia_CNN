"""Página «arquitectura». El contenido vive en vista_arquitectura.py; el título y el paso del ACA los dibuja app.py."""

import vista_arquitectura
from contexto import obtener

vista_arquitectura.render(obtener())
