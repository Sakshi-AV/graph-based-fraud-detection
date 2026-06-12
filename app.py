"""Development entrypoint for the Flask fraud monitoring app."""

from backend.factory import create_app


app = create_app(load_artifacts=False)


if __name__ == "__main__":
    app = create_app(load_artifacts=True)
    app.run(debug=True, use_reloader=False)
