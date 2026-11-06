"""Página «equipo». El contenido vive en vista_equipo.py; el título y el paso del ACA los dibuja app.py."""

import vista_equipo
from contexto import obtener

vista_equipo.render(obtener())
