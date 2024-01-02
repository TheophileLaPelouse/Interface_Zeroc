#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 15:15:53 2023

@author: theophile
"""

import cplex
import pandas as pd
import numpy as np
from numpy import random as rd
import json
# from tridonnees import create_dico, DICO
#%%
"""
Génération de colonnes

En gros on doit recréer tout ce uqi était avant nos variables de décisions soit :
    x = eppaisseur de chaque mat dans chaque pièce
    xbool = version booléenne de chacune des pièces 
    qmat = qunatité de chacun des matériaux
    y = méthode utilisée pour chaque pièce
    t = date de départ de construction
    lieu_prod = lieu de production
    lieu_dech = lieu de dépo des déchets 
    
Pour s'aider dans tout ça, on va pouvoir utiliser des tableaux utiles :
    mat_piece = matériaux disponibles pour chaque type de pièces 
    thermique_utile = qu'elle pièce ont une utilité thermique
    methode_mat = qu'elle méthode pour quel mat
    methode_piece = ...
    
    
Quelles sont nos contraintes : 
    x>0 => xbool > 0
    forall(j in mat) {
      	sum(i in produ) lieu_prod[i][j] >= qmat[j] ;
      	sum(p in pos) x[p][j]*surface[p]/dens_mat[j] <= qmat[j] ;
        sum(d in disp) lieu_disp[d][j] <= sum(p in pos, m in meth, k in 1..3) xbool[p][j]*y[p][m]*dechet_meth[m][j] ; // On enlève tous les déchets du chantier
        forall(p in pos) 
            xbool[p][j] <= sum(m in meth) y[p][m]*methode_mat[j][m] ;
            xbool[p][j] <= mat_piece[j][plan[p]] ;
        forall(pr in produ)
        	lieu_prod[pr][j] <= dist_prod[pr][j] ; 
        	lieu_disp[d][j] <= dist_disp[d][j] ;
    sum(p in pos, m in meth) y[p][m] == 1 ;
    
    Le temps 
    forall(i in pos) {
	forall(j in pos)
  	if (i != j) {
    	if (position[i][3] > position[j][3]) {t[i] >= t[j] + sum(m in meth) y[j][m]*temps_meth[m][plan[j]] ; }
  	}
  }

    Contraintes thermiques à refaire -> ça devient 
    Rthmaison*deltaT*deltat <= energie beaucoup
    
    
Sur le modèle : 
    On minimize l'énergie dépenser c'est à dire sum(x[i]*T[i]) où T[i] c'est le booléen qui dit quels patterns
    on utilise. x[i] c'est l'énergie dépenser dans par le pattern d'énergie
    
    Contrainte = en fonction de disponibilité dans les différents site de production et de trie, plus pourquoi pas disponibilité des méthodes en fonction du personnel.
    
    note : ce srait du coup, on minimize l'énergie utilisé et la contrainte tient sur est ce qu'on a assez d'isolation du coup si on reprend le modèle des tissus :
        width devient, choix de la provenance, choix des méthodes, choix de l'ordre dans lequel c'est fait 
        sachant que le pattern donne quels matériaux et où, et on aura un truc en plus qui donne isolation total.
        
Voir pour faire un truc ou on décide d'un mur type, d'un plafond et d'un sol, pour calculer les combin de resistance pour faire un modèle plus intéressant.
--------------------------

my_obj = []
pos =10
meth = 10
for k in range(pos) :
    for j in range(meth) :
        my_obj.append(Emet[j])
        
couplé avec 

my_colnames = []
meth = 0
pos =0
my_colnames += ["y_%s_%s" % (k, j) for k in range(pos) for j in range(meth)]
-----------------------------

"""
class colonne : 
    # def __init__(self, tab_piece, dico_type, dico_mat, dTh = 15, dTe = 5, tempsh = 30*24*60*60*6, tempse = 30*24*60*60*6, Emax = 10**9) :
    #     self.truc = 0
    #     self.rth = 0
    #     self.pieces = [] # On va les supposer défini avec position de deux coins opposés (0, 0) et (1, 1) donc liste de tuple de tuple
    #     self.piece_th = []
    #     self.nbpieces = len(self.pieces)
    #     # Comment est ce que je veux mes données 
    #     # dico_piece = [[pos, type, emax, dim, th_utile, mat, e]] (peut être un tableau de dico pour lisibilité du code)
    #     # dico_type['type'] = [lmat, liso, lmeth]
    #     # dico_mat[mat] = (ro, energie/kg)
    #     for p in tab_piece : 
    #         typ = p['type']
    #         self.pieces.append(Piece(*dico_type[typ], *tab_piece))
        
    #     self.qmat, self.energie_tot = self.calc_mat(dico_mat)
    #     self.rtot()
    #     self.valid = self.isvalid(dTh, dTe, tempsh, tempse, Emax)
        
    def __init__(self, Lpiece, dico_mat, dTh = 15, dTe = 5, tempsh = 30*24*60*60*6, tempse = 30*24*60*60*6, Emax = 10**9):
        self.pieces = Lpiece
        # print(Lpiece)
        self.nbpieces = len(self.pieces)
        self.pieces_th = []
        for k in range(self.nbpieces) :
            # print(self.pieces[k].th_utile)
            if self.pieces[k].th_utile :
                self.pieces_th.append(self.pieces[k])
        self.qmat, self.energie_tot = self.calc_mat(dico_mat)
        self.rtot()
        self.valid = self.isvalid(dTh, dTe, tempsh, tempse, Emax)
    
    
    def calc_mat(self, dico_mat) :
        # Intialisation de qmat
        qmat = dict()
        for tab in dico_mat :
            qmat[tab] = [0, 0]
        
        # Pour toute les pièces on update qmat
        for p in self.pieces :
            for mat in p.qmatv : 
                qmat[mat][0] += p.qmatv[mat]*dico_mat[mat][0]
        
        for mat in dico_mat : 
            qmat[mat][1] = qmat[mat][0]*dico_mat[mat][1]
        
        energie_tot = sum(qmat[mat][1] for mat in qmat)
        return(qmat, energie_tot)
        
    
    def rtot(self) :
        Rth = []
        # print(self.pieces_th)
        for p in self.pieces_th :
            Rth.append(p.res_th)
        self.rth = rpara(Rth)
        
    def isvalid(self, dTh, dTe, tempsh, tempse, Emax) :
        # print('rth = ', self.rth)
        return(self.rth*(dTh*tempsh + dTe*tempse) > 0.01) # Ne pas oublier de le remettre bien
               
            
        
class Piece :
    def __init__(self, dico, lmat, liso, lmeth, pos, piece_type, emax, dim, th_utile, mat = [], e = []) :
        self.pos = pos
        self.th_utile = th_utile
        nbmat = len(lmat)
        self.mat = []
        self.matid = []
        self.matid.append(lmat[rd.randint(nbmat)])
        self.mat.append(dico['mat'][dico['indicemat'][self.matid[-1]]]) # Matériaux présent dans une pièce, au moins un truc solide
        nbcouche = 1
        if self.th_utile :
            nbcouche = rd.randint(5) + 1 # On met entre 1 et 5 matériaux
            nbiso = len(liso)
            for k in range(nbcouche - 1) :
                i = rd.randint(nbmat + nbiso)
                if i >= nbmat :
                    self.matid.append(liso[i - nbmat])
                    self.mat.append(dico['mat'][dico['indicemat'][liso[i - nbmat]]])
                else : 
                    self.matid.append(lmat[i])
                    self.mat.append(dico['mat'][dico['indicemat'][lmat[i]]])
        permutation = rd.permutation(nbcouche)
        self.e = [0 for k in range(nbcouche)]
        if not isinstance(emax, float) :
            try : 
                emax = float(emax.replace(',', '.'))
            except : 
                print('warning problème de emax')
                emax = 0
        etot = emax + (rd.random()-0.5)*2/10*emax
        reste = 1
        for k in permutation[:-1] :
            prop = rd.random()*reste
            reste = reste - prop
            ei = prop*etot
            self.e[k] = ei
        self.e[permutation[-1]] = reste*etot
        
        if mat != [] :
            self.mat = mat
        if e != [] :
            self.e = e
            
        self.res_th = rserie(self.mat, self.e) # Conductivité thermique
        # print(self.res_th)
        self.type = piece_type
        # self.meth = lmeth[rd.randint(len(lmeth))]
        self.t0 = 0
        if not isinstance(dim, float) :
            try : 
                dim = float(dim.replace(',', '.'))
            except :
                print('Warning surface incorrecte')
                dim = 0
        self.S = dim
        self.qmatv = dict()
        for k in range(nbcouche) :
            self.qmatv[self.matid[k]] = self.S*self.e[k]
    
    def update_S(self, surface) : 
        self.S = surface
            
        
            
            



def rserie(Mat, E) :
    # Mat = liste de conductivité thermique des matériaux présent dans la série de résistance
    n = len(Mat)
    return(sum(E[k]/Mat[k] for k in range(n)))

def rpara(Rth) :
    n = len(Rth)
    return(1/(sum(1/Rth[k] for k in range(n))))
    
        
def gencol(dico, Nbpat) :
    types = []
    for typ in dico["type"] :
        types.append(typ)
    indicemat = dico['indicemat'] #dictionnaire d'indice des matériaux
    matindice = []
    c= 0
    for mat in dico['mat'] :
        matindice.append(mat)
        c += 1
    
    nbpat = sum(Nbpat)
    n_piece = 0
    for typ in types :
        n_piece += len(dico['piece'][typ])
    n_type = len(types)
    n_mat = len(dico["mat"])
    x = [[[0 for m in range(n_mat)] for j in range(n_piece)] for k in range(nbpat)]
    ind_pat = []
    LPIECE = []
    # Faudra faire de la suite une fonction qu'on appelle pour chaque type de pièce ce sera plus pratique 
    
    ind_pat = []
    c = 0
    for p in range(n_type) :
        i = len(dico["piece"][types[p]])
        ind_pat.append(range(c, c+i))
        c += i 
        
        
    
    def boucle(ityp, typ, nbpat) :
        Lpiece = []
        for k in range(nbpat) :
            [lmat, liso] = dico["type"][typ]
            [pos, emax, dim, th_utile, mat, e] = dico["piece"][typ][0] # de base, mat et e ne sont pas défini
            piece = Piece(dico, lmat, liso, [], pos, typ, emax, dim, th_utile, mat = mat, e = e)
            # print(piece.mat)
            Lpiece.append(piece)
            n_mat = len(piece.mat)
            for i in ind_pat[ityp] :
                for j in range(n_mat) :
                    # print(k, i, j)
                    x[k][i][indicemat[piece.matid[j]]] = piece.e[j]
        return(Lpiece)
    
    for i in range(n_type) :
        LPIECE.append(boucle(i, types[i], Nbpat[i]))
    def somme_t(T) :
        n = len(T)
        s = []
        # print(T)
        for k in range(n) :
            s = s + T[k]
        return(s)
    # print(ind_pat)
    tup_valid = np.zeros(Nbpat)
    # On va faire simple on va décider d'un nombre de truc utile à faire et c'est tout probablement 
    # for k1 in range(Nbpat[0]) :
    #     for k2 in range(Nbpat[1]) :
    #         for k3 in range(Nbpat[2]) :
    #             for k4 in range(Nbpat[3]) :
    #                 for k5 in range(Nbpat[4]) :
    #                     K = [k1, k2, k3, k4, k5]
    #                     Lpiece = somme_t(LPIECE[i][K[i]]*(ind_pat[i][-1]+1) for i in range(n_type))
    #                     col = colonne(Lpiece)
    #                     if col.valid :
    #                         tup_valid[k1, k2, k3, k4, k5] = 1 
    # print(len(LPIECE), len(LPIECE[0]))
    # print(LPIECE[3])
    
    for k1 in range(Nbpat[0]) :
        for k2 in range(Nbpat[1]) :
            for k3 in range(Nbpat[2]) :
                for k4 in range(Nbpat[3]) :
                    K = [k1, k2, k3, k4]
                    # Lpiece = somme_t([LPIECE[i][K[i]] for j in ind_pat[i] for i in range(n_type)])
                    # for i in range(n_type) :
                    #     print(i, K[i], len(LPIECE[i]))
                    Lpiece = [LPIECE[i][K[i]] for j in ind_pat[i] for i in range(n_type)]
                    for i in range(n_type) :
                        for j in ind_pat[i] : 
                            j2 = j - ind_pat[i][0]
                            surface = dico['piece'][types[i]][j2][2]
                            LPIECE[i][K[i]].update_S(surface)
                            Lpiece.append(LPIECE[i][K[i]])
                    # print([LPIECE[i][K[i]] for j in ind_pat[i] for i in range(n_type)])
                    # print(Lpiece)
                    col = colonne(Lpiece, dico["mat_energie"])
                    # print(col.valid)
                    if col.valid or True:
                        tup_valid[k1, k2, k3] = 1 
                        
    
    # x = [[[1]]]
    # tup_valid = [[[1]]] # Tableau des tuple de pattern valid.
    return (x, tup_valid, indicemat, ind_pat, LPIECE, matindice)

def gencoltest(dico, nbpat1, nbpat2, nbpat3) :
    x = [[[1]]]
    tup_valid = [[[1]]] # Tableau des tuple de pattern valid.
    return (x, tup_valid)

def testdico() :
    d = dict()
    d["Emet"] = [1] 
    d["Emat"] = [1]
    d["dist_prod"] = [[1]]
    d["dist_dech"] = [[1]] # pas check
    d["c_depl"] = 1
    d["surface"] = [1]
    d["dens_mat"] = [1]
    d["dech_meth"] = [[1]] # pas check
    d["meth_mat"] = [[1]] 
    d["piece"] = {"mur" : [[1, 1, 1, 1, [], []]], "plafond" : [[1, 1, 1, 1, [], []]], "sol" : [[1, 1, 1, 1, [], []]]} #[pos, emax, dim, th_utile, mat, e]
    d["mat"] = [1] # Conductivité thermique du matériaux
    d["type"] = {"mur" : [[1], []], "plafond" : [[1], []], "sol" : [[1], []]} # [lmat, liso]
    d["mat_energie"] = {1 : [1, 1]}
    d["mat_name"] = {1 : "acier"}
    return(d)

def aupif(xtot, taux) :
    n = len(xtot)
    nred = int(len(xtot)*taux/100)
    K = np.random.permutation(nred)
    Kbar = []
    for k in range(n) :
        if k not in K :
            Kbar.append(k)
    return([xtot[k] for k in K], K, Kbar)

#%% Ici on va mettre le modèle cplex en commençant par les fonctions objectifs et définition des variables de décision
"""
my_obj = []
pos =10
meth = 10
for k in range(pos) :
    for j in range(meth) :
        my_obj.append(Emet[j])
        
couplé avec 

my_colnames = []
meth = 0
pos =0
my_colnames += ["y_%s_%s" % (k, j) for k in range(pos) for j in range(meth)]
"""
# tout ce qui suit sera des len de truc
# On a mis mat alors que ça correspond toujours pas à des matériaux en vrai.
# csv_traitement = 'TRAITEMENT.csv'
# csv_ifc = 'propriétés.csv'
# csv_meth = 'construction.csv'
# adresse = "Avenue Paul Langevin Villeneuve-d'Ascq"

# # cmis, cmiis, cmes, cmeis, cps, cpis, css, csis = ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation'], ['º Isolation']
# cmis, cmiis, cmes, cmeis, cps, cpis, css, csis = ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre'], ['Laine de verre']

# dico = testdico()
# dico = DICO
# c = 0
# for s in dico['surface'] : 
#     if not isinstance(s, float) :
#         dico['surface'][c] = float(s.replace(',', '.'))
#     c += 1
# meth = len(dico['Emet'])
# piece = len(dico['surface'])
# matv = len(dico['mat']) # Matériaux vendus
# matd = 0 # Matériaux à jeter, voir si diff de vendus en fonction de comment on le fait
# prod = len(dico['dist_prod'])
# dech = 0
# dico['c_depl'] = 1

# nbpat1 = 0
# nbpat2 = 0
# nbpat3 = 1
# xtot, tup_valid = gencoltest(dico, nbpat1, nbpat2, nbpat3)
# Nbpat = [10, 10, 10, 10]
# xtot, tup_valid, indicemat, ind_pat, LPIECE, matindice = gencol(dico, Nbpat)
# x, K, Kbar = aupif(xtot, 10)
# x = xtot
# nbpat = nbpat1 + nbpat2 + nbpat3
# xbool = [[[1 if x[k][p][j] > 0 else 0 for j in range(matv)] for p in range(piece)] for k in range(len(x))]

transcription = {"mur_exte" : "pattern_m_", "sol" : "pattern_s_", "plafond" : "pattern_p_", 'mur_inte' : 'pattern_m_i_'}

def genmodel(dico, x, xbool, tup_valid, Nbpat, path = 'model.lp') :
    
    c = 0
    for s in dico['surface'] : 
        if not isinstance(s, float) :
            dico['surface'][c] = float(s.replace(',', '.'))
        c += 1
    meth = len(dico['Emet'])
    piece = len(dico['surface'])
    matv = len(dico['mat']) # Matériaux vendus
    matd = 0 # Matériaux à jeter, voir si diff de vendus en fonction de comment on le fait
    prod = len(dico['dist_prod'])
    dech = 0
    dico['c_depl'] = 1
    
    nbpat = sum(pat for pat in Nbpat)
    Obj = []
    
    obj_meth = [dico["Emet"][m] for po in range(piece) for m in range(meth)]
    dvar_meth = ["y%d_%d" % (po, m) for po in range(piece) for m in range(meth)]
    typ_meth = ['B' for po in range(piece) for m in range(meth)]
    
    obj_mat = [dico["Emat"][m] for m in range(matv)]
    dvar_mat = ["qmat_%d" % m for m in range(matv)]
    typ_mat = ["C" for m in range(matv)]
    
    obj_prod = [dico["dist_prod"][pr][m]*dico["c_depl"] for pr in range(prod) for m in range(matv)]
    dvar_prod = ["lieu_prod_%d_%d" % (pr, m) for pr in range(prod) for m in range(matv)]
    typ_prod = ["C" for pr in range(prod) for m in range(matv)]
    
    obj_dech = [dico["dist_dech"][d][m]*dico["c_depl"] for d in range(dech) for m in range(matd)]
    dvar_dech = ["lieu_dech_%d_%d" % (d, m) for d in range(dech) for m in range(matd)]
    typ_dech = ["C" for d in range(dech) for m in range(matd)]
    
    obj_t = [0 for p in range(piece)] # On le fera en dernier parce que c'est le plus tendu
    dvar_t = ["t%d" % p for p in range(piece)]
    typ_t = ["C" for p in range(piece)]
    
    
    dvar_pattern_p = ["pattern_p_%d" % k for k in range(Nbpat[0])]
    dvar_pattern_s = ["pattern_s_%d" % k for k in range(Nbpat[1])]
    dvar_pattern_m = ["pattern_m_%d" % k for k in range(Nbpat[2])]
    dvar_pattern_m_i = ['pattern_m_i_%d' % k for k in range(Nbpat[3])] 
    dvar_pat = dvar_pattern_p + dvar_pattern_s + dvar_pattern_m + dvar_pattern_m_i
    obj_pat = [0 for k in range(nbpat)] 
    typ_pat = ["B" for k in range(nbpat)]
    
    # dvar_yxbool = ["yxbool_%d_%d_%d" % (k, po, m, j) for k in range(nbpat) for po in range(piece) for m in range(meth) for j in range(x[0])]
    # typ_yxbool = ["B" for k in range(nbpat) for po in range(piece) for m in range(meth) for j in range(x[0])]
    # # Traduit la varible xbool*y suaf que c'est pas linéaire donc faut rajouter une variable avec des contraites qui oblige la même chose
    # # Il manque un truc le fait que y'a des pattern pour xbool
    # En fait ça sert à rien yxbool parce que xbool c'est pas une variable de décision
    
    dvar = dvar_meth + dvar_mat + dvar_prod + dvar_dech + dvar_t + dvar_pattern_p + dvar_pattern_s + dvar_pattern_m + dvar_pattern_m_i #+ dvar_yxbool
    Obj = obj_meth + obj_mat + obj_prod + obj_dech + obj_t + obj_pat
    typ = typ_meth + typ_mat + typ_prod + typ_dech + typ_t + typ_pat #+ typ_yxbool
    lb = [0 for k in range(len(dvar))]
    
    # Initialisation du modèle
    
    prob = cplex.Cplex()
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.variables.add(obj=Obj, names=dvar, lb=lb, types=typ)
    
    # Maintenant on écrit les contraintes 
    
    # On suppose qu'on a un tableau de tableau de pièces.
    # Contrainte 1 : lien entre pattern et qmat
    # Faudra mettre linking contraint entre xbool, y et yxbool
    
    
    # Contrainte : 1 seul pattern par plafond, un seul pattern par mur et un seul pattern par sol
    rows = [[dvar_pattern_p, [1 for k in range(Nbpat[0])]], 
            [dvar_pattern_s, [1 for k in range(Nbpat[1])]], 
            [dvar_pattern_m, [1 for k in range(Nbpat[2])]], 
            [dvar_pattern_m_i, [1 for k in range(Nbpat[3])]]]
    rhs = [1, 1, 1, 1]
    senses = "EEEE"
    rownames = ["patternp", "patterns", "patternm", "patternmi"]
    prob.linear_constraints.add(lin_expr=rows, senses=senses, rhs=rhs, names=rownames)
    
    # row = [[dvar_pattern_m, [1 for k in range(nbpat3)]]]
    # rhs = [1]
    # sense = "E"
    # rowname = ["patternm"]
    # prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
    
    # Contrainte 2 : pattern de quadruplet possible en fonction de tup_valid
    
    for k in range(Nbpat[0]) :
        for j in range(Nbpat[1]) :
            for i in range(Nbpat[2]) :
                for p in range(Nbpat[3]) :
                    # print(tup_valid[k][j][i][p])
                    row = [[["pattern_p_%d" % k, "pattern_s_%d" % j, "pattern_m_%d" % i, "pattern_m_i_%d" % p], 
                            [1 for count in range(4)]]]
                    rhs = [3+tup_valid[k][j][i][p]]
                    sense = 'L'
                    rowname = ["tup_pattern"]
                    prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
                
    for j in range(matv) :
    
        # sum(p in pos, k in T) pattern[k]*x[p][j]*surface[p]/dens_mat[j] <= qmat[j] for j in mat
        s = sum(x[k][p][j]*dico['surface'][p] for k in range(nbpat) for p in range(piece))
        # print("\n", s, '\n')
        row = [[dvar_pat + ["qmat_%d" % j], [s for k in range(nbpat)] + [-1]]]
        rhs = [0] 
        rowname = ["qmat_x"]
        prob.linear_constraints.add(lin_expr=row, senses="L", rhs=rhs, names=rowname)
        
        # Contrainte liant production et quantité de matériaux 
        row = [[["lieu_prod_%d_%d" % (i, j) for i in range(prod)] + ["qmat_%d" % j], [1 for i in range(prod)] + [-1]]]
        rhs = [0]
        sense = 'G'
        rowname = ["prod_qmat"]
        prob.linear_constraints.add(lin_expr=row, senses="G", rhs=rhs, names=rowname)
        
        # Contrainte liant déchet et quantité de matériaux 
        #sum(d in disp) lieu_disp[d][j] <= sum(p in pos, m in meth, for k in pat) y[p][m]*xbool[k][p][j]*dechet_meth[m][j] 
        
        # row = [[["lieu_dech_%d_%d" % (d, j) for d in range(dech)] 
        #         + ["y%d_%d" % (p, m) for k in range(nbpat) for p in range(piece) for m in range(meth)], 
        #        [1 for d in range(dech)] + [-1*dico["dech_meth"][m][j]*xbool[k][p][j] for k in range(nbpat) for p in range(piece) for m in range(meth)]]]
        # # Faut vérifier cette contrainte mais on va tester comme ça pour le moment
        # rhs = [0]
        # sense = 'L'
        # rowname = ["dech_meth"]
        # prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
    
        """
        forall(p in pos) 
            xbool[p][j] <= sum(m in meth) y[p][m]*methode_mat[j][m] ;
            xbool[p][j] <= mat_piece[j][plan[p]] ; je crois que celle là n'existe plus parce que xbool déjà défini
            
            -> devient :
                dvar_pattern[k]*xbool[k][p][j] <= sum(m in meth) y[p][m]*methode_mat[j][m] ;
        forall(pr in produ)
        	lieu_prod[pr][j] <= dist_prod[pr][j] ; On peut produire que si le site de production est visible (dist_prod = 0 si indisponible et vaut toujours plus que 1)
        	lieu_disp[d][j] <= dist_disp[d][j] ;
        """
        for p in range(piece) :
            row = [[["y%d_%d" % (p, m) for m in range(meth)] + dvar_pat, 
                   [-1*dico["meth_mat"][j][m] for m in range(meth)] + [xbool[k][p][j] for k in range(nbpat)]]]
            rhs = [0]
            sense = "L"
            rowname = ["meth_mat"]
            prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
        
        for pr in range(prod) :
            row = [[["lieu_prod_%d_%d" % (pr, j)], [0.01]]]
            rhs = [dico["dist_prod"][pr][j]]
            sense = "L"
            rowname = ["lieu de production disponible"]
            prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
            
        for d in range(dech) :
            row = [[["lieu_dech_%d_%d" % (d, j)], [1]]]
            rhs = [dico["dist_dech"][pr][j]]
            sense = "L"
            rowname = ["lieu de production disponible"]
            prob.linear_constraints.add(lin_expr=row, senses=sense, rhs=rhs, names=rowname)
        
    # sum(p in pos, m in meth) y[p][m] == 1 ; voir si c'est pas une méthode par pièce et par matériaux en vrai, sachant que dans matériaux c'est l'object en soit et pas le mat
    row = [[dvar_meth, [1 for p in range(piece) for m in range(meth)]]]
    rhs = [1]
    sense = 'E'
    rowname = ["1meth"]
    
    prob.write(path)
    
    return(prob, Obj)


#%% travail avec le prob

# prob, Obj = genmodel(dico, x, tup_valid, Nbpat, path = '/home/theophile/Documents/Projet G1-G2/model.lp')
# prob.solve()

# obj0 = prob.solution.get_objective_value()
# ref = 10 # Valeur à déterminer par exemple en faisant une moyenne sur quand on fait au pif, ou alors en trouvant des résultats



# def margcost(x, prob) :
#     """
#     La formule c'est MC(i) = sum Pattern(i)(j)*demande(j).dual
#     Où Pattern(i)(j) nous ça va être x(i)(p)(m) où on prend la somme sur toutes les pièces des couts marginaux en fait.
#     Et demande(j).dual est le dual associé à la contrainte nommée demande (dans un ordre code)
    
#     On obtient alors MC(k) = sum(p, j) (x[k][p][j]*dico['surface'][p]/dico['dens_mat'][j]*dual(qmat_x)
#                                         + sum(p, j) xbool[k][p][j]*dual(meth_mat)
#     """
    
    
#     # mc  = 0
#     # pi = my_prob.solution.get_dual_values()
    
#     # for p in range(piece) :
#     #     for j in range(mat) :
#     #         mc += x[p][j]*dico['pièces2'][p][2]/dico['dens_mat'][j]*
#     # Pour l'instant on va faire au pif parmis ce qu'il reste
#     mc = 0
#     return(mc)

# error = 0.1
# hist = [obj0]
# pattern = [xtot[k] for k in Kbar]
# while obj0 - ref > error :
#     ref = obj0
#     mini = margcost(pattern[0])
#     newx = pattern[0]
#     for x in pattern :
#         tamp = margcost(x)
#         if tamp < mini :
#             mini = tamp
#             newx = x 
    
#     prob = genmodel(dico, x+newx, tup_valid)
#     prob.solve()
#     obj0 = prob.solution.get_objective_value()
#     hist.append(obj0)

#%% Sauvegarde des résultats


def to_json(prob, Obj, dico, Nbpat, LPIECE, transcription, dic_adresse_vu, path="/home/theophile/Documents/Projet G1-G2/bonjour.json") :
    c = 0
    for s in dico['surface'] : 
        if not isinstance(s, float) :
            dico['surface'][c] = float(s.replace(',', '.'))
        c += 1
    meth = len(dico['Emet'])
    piece = len(dico['surface'])
    matv = len(dico['mat']) # Matériaux vendus
    matd = 0 # Matériaux à jeter, voir si diff de vendus en fonction de comment on le fait
    prod = len(dico['dist_prod'])
    dech = 0
    dico['c_depl'] = 1
    
    k = piece*meth
    ind_meth = range(k)
    i = k 
    k = i + matv
    ind_mat = range(i, k)
    i = k
    k = i + prod*matv
    ind_prod = range(i, k)
    i = k
    k = i + dech*matd
    ind_dech = range(i, k)
    i = k 
    k = i + piece
    ind_t = range(i, k)
    i = k 
    # k = i + nbpat1
    # ind_pat1 = range(i, k)
    # i = k 
    # k = i + nbpat2
    # ind_pat2 = range(i, k)
    # i = k 
    # k = i + nbpat3
    # ind_pat3 = range(i, k)
    # k = i + nbpat4
    # ind_pat4 = range(i, k)
    # k = i + nbpat5
    # ind_pat5 = range(i, k)
    
    futur_json = dict()
    d_ener = dict()
    d_ener["Total"] = prob.solution.get_objective_value()
    
    def create_ener(d_energie, I, L) :
        n = len(I)
        for i in range(n) :
            var = prob.solution.get_values([k for k in I[i]])
            obj = [Obj[k] for k in I[i]]
            d_energie[L[i]] = sum(var[k]*obj[k] for k in range(len(I[i])))
        return
    
    I = [ind_meth, ind_mat, ind_prod, ind_dech, ind_t]
    L = ["Methodes", "Materiaux", "Sites de Production (transport)", "Dechetteries (transport)", "temps d'utilisation"]
    create_ener(d_ener, I, L)
    futur_json['Energie'] = d_ener
    
    dpiece = dict()
    Pat = ['mur_exte', 'sol', 'plafond', 'mur_inte']
    # note -> Faudra adater les dimensions et la position des pièces (genre ce qui n'ets pas utile à la modélisation)
    def create_dpiece(dpiece, Pat, Nbpat) :
        ntype = len(Nbpat)
        for j in range(ntype) :
            for i in range(Nbpat[j]) : 
                dic = dict()
                for k in range(meth) :
                    try :
                        m = prob.solution.get_values("y%d_%d" % (i, k))
                    except : 
                        print("erreur : variable y%d_%d non trouvée" % (i, k))
                        m  = 0
                    if m :
                        break 
                dic["Methode"] = dico['Methodes'][k]
                
                for k in range(Nbpat[j]) :
                    deb = transcription[Pat[j]]
                    m = prob.solution.get_values(deb + ("%d" % k))
                    if m :
                        break 
                # Définir fonction
                piece_retenue = LPIECE[j][k]
                c = 0
                dic["Matériaux"] = {}
                for mat in piece_retenue.matid :
                    dic["Matériaux"][mat] = str(piece_retenue.e[c]) + 'm'
                    c += 1
            dpiece[Pat[j]] = dic
        return
    
    create_dpiece(dpiece, Pat, Nbpat)
    futur_json['Piece'] = dpiece 
    
    dmat = {}
    
    def create_mat(dmat, ind_mat) :
        sdmat = dict()
        for j in ind_mat :
            qmat = prob.solution.get_values(j)
            if qmat > 0 :
                sdmat[dico['mat_name'][j - ind_mat[0]]] = qmat
        dmat["Quantité"] = sdmat
        return
    
    l_adr = list(dic_adresse_vu.keys())
    
    def create_mat2(dmat, I, L, indicemat, l_adr):
        n = len(I)
        
        for i in range(n) :
            sdmat = dict()
            for mat in dmat["Quantité"] :
                for j in range(I[i]) :
                    var = prob.solution.get_values("lieu_prod_%d_%d" % (j, indicemat[mat]))
                    if var > 0 :
                        sdmat[l_adr[j]] = str(var) + 'm2'
            dmat[L[i]] = sdmat
        return
    
    create_mat(dmat, ind_mat)
    I = [prod, dech]
    L = ["Site de Production", "Déchetterie"]
    create_mat2(dmat, I, L, dico['indicemat'], l_adr)
    sdmat = {}
    for mat in dmat["Quantité"] : 
        sdmat[mat] = dico["Emat"][dico['indicemat'][mat]]*dmat["Quantité"][mat]
        dmat["Quantité"][mat] = str(dmat["Quantité"][mat]) + 'm2'
    dmat["Energie/Materiaux"] = sdmat
    futur_json['Matériaux'] = dmat
    
    with open(path, "w") as fp :
        json.dump(futur_json, fp, ensure_ascii=False)
    return
                
    

# Manque contrainte temporelle mais on verra après les premiers tests


def pleinfor(n, nb, nargs, *args) :
    argu = [[args[k] for k in range(nargs)] for i in range(nb)]
    if n <= 0 :
        print(argu[0])
    else :
        for k in range(nb) :
            argu[k].append(k)
            pleinfor(n-1, nb, nargs+1, *argu[k])
        

 # Fonction qui détermine si th_utile

# def th_utiles(self) :
#     # Première méthode, on regarde les plans que forment les pièces et on 
#     piece_nonth = []
#     num = [k for k in range(self.nbpieces)]
#     k = 0
#     n = len(num)
#     ind_xmax = max([k for k in range(self.nbpieces)], key = lambda x : max(abs(self.pieces[x][0][0]), abs(self.pieces[x][1][0])))
#     ind_ymax = max([k for k in range(self.nbpieces)], key = lambda x : max(abs(self.pieces[x][0][1]), abs(self.pieces[x][1][1])))
#     while k < n :
#         vect = (self.pieces[k][0][0] - self.pieces[k][1][0], self.pieces[k][0][1] - self.pieces[k][1][1])
#         droite = [(vect[0]*k, vect[1]*k) for k in np.linspace(0, max(xmax, ymax), 1)] # Voir le 1 en fonction de si y'a trop de truc dedans
#         i = k + 1
#         pieces_traversees = []
#         while i < n :
#             plan = 
#             for points in droite :
#     # Donc là faudrait caractériser les plans puis résoudre des équations en inversant des matrices 
    
#     # Autre méthode possible, faire comme si on avait un graphe et parcourir les pièces au bord que par leurs extrémités.
#     new_piece = self.pieces[ind_xmax]
#     while new_piece not in self.pieces_th :
#         if new_piece not in self.pieces_th :
#             self.pieces_th.append(new_piece)
#         coin1, coin2 = new_piece
#         coin3 = 