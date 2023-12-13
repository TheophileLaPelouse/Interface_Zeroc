from flask import Flask, render_template, send_file, jsonify
from celery import Celery
from celery_init_app import celery_init_app
from tasks import tasks_bp
from views import main_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    @app.route("/")
    def index() -> str:
        return render_template("Zeroc.html")

    import views

    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    
    app.config['adresse'] = ""
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, )