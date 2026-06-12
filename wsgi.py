"""WSGI entrypoint for production WSGI servers."""

from backend.factory import create_app


application = create_app(load_artifacts=True)

