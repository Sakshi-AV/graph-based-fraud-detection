"""WSGI entrypoint for production WSGI servers.

This file does not change any UI/ML logic. It only exposes the existing Flask
app instance for servers like gunicorn/uwsgi.
"""

import importlib.util
from pathlib import Path

# Load the top-level app.py explicitly to avoid name collision with the /app package.
app_path = Path(__file__).resolve().parent / 'app.py'
spec = importlib.util.spec_from_file_location('fraud_flask_app', app_path)
app_module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
assert spec and spec.loader
spec.loader.exec_module(app_module)

application = getattr(app_module, 'app')




