#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 12:27:13 2023

@author: theophilemounier
"""

"""
On va revoir le code tridonnees en faisant une classe arborescence qui sera giga pratique
"""

import pandas as pd
import re 
import data.Programme_des_distances as dist
import csv
import os
#from extractifc import ifc2csv
import json
import numpy as np

def arborescence(csv_traitement) :
    df = pd.read_csv(csv_traitement, encoding='utf-8', sep=';')
    arbre= {}
    n = len(df.index)
    k = 0
    while k < n :
        name = df['NOM DU PRODUIT'][k]
        if not pd.isnull(name) :
            rep = df['REPERTOIRE'][k]
            if rep not in arbre : 
                arbre[rep] = {}
            arbrisseau = arbre[rep]
            j = k + 1
            while j < n and pd.isnull(df['NOM DU PRODUIT'][j]) and (j-k) < 5:
                rep = df['REPERTOIRE'][j]
                if not pd.isnull(rep) :
                    rep = rep.strip()
                    rep = rep.replace('â–º ', '')
                    if rep not in arbrisseau : 
                        arbrisseau[rep] = {}
                    arbrisseau = arbrisseau[rep]
                j += 1
            arbrisseau[name] = {}
            info = ['ADRESSE PRODUCTEUR', 'QUANTITE', 'CONDUCTIVITE', 'BILAN', 'ORGANISME DECLARANT', 'EQ CO2']
            for i in info :
                try : 
                    arbrisseau[name][i] = float(df[i][k].replace(',', '.'))
                except :
                    arbrisseau[name][i] = df[i][k]
            k = j
        else : 
            k += 1
    return(arbre)

class navigate :
    # Faut faire un truc qui permet de travailler facilement avec les chemins histoires que ce soit propre
    def __init__(self, csv_traitement):
        self.arbre = arborescence(csv_traitement)
        self.l_adresse = []
        Path_adr = self.parcourir('ADRESSE PRODUCTEUR')
        for path in Path_adr : 
            adr = self.get(path + '//' + 'ADRESSE PRODUCTEUR')
            if adr not in self.l_adresse : 
                self.l_adresse.append(adr)
    
    def parcourir(self, name, path='', symb = '') :
        
        if symb != '' : 
            Path = []
            def fun(arbre, abs_path) :
                
                if isinstance(arbre, dict) :
                    for key in arbre.keys() : 
                        if re.search(symb, key) is not None:
                            Path.append(abs_path)
                        else : 
                            fun(arbre[key], abs_path + '//' + key)
                else : 
                    # print('bonjour', arbre, symb)
                    if not pd.isnull(arbre) and re.search(symb, arbre) is not None :
                        Path.append(abs_path)
                return   
            fun(self.get(path), path)
            
        if isinstance(name, int) :
            Path = []
            def fun(arbre, abs_path, i) :
                if i < name :
                    for key in arbre.keys() : 
                        fun(arbre[key], abs_path + '//' + key, i + 1)
                else : 
                    Path.append(abs_path)
                return       
            fun(self.arbre, '', 0)
        if isinstance(name, str) :
            Path = []
            def fun(arbre, abs_path) :
                
                if isinstance(arbre, dict) :
                    for key in arbre.keys() : 
                        if key == name :
                            Path.append(abs_path)
                        else : 
                            fun(arbre[key], abs_path + '//' + key)
                else : 
                    if arbre == name :
                        Path.append(abs_path)
                return   
            
            fun(self.get(path), path)
        return(Path)
            
    def get(self, path) :
        lkey = path.split('//')
        lkey.pop(0)
        def fun(arbre, lkey) :
            if lkey == [] :
                return arbre
            else :
                key = lkey.pop(0)
                branche = arbre[key]
                return fun(branche, lkey)
        return  fun(self.arbre, lkey)
    
    def get_rep(self, path) : 
        lkey = path.split('//')
        lkey.pop(0)
        def fun(arbre, lkey) :
            if lkey == [] :
                if isinstance(arbre, dict) : 
                    keys = arbre.keys()
                    l = []
                    for key in keys :   
                        l.append(path + '//' + key)
                    return l
                else : 
                    return []
            else :
                key = lkey.pop(0)
                branche = arbre[key]
                return fun(branche, lkey)
        return  fun(self.arbre, lkey)
   
def create_adresses(csv_traitement, adresse) :
    nav = navigate(csv_traitement)
    dic_adresse_vu = {}
    for adr in nav.l_adresse :
        if adr == '8187 Sta. EulÃ\xa0lia de RonÃ§ana - Espagne':
            adr = 'Santa Eulàlia de Ronçana - Espagne'
        print(adr)
        if not pd.isnull(adr) :
            dic_adresse_vu[adr] = dist.distance(adr, adresse)
            if dic_adresse_vu[adr] is None :
                dic_adresse_vu[adr] = 0
    return(dic_adresse_vu)

def create_dico(csv_traitement, csv_ifc, csv_meth, adresse, 
                l_cat_mat, l_cat_iso, dicsaved = None) : 
    
    DICO = {}
    DICO['type'] = {}
    DICO['mat'] = []
    DICO['mat_name'] = []
    DICO['mat_energie'] = {}
    DICO['surface'] = []
    DICO['Emat'] = []
    DICO['Emet'] = []
    DICO["dens_mat"] = []
    DICO['dist_prod'] = [[]]
    DICO['indicemat'] = {}
    DICO['mat_quantite_u']={}
    
    nav = navigate(csv_traitement)
    
    if dicsaved is None :
        dic_adresse_vu = {}
        for adr in nav.l_adresse :
            if adr == '8187 Sta. EulÃ\xa0lia de RonÃ§ana - Espagne':
                adr = 'Santa Eulàlia de Ronçana - Espagne'
            print(adr)
            if not pd.isnull(adr) :
                dic_adresse_vu[adr] = dist.distance(adr, adresse)
                if dic_adresse_vu[adr] is None :
                    dic_adresse_vu[adr] = 0
                    
    else : 
        dic_adresse_vu = dicsaved
    
    dico_adresse = {}
    
    def remplissage(l_cat) :
        l = []
        for cmat in l_cat : 
            l_path = []
            for c in cmat : 
                path = nav.parcourir(c)[0] + '//' + c
                l_path += nav.get_rep(path)
                for chemin in l_path : 
                    prods = nav.get_rep(chemin)
                    dico_adresse[chemin] = []
                    for prod in prods : 
                        dic = nav.get(prod)
                        if not pd.isnull(dic['ADRESSE PRODUCTEUR']) :
                            dico_adresse[chemin].append([dic['ADRESSE PRODUCTEUR'], dic_adresse_vu[dic['ADRESSE PRODUCTEUR']]])
            l.append(l_path)
        return l 
    
    lmat = remplissage(l_cat_mat)
    liso = remplissage(l_cat_iso)
        
    LMAT = {'mur_inte': [lmat[0], liso[0]], 
            'mur_exte' : [lmat[1], liso[1]], 
            'Plafonds': [lmat[2], liso[2]], 
            'Sols': [lmat[3], liso[3]]
            }
    

    
    list_id = []                            #liste des identifiants des objets
    list_volume = []                        #liste des volumes de chaque objet
    list_surface = []                       #liste des surfaces de chaque objet 
    dico_type = {'mur_inte': [], 'mur_exte' : [], 'Plafonds': [], 'Sols': []}
    
    f_prop = open(csv_ifc, 'r')
    line = csv.reader(f_prop, delimiter = ';')
    
    
    for l in line:
        # print(l)
        if l[0]!='Catégorie':
            list_id.append(l[1])
            list_volume.append(l[3])
            list_surface.append(l[2])
            # print(l)
            if l[4]=='Extérieur' and l[0]=='Murs':
                # print("Important")
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
        th_utile = not (typ == 'mur_inte')
        c_mat, c_iso = LMAT[typ]
        lmat, liso = [], []
        def lmatiso(l, c) : 
            for mat in c :
                l.append(mat)
                paths = nav.get_rep(mat)
                energie = 0
                n_energie = 0
                conduc = 0
                n_conduc = 0 
                for path in paths :
                    dic_mat = nav.get(path)
                    if not pd.isnull(dic_mat['EQ CO2']) :
                        energie += dic_mat['EQ CO2']
                        n_energie += 1
                    if not pd.isnull(dic_mat['BILAN']) :
                         conduc += dic_mat['BILAN']
                         n_conduc += 1
                if n_conduc != 0 :
                    conduc = conduc/n_conduc
                else :
                    conduc = np.NAN
                if n_energie != 0 : 
                    energie = energie/n_energie # On moyenne les valeurs pour plus de cohérence 
                else : 
                    energie = np.NAN
                try : 
                    symb = 'DONNEE ENVIRONNEMENTALE PAR DEFAUT'
                    path2ministre = nav.parcourir('', path=mat, symb=symb)
                    # print(path2ministre)
                    dic_mat = nav.get(path2ministre[0])
                    DICO['mat_name'].append(mat)
                    if not pd.isnull(dic_mat['QUANTITE']) :
                        number = re.match('[0-9]*', dic_mat['QUANTITE'])
                        unite = dic_mat['QUANTITE'][number.span()[1]]
                        try : 
                            number = float(number[0].replace(',', '.'))
                        except :
                            number = number[0]
                    else : 
                        number = np.nan
                    DICO['mat_quantite_u'][mat] = unite
                    DICO['mat_energie'][mat] = [number, energie]
                    DICO['mat'].append(conduc)
                    DICO['Emat'].append(energie)
                except : 
                    pathpif = nav.get_rep(mat)[0]
                    dic_mat = nav.get(pathpif)
                    # print(dic_mat)
                    DICO['mat_name'].append(mat)
                    if not pd.isnull(dic_mat['QUANTITE']) :
                        number = re.match('[0-9]*', dic_mat['QUANTITE'])
                        unite = dic_mat['QUANTITE'][number.span()[1]]
                        try : 
                            number = float(number[0].replace(',', '.'))
                        except :
                            number = number[0]
                    else : 
                        number = np.nan
                    DICO['mat_quantite_u'][mat] = unite
                    DICO['mat_energie'][mat] = [number, energie]
                    DICO['mat'].append(conduc)
                    DICO['Emat'].append(energie)
            return
        lmatiso(lmat, c_mat)
        lmatiso(liso, c_iso)
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
    # list_repertoire = [rep.split('//')[-1] for rep in DICO['mat_name']]
    list_repertoire = DICO['mat_name']
    for repertoire in list_repertoire:
        dico_materiau[repertoire] = []
    for l in line:
        for repertoire in list_repertoire:
            if repertoire.split('//')[-1].lower() in l[6].lower():
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
    
    DICO['Methodes'] = l_meth
    
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
    
    DICO['dist_prod'] = [[1000 for k in range(n_mat)] for j in range(n_adr)]
    
    DICO['meth_mat'] = [[0 for k in range(n_meth)] for j in range(n_mat)]
    j = 0
    for cond in DICO['mat'] :
        for k in range(n_meth) :
            DICO['meth_mat'][j][k] = 1 
            # if l_meth[k] in dico_materiau[DICO['mat_name'][j]] :
            #     DICO['meth_mat'][j][k] = 1 
        j += 1
    
    c = 0 
    for mat in DICO['mat_name'] :
        DICO['indicemat'][mat] = c
        c += 1 
    
    DICO['c_depl'] = 1 # A vérifier
    DICO['dist_dech'] = []
    
    return(DICO, dic_adresse_vu, dico_adresse)
    
def json_adresse(dic_adr, path = "/home/theophile/Documents/Projet G1-G2/adresses.json") :
    l = []
    for adr in dic_adr :
        l.append(adr)
    with open(path, "w") as fp : 
        json.dump(l, fp)
    return

if __name__ == '__main__' :
    csv_traitement = '/Users/theophilemounier/Desktop/github/Interface_Zeroc/Files/TRAITEMENTpropre.csv'
    csv_meth = '/Users/theophilemounier/Desktop/github/Interface_Zeroc/Files/construction.csv'
    ifc_file = '/Users/theophilemounier/Desktop/github/Interface_Zeroc/Files/non_traite/11 Jay St - 2015.ifc'
    if not os.path.exists('../../Files/traite') : 
        os.mkdir('../../Files/traite')
    csv_ifc = '../../Files/non_traite/11 Jay St - 2015.csv'
    # ifc2csv(ifc_file, csv_ifc)
    nav = navigate(csv_traitement)
    adresse = '59650'
    l_cat_mat = [['Cloisonnement'], ['Cloisonnement'], ['Cloisonnement'], ['Cloisonnement']]
    l_cat_iso = [['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
                 ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
                 ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)'], 
                 ['Isolants thermiques et acoustiques pour murs (ITE)', 'Isolants thermiques et acoustiques pour murs (ITI)']]
    
 