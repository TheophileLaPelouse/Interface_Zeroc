import time
from celery import shared_task, Task
from celery.result import AsyncResult
from flask import Blueprint, render_template, jsonify, request, current_app, redirect, send_from_directory
from .ex import calculate_exp, run_main 
import os

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.get("/result/<id>")
def result(id):
    result = AsyncResult(id)
    ready = result.ready()
    return {
        "ready": ready,
        "successful": result.successful() if ready else None,
        "value": result.get() if ready else result.result,
    }

# @tasks_bp.route("/add", methods=["POST"])
# def add():
#     a = request.form.get("a", type=int)
#     b = request.form.get("b", type=int)
#     result = current_app.send_task("tasks.add", args=[a, b])
#     return {"result_id": result.id}

# @tasks_bp.route("/block", methods=["POST"])
# def block():
#     result = current_app.send_task("tasks.block")
#     return {"result_id": result.id}

# @tasks_bp.route("/process", methods=["POST"])
# def process():
#     total = request.form.get("total", type=int)
#     result = current_app.send_task("tasks.process", kwargs={"total": total})
#     return {"result_id": result.id}

@tasks_bp.route('/')
def index():
    file_path = 'Zeroc.html'
    return render_template(file_path, title='Home')

@tasks_bp.route('/<example>')
def launch(example):
    file_path = f'{example}.html'
    return render_template(file_path, title='Bonjour')

# @tasks_bp.route('/get_result', methods=['GET'])
# def get_result():
#     result = current_app.send_task("tasks.background_task")
#     return jsonify({'status': 'Task initiated. Check the Celery worker console for the result.'})

@tasks_bp.route('/calculate_exp_result', methods=['POST'])
def calculate_exp_result():
    result = calculate_exp.delay()
    return render_template('simu.html', result_id=result.id)

@tasks_bp.route('/upload', methods=['POST'])
def upload() :
    file = request.files['ifcfile']
    if file.filename != "" :
        path = "/home/theophile/Documents/Projet G1-G2/site_web_zeroc/Files/non_traite"
        print(os.path.join(path, os.path.basename(file.filename)))
        file.save(os.path.join(path, os.path.basename(file.filename)))
    return redirect('../simu.html')

@tasks_bp.route('/get_adresse', methods=['POST'])
def get_adresse() :
    zip_code = request.form.get("zipc", type=str)
    current_app.config['adresse'] = zip_code
    print(current_app.config['adresse'])
    return redirect('../etape2.html')

@tasks_bp.route('/run_calc', methods=['POST'])
def run() :
    print(current_app.config['adresse'])
    result=run_main.delay(current_app.config['adresse'])
    return render_template('derniereEtape.html')

@tasks_bp.route('/download/<filename>', methods=['GET'])
def download(filename) :
    send_from_directory("/home/theophile/Documents/Projet G1-G2/site_web_zeroc/Files/resultats", filename)
    return render_template('derniereEtape.html')