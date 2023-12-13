# views.py

from celery.result import AsyncResult
from flask import Blueprint, render_template, jsonify, request, current_app
from tasks import add, block, process, calculate_exp

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def index():
    file_path = 'Zeroc.html'
    return render_template(file_path, title='Home')

@main_bp.route('/<example>')
def launch(example):
    file_path = f'{example}'
    return render_template(file_path, title='Bonjour')

@tasks_bp.get("/result/<id>")
def result(id):
    result = current_app.AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }

@tasks_bp.route("/add", methods=["POST"])
def add_route():
    a = request.form.get("a", type=int)
    b = request.form.get("b", type=int)
    result = current_app.send_task("tasks.add", args=[a, b])
    return {"result_id": result.id}

@tasks_bp.route("/block", methods=["POST"])
def block_route():
    result = current_app.send_task("tasks.block")
    return {"result_id": result.id}

@tasks_bp.route("/process", methods=["POST"])
def process_route():
    total = request.form.get("total", type=int)
    result = current_app.send_task("tasks.process", kwargs={"total": total})
    return {"result_id": result.id}

@tasks_bp.route('/')
def index():
    file_path = 'Zeroc.html'
    return render_template(file_path, title='Home')

@tasks_bp.route('/<example>')
def launch(example):
    file_path = f'{example}.html'
    return render_template(file_path, title='Bonjour')

@tasks_bp.route('/get_result', methods=['GET'])
def get_result():
    result = current_app.send_task("tasks.background_task")
    return jsonify({'status': 'Task initiated. Check the Celery worker console for the result.'})

@tasks_bp.route('/calculate_exp', methods=['POST'])
def trigger_calculate_exp():
    result = calculate_exp.delay()
    return jsonify({'status': 'Task initiated. Check the Celery worker console for the result.'})
