"""Página «sql». El contenido vive en vista_sql.py; el título y el paso del ACA los dibuja app.py."""

import vista_sql
from contexto import obtener

vista_sql.render(obtener())
