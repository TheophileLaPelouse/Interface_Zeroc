import math
from celery import shared_task, Task
import time
import sys
from flask import current_app
import os

sys.path.append("/home/theophile/Documents/Projet G1-G2/pycode")
import main

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
    csv_traitement = '/home/theophile/Documents/Projet G1-G2/TRAITEMENT.csv'
    csv_ifc = '/home/theophile/Documents/Projet G1-G2/propriétés.csv'
    csv_meth = '/home/theophile/Documents/Projet G1-G2/construction.csv'
    print(adresse, "bonjour")
    ifc = os.listdir("/home/theophile/Documents/Projet G1-G2/site_web_zeroc/Files/non_traite")[0]
    main.run(ifc, csv_ifc, csv_traitement, csv_meth, adresse)
    return