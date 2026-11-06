"""Página «metricas». El contenido vive en vista_metricas.py; el título y el paso del ACA los dibuja app.py."""

import vista_metricas
from contexto import obtener

vista_metricas.render(obtener())
