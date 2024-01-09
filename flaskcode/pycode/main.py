#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:48:00 2023

@author: theophile
"""

from .data.extractifc import ifc2csv
from .data.tridonneesV2 import create_dico, json_adresse, create_adresses
from .model.colonnes import gencol, genmodel, to_json
import os
import time

# csv_traitement = 'ptitraitement.csv'
# csv_traitement = '../Files/TRAITEMENTpropre.csv'
# csv_ifc = '../Files/traite/propriétés.csv'
# csv_meth = '../Files/construction.csv'
# adresse = "Avenue Paul Langevin Villeneuve-d'Ascq"
l_cat_mat = [['Cloisonnement'], ['Cloisonnement'], ['Cloisonnement'], ['Cloisonnement']]
l_cat_iso = [['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
             ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
             ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
             ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)']]

def run(csv_traitement, csv_meth, adresse, l_cat_iso = l_cat_iso, l_cat_mat=l_cat_mat,
        path_adresse = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Files/Resultats/adresses.json'), dic_adresse_vu = None) :
    
    tic = time.time()
    print("Traitement du fichier IFC")
    try : 
        path_ifc = os.path.join('../Files/non_traite', os.listdir('../Files/non_traite')[0])
    except : 
        print("Erreur fichier non reçu")
        return(-1)
    tac = time.time()
    print("Fin du Traitement du fichier, temps de traitement = %f s" % abs(tic - tac))
    tic = tac
    csv_ifc = os.path.join('../Files/non_traite', os.path.basename(path_ifc)[:-3] + 'csv')
    ifc2csv(path_ifc, csv_ifc)
    print("Création du dictionnaire")
    
    if dic_adresse_vu is None :
        DICO, dic_adresse_vu, dico_adresse = create_dico(csv_traitement, csv_ifc, csv_meth, adresse, l_cat_mat, l_cat_iso)
    else : 
        DICO, dic_adresse_vu, dico_adresse = create_dico(csv_traitement, csv_ifc, csv_meth, adresse, l_cat_mat, l_cat_iso, dicsaved=dic_adresse_vu)
    tac = time.time()
    print("Fin de création du dictionnaire, temps de traitement = %f s" % abs(tic - tac))
    
    tic = tac
    json_adresse(dic_adresse_vu, path=path_adresse)
    Nbpat = [10, 10, 10, 10]
    print('génération des patterns')
    print('Nbpat = ', Nbpat)
    xtot, tup_valid, indicemat, ind_pat, LPIECE, matindice = gencol(DICO, Nbpat)
    tac = time.time()
    print("Fin génération de colonne, temps de traitement = %f s" % abs(tic - tac))
    
    tic = tac
    # x, K, Kbar = aupif(xtot, 10)
    x = xtot
    piece = len(DICO['surface'])
    matv = len(DICO['mat']) # Matériaux vendus
    xbool = [[[1 if x[k][p][j] > 0 else 0 for j in range(matv)] for p in range(piece)] for k in range(len(x))]
    transcription = {"mur_exte" : "pattern_m_", "sol" : "pattern_s_", "plafond" : "pattern_p_", 'mur_inte' : 'pattern_m_i_'}
    print("Création du modèle")
    prob, Obj = genmodel(DICO, x, xbool, tup_valid, Nbpat, path = '../Files/Resultats/model.lp')
    print("Résolution")
    prob.solve()
    """
    Il faudra rajouter la partie cout marginal et tout 
    """
    to_json(prob, Obj, DICO, Nbpat, LPIECE, transcription, dic_adresse_vu, path=os.path.join('../Files/Resultats/', os.path.basename(path_ifc)[:-3] + 'json'))
    tac = time.time()
    print("Sucess ! , temps de traitement = %f s" % abs(tic - tac))
    return(DICO, xtot, tup_valid, indicemat, ind_pat, LPIECE, matindice, prob, Obj, Nbpat)








