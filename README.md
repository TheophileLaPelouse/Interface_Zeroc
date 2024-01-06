Pour lancer l'application flask effectuer les commandes suivantes dans un terminal :
celery -A make_celery worker --loglevel INFO

Et 
flask -A task_app run --debug
Dans un autre 

De plus redis doit avoir été lancé
