# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:38:09 2023

@author: natha
"""

from urllib import response
import requests 
from pprint import pprint
import csv
import json


# #adresse de l'utilisateur
# adresse = "Avenue Paul Langevin Villeneuve-d'Ascq"


# #Lien pour transformer les adresses classiques en position GPS  search?format=json
# BASE_URL = 'https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q='

# #adresse = input("Entrez votre adresse (n° rue nomderue nomdeville): ")

# fin_url = '&format=json&limit=1'

# demande1 = BASE_URL + adresse + fin_url
# response1 = requests.get(f"{demande1}")
# data1 = response1.json()

# #Lien pour obtenir une distance entre 2 points par voie routière 
# lien = 'https://router.project-osrm.org/route/v1/driving/'

# #Position de départ en string
# longDepart = data1[0]['lon']
# latDepart = data1[0]['lat']


#Positions d'arrivée que tu récupére depuis un csv  [logitude,latitude]
#pos = []

#ouverture du fichier csv des coordonnées
# fichier = open('coord.csv', encoding='utf-8-sig')
# lecture = csv.reader(fichier, delimiter=';')


#Création de la liste des coordonnées et sauvegarde du fichier csv en liste de listes

#  #nombre de coordonnées





#initialisation de la liste des distances
#res = []


#récupération de la distance par rapport à chaque lieu du fichier csv
# for i in range (0,n):
#     demande2 = lien + longDepart + ',' + latDepart + ';' + pos[i][0] + ',' + pos[i][1]             #création du lien à interroger
#     response2 = requests.get(f"{demande2}")                                                         #requête du lien
#     data2 = response2.json()                                                                        #récupération de la réponse json du lien
#     res.append(data2['routes'][0]['legs'][0]['distance'])
# #['routes'][0]['legs'][0]['distance']    

# print("Distances (en m) : ")

# print(res)

#ajout des distances dans le fichier csv (colonne de distances)
# for i in range(0,rowf):
#     pos[i][2] = str(res[i])
    

#réécriture du fichier csv avec la liste file en rajoutant les distances

#print(file)

# f = open('coord.csv', 'w', newline='')
# ec = csv.writer(f, delimiter=';')

# ec.writerows(pos)
        
    
# f.close()



def distance(place, adresse):
    
    #adresse de l'utilisateur


    #Lien pour transformer les adresses classiques en position GPS  search?format=json
    BASE_URL = 'https://nominatim.openstreetmap.org/?format=json&addressdetails=1&q='

    #adresse = input("Entrez votre adresse (n° rue nomderue nomdeville): ")

    fin_url = '&format=json&limit=1'

    demande1 = BASE_URL + adresse + fin_url
    response1 = requests.get(f"{demande1}")
    data1 = response1.json()

    #Lien pour obtenir une distance entre 2 points par voie routière 
    lien = 'https://router.project-osrm.org/route/v1/driving/'

    #Position de départ en string
    longDepart = data1[0]['lon']
    latDepart = data1[0]['lat']
    
    demande3 = BASE_URL + place + fin_url
    response3 = requests.get(f"{demande3}")
    data3 = response3.json()
    if data3 != []: 
        longDepart3 = data3[0]['lon']
        latDepart3 = data3[0]['lat']

        demande4 = lien + longDepart + ',' + latDepart  + ';' + longDepart3 + ',' + latDepart3
        response4 = requests.get(f"{demande4}")
        data4 = response4.json()['routes'][0]['legs'][0]['distance']
        return(data4)
    
    else:
        return None

#print(distance("AVIGNON - France"))
