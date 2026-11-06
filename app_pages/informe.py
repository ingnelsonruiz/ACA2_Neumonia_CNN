"""Página «informe». El contenido vive en vista_informe.py; el título y el paso del ACA los dibuja app.py."""

import vista_informe
from contexto import obtener

vista_informe.render(obtener())
