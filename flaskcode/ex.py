import math
from celery import shared_task, Task
import time
import sys
from flask import current_app
import os

#sys.path.append("/home/theophile/Documents/Projet G1-G2/pycode")
from .pycode.main import run, l_cat_iso, l_cat_mat

@shared_task(bind = True, ignore_result=False)
def calculate_exp(self: Task):
    for i in range(5):
        self.update_state(state="work in progress", meta={"current" : math.exp(i)})
        time.sleep(1)
        print(math.exp(i))
    return {"current" : math.exp(4), "final" : math.exp(4)}
        # print(f"exp({i}) = {result}")

@shared_task(bind = True, ingore_result=False)
def run_main(self: Task, adresse) :
    print("couquecemarcepas?")
    csv_traitement = 'files/TRAITEMENTpropre.csv'
    csv_meth = 'files/construction.csv'
    print(adresse, "bonjour")
    run(csv_traitement, csv_meth, adresse)
    return
