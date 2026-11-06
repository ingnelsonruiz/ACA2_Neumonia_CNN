"""Página «dataset». El contenido vive en vista_dataset.py; el título y el paso del ACA los dibuja app.py."""

import vista_dataset
from contexto import obtener

vista_dataset.render(obtener())
