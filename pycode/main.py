#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:48:00 2023

@author: theophile
"""

from data.extractifc import ifc2csv
from data.tridonnees import create_dico, json_adresse
from model.colonnes import gencol, genmodel, to_json
import os

# csv_traitement = 'ptitraitement.csv'
csv_traitement = '../Files/TRAITEMENT.csv'
csv_ifc = '../Files/traite/propriétés.csv'
csv_meth = '../Files/construction.csv'
adresse = "Avenue Paul Langevin Villeneuve-d'Ascq"
def run(csv_ifc, csv_traitement, csv_meth, adresse, path_adresse = "/home/theophile/Documents/Projet G1-G2/adresses.json", **kwargs) :
    try : 
        path_ifc = os.listdir('../Files/non_traite')[0]
    except : 
        print("Erreur fichier non reçu")
        return(-1)
    # ifc2csv(path_ifc, csv_ifc)
    print("Création du dictionnaire")
    DICO, dic_adresse_vu, dico_adresse = create_dico(csv_traitement, csv_ifc, csv_meth, adresse)
    print("Fin de création du dictionnaire")
    json_adresse(dic_adresse_vu, path=path_adresse)
    Nbpat = [10, 10, 10, 10]
    xtot, tup_valid, indicemat, ind_pat, LPIECE, matindice = gencol(DICO, Nbpat)
    # x, K, Kbar = aupif(xtot, 10)
    x = xtot
    piece = len(DICO['surface'])
    matv = len(DICO['mat']) # Matériaux vendus
    xbool = [[[1 if x[k][p][j] > 0 else 0 for j in range(matv)] for p in range(piece)] for k in range(len(x))]
    transcription = {"mur_exte" : "pattern_m_", "sol" : "pattern_s_", "plafond" : "pattern_p_", 'mur_inte' : 'pattern_m_i_'}
    prob, Obj = genmodel(DICO, x, xbool, tup_valid, Nbpat, path = '/home/theophile/Documents/Projet G1-G2/model.lp')
    prob.solve()
    """
    Il faudra rajouter la partie cout marginal et tout 
    """
    to_json(prob, Obj, DICO, Nbpat, LPIECE, transcription)
    print("Sucess !")
    return(1)