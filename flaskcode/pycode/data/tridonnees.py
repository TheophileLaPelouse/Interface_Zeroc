# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 16:03:31 2023

@author: natha
"""

import csv
import re
import data.Programme_des_distances as dist
from urllib import response
import requests 
from pprint import pprint
import json
#strip() retire les espaces à gauche et à droite
#re pour prendre en compte les caractères spéciaux, re.match

# csv_traitement = 'ptitraitement.csv'
# csv_traitement = 'TRAITEMENT.csv'
# csv_ifc = 'propriétés.csv'
# csv_meth = 'construction.csv'
# adresse = "Avenue Paul Langevin Villeneuve-d'Ascq"

# # cmis, cmiis, cmes, cmeis, cps, cpis, css, csis = ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation']
# cmis, cmiis, cmes, cmeis, cps, cpis, css, csis = ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre']
def create_dico(csv_traitement, csv_ifc, csv_meth, adresse, 
                cmis=['Laine de verre'], cmiis=['Laine de verre'], 
                cmes=['Laine de verre'], cmeis=['Laine de verre'], 
                cps=['Laine de verre'], cpis=['Laine de verre'], 
                css=['Laine de verre'], csis=['Laine de verre']) :
    DICO = {}
    DICO['type'] = {}
    DICO['mat'] = []
    DICO['mat_name'] = []
    DICO['mat_energie'] = {}
    DICO["dens_mat"] = []
    DICO['surface'] = []
    DICO['Emat'] = []
    DICO['Emet'] = []
    DICO["dens_mat"] = []
    DICO['dist_prod'] = [[]]
    DICO['indicemat'] = {}
    
    LMAT = {'mur_inte': [cmis, cmiis], 
            'mur_exte' : [cmes, cmeis], 
            'Plafonds': [cps, cpis], 
            'Sols': [css, csis]
            }
    
    f_traitement = open(csv_traitement, 'r', errors= 'ignore')
    
    ligne = csv.reader(f_traitement, delimiter = ';')
    
    res = []
    
    dico_repertoire = {} #utilisation les tableaux des matériaux associés aux isolations par exemple
    dico_eqco2 = {}     #classe les matériaux avec leur equivalent CO2
    dico_adresse = {}   #classe l'adresse associé pour chaque matériaux et en plus renvoyer la distance directement on se trouve à centrle
    dico_conduct = {}   #donne la conductivité thermique de chaque matériaux 
    dico_rho = {} #Faudra que ce soit la liste des densités
    
    list_materiau = []
    list_repertoire = []    #liste des utilisation répertoire ex : isolation
    list_eqco2 = []
    list_adresse = []
    list_conductivite = []
    list_rho = []
    rep2 = []   #permet de savoir avec le multiple de 3 quel materiau pour quel type de placement +3
    
    c = 0
    for l in ligne:
        c += 1
        if l[11]!='NOM DU PRODUIT':
            repertoire1 = l[12]
            if l[12]!="":
                repertoire2 = repertoire1.strip()[2:].replace("Ã©", "é").replace("Ã¨", "è").replace("Ã¢", "â")   #suppression des caractères en trop et des espaces
                rep2.append(repertoire2)
                
            if repertoire2 not in list_repertoire and l[12]!="" and repertoire2!='oduits de construction':
                list_repertoire.append(repertoire2)
                
            if l[11]!="":
                list_materiau.append(l[11])
                list_eqco2.append(l[15])
                list_adresse.append(l[17])
                list_conductivite.append(l[43])
                list_rho.append(1) # Faudra faire des vrais coefficient en fait, une petite fonction fera l'affaire
            
    
    nb_mat = len(list_materiau)
    nb_methode = len(list_repertoire)
    dic_adresse_vu = {} # Chaque adresse existante et sa distance
    for i in range (0,nb_methode):
        print(i, nb_methode)
        r = list_repertoire[i].replace("Ã©", "é").replace("Ã¨", "è").replace("Ã¢", "â")
        # print(r)
        dico_repertoire[r] = []
        dico_adresse[r] = []
        dico_eqco2[r] = []
        dico_conduct[r] = []
        dico_rho[r] = []
        for j in range (0, nb_mat):
            if rep2[j+1] == list_repertoire[i] or rep2[j+2] == list_repertoire[i] or rep2[j+3] == list_repertoire[i]:
                dico_repertoire[r].append(list_materiau[j].replace("Ã©", "é").replace("Ã¨", "è").replace("Ã¢", "â"))
                if list_adresse[j] != "" :
                    if list_adresse[j] in dic_adresse_vu :
                        dico_adresse[r].append([list_adresse[j], dic_adresse_vu[list_adresse[j]]])
                    else : 
                        dic_adresse_vu[list_adresse[j]] = dist.distance(list_adresse[j], adresse)
                        dico_adresse[r].append([list_adresse[i], dic_adresse_vu[list_adresse[j]]])
                else : 
                    dico_adresse[r].append([None,0])
                try :
                    dico_eqco2[r].append(float(list_eqco2[j].replace(',', '.')))
                except :
                    dico_eqco2[r].append(-1)
                try :
                    dico_conduct[r].append(float(list_conductivite[j].replace(',', '.')))
                    dico_rho[r].append(float(list_rho[j]))
                except : 
                    # print(list_conductivite[j])
                    dico_conduct[r].append(2)
                    dico_rho[r].append(-1)
                    
        # if list_adresse[i] != "":
        #     dico_adresse[r] = [list_adresse[i],dist.distance(list_adresse[i][6:])]
        # else:
        #     dico_adresse[r] = [None,None]
            
        
    f_traitement.close()
    
    
    #11 12 15 17 44
        
    list_id = []                            #liste des identifiants des objets
    list_volume = []                        #liste des volumes de chaque objet
    list_surface = []                       #liste des surfaces de chaque objet 
    dico_type = {'mur_inte': [], 'mur_exte' : [], 'Plafonds': [], 'Sols': []}
    
    
                 
    #print(dico_adresse)
        
    f_prop = open(csv_ifc, 'r', encoding='latin-1')
    line = csv.reader(f_prop, delimiter = ';')
    
    
    for l in line:
        # print(l)
        if l[0]!='Catégorie':
            list_id.append(l[1])
            list_volume.append(l[3])
            list_surface.append(l[2])
            if l[4]=='Extérieur' and l[0]=='Murs':
                dico_type['mur_exte'].append(l[1])
            elif l[0] == 'Murs':
                dico_type['mur_inte'].append(l[1])
            elif l[0]=='Plafonds':
                dico_type['Plafonds'].append(l[1])
            elif l[0]=='Sols':
                dico_type['Sols'].append(l[1])
            
    f_prop.close()
    
    dico_id = dict(zip(list_id, list(zip(list_volume, list_surface))))
    c = 0
    for ids in dico_id :
        if c !=0 :
            dico_id[ids] = (float(dico_id[ids][0])/float(dico_id[ids][1]), float(dico_id[ids][1]))
        c += 1
        
    for typ in dico_type: 
        n = len(dico_type[typ])
        th_utile = (typ == 'mur_exte')
        c_mat, c_iso = LMAT[typ]
        lmat, liso = [], []
        for mat in c_mat :
            try: 
                lmat.append(mat)
                DICO['mat_name'].append(mat)
                DICO['mat_energie'][mat] = [dico_rho[mat][0], dico_eqco2[mat][0]]
                DICO["dens_mat"].append(dico_rho[mat][0])
                DICO['mat'].append(dico_conduct[mat][0])
                DICO['Emat'].append(dico_eqco2[mat][0])
            except : pass
        for iso in c_iso :
            try : 
                liso.append(iso)
                DICO['mat_name'].append(iso)
                DICO['mat_energie'][iso] = [dico_rho[iso][0], dico_eqco2[iso][0]]
                DICO["dens_mat"].append(dico_rho[iso][0])
                DICO['mat'].append(dico_conduct[iso][0])
                DICO['Emat'].append(dico_eqco2[iso][0])
            except : pass
        DICO['type'][typ] = [lmat, liso]
        for k in range(n) :
            emax, S = dico_id[dico_type[typ][k]]
            DICO['surface'].append(S)
            dico_type[typ][k] = [dico_type[typ][k], emax, S, th_utile, [], []] # de la forme de d[pièce] dans colonne
            
    DICO['piece'] = dico_type
    
    f_construct = open(csv_meth, 'r', encoding='latin-1')
    line = csv.reader(f_construct, delimiter = ';')
    
    list_materiau = []
    dico_partie = {}    #
    dico_methode = {}
    dico_heure = {}
    dico_unite = {}
    dico_materiau = {}
    list_coef = []
    l_meth = []
    
    #0 1 4 5 6  on vérifie le match de 6 avec le titre de repertoire de la base inies
    for repertoire in list_repertoire:
        dico_materiau[repertoire] = []
    for l in line:
        for repertoire in list_repertoire:
            if repertoire.lower() in l[6].lower():
                list_materiau.append(l[6])
                dico_materiau[repertoire].append(l[6])
                dico_unite[l[6]] = l[5]
                try :
                    dico_heure[l[6]] = float(l[4].replace(',', '.'))
                except :
                    dico_heure[l[6]] = -1
                dico_methode[l[6]] = l[1]
                dico_partie[l[6]] = l[0]
                list_coef.append(1) # Faudra mettre ça de manière propre
                DICO['Emet'].append(dico_heure[l[6]])
                l_meth.append(l[6])
                
    f_construct.close()
    
    n_meth = len(DICO['Emet'])
    n_mat = len(DICO['mat'])
    n_adr = len(dic_adresse_vu)
    DICO['dist_prod'] = [[0 for k in range(n_mat)] for j in range(n_adr)]
    k = 0
    for cond in DICO['mat'] :
        j = 0
        for adr in dic_adresse_vu :
            if [adr, dic_adresse_vu[adr]] in dico_adresse[DICO['mat_name'][k]] : 
                # print(adr, dico_adresse[DICO['mat_name'][cond]])
                DICO['dist_prod'][j][k] = dic_adresse_vu[adr]
            j += 1 
        k += 1 
        
    DICO['meth_mat'] = [[0 for k in range(n_meth)] for j in range(n_mat)]
    j = 0
    for cond in DICO['mat'] :
        for k in range(n_meth) :
            try :
                if l_meth[k] in dico_materiau[DICO['mat_name'][j]] :
                    DICO['meth_mat'][j][k] = 1 
            except : 
                pass
        j += 1
    
    c = 0 
    for mat in DICO['mat_name'] :
        DICO['indicemat'][mat] = c
        c += 1 
    
    DICO['c_depl'] = 1 # A vérifier
    DICO['dist_dech'] = []
    return(DICO, dic_adresse_vu, dico_adresse)

                
# DICO, dic_adresse_vu, dico_adresse = create_dico(csv_traitement, csv_ifc, csv_meth, adresse)
# DICO['dist_dech'] = []

def json_adresse(dic_adr, path = "/home/theophile/Documents/Projet G1-G2/adresses.json") :
    l = []
    for adr in dic_adr :
        l.append(adr)
    with open(path, "w") as fp : 
        json.dump(l, fp)
    return