#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:42:28 2023

@author: theophile
"""

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.api.material
import csv

#Fonctions pour convertir les pieds en mètres

def pied_metre(ft):
    return 0.3048*ft

def pied2_metre2(ft2):
    return 0.3048*0.3048*ft2

def pied3_metre3(ft3):
    return 0.3048*0.3048*0.3048*ft3


#Création du fichier objet

ifc_file_path = "11 Jay St - 2015.ifc"

def ifc2csv(ifc, csv_path) :
    ifc_file = ifcopenshell.open(ifc)
    
    
    #Création des listes d'objets
    
    #Murs
    list_wall = ifc_file.by_type("IfcWall")
    #Plafonds
    list_covering = ifc_file.by_type("IfcCovering")
    #Sols
    list_slab = ifc_file.by_type("IfcSlab")
    
    
    
    n_wall = len(list_wall)
    n_covering = len(list_covering)
    n_slab = len(list_slab)
    
    # Objets test
    wall = list_wall[0]
    covering = list_covering[0]
    ground = list_slab[0]
    
    
    
    
    
    #Ecriture des données nécessaires dans un fichier csv
    
    
    nom_colonnes = ["Catégorie", "Identifiant", "Surface", "Volume", "Localisation", "Matériau"]
    f = open(csv_path, 'w')
    
    f.write(nom_colonnes[0] + ";" + nom_colonnes[1] + ";" + nom_colonnes[2] + ";" + nom_colonnes[3] + ";" + nom_colonnes[4] + ";" + nom_colonnes[5] + "\n")
    
    #Ecriture des propriétés des murs
    
    for i in range(0, n_wall):
        
        c = ifcopenshell.util.element.get_psets(list_wall[i])["Autre"]["Catégorie"]
        ide = str(ifcopenshell.util.element.get_psets(list_wall[i])["Autre"]["id"])
        s = str(pied2_metre2(ifcopenshell.util.element.get_psets(list_wall[i])["Cotes"]["Surface"]))
        v = str(pied3_metre3(ifcopenshell.util.element.get_psets(list_wall[i])["Cotes"]["Volume"]))
        l = ifcopenshell.util.element.get_psets(list_wall[i])["Construction"]["Fonction"]
        if hasattr(ifcopenshell.util.element.get_psets(list_wall[i]), "Matériaux et finitions") :
            m = ifcopenshell.util.element.get_psets(list_wall[i])["Matériaux et finitions"]["Matériau structurel"]
        else:
            m = ""
        
        f.write(c + ";" + ide + ";" + s + ";" + v + ";" + l + ";" + m + "\n")
    
    #Ecriture des propriétés des plafonds
    
    for i in range(0, n_covering):
        
        c = ifcopenshell.util.element.get_psets(list_covering[i])["Autre"]["Catégorie"]
        ide = str(ifcopenshell.util.element.get_psets(list_covering[i])["Autre"]["id"])
        s = str(pied2_metre2(ifcopenshell.util.element.get_psets(list_covering[i])["Cotes"]["Surface"]))
        v = str(pied3_metre3(ifcopenshell.util.element.get_psets(list_covering[i])["Cotes"]["Volume"]))
        l = ""
        if hasattr(ifcopenshell.util.element.get_psets(list_covering[i]), "Matériaux et finitions") :
            m = ifcopenshell.util.element.get_psets(list_covering[i])["Matériaux et finitions"]["Matériau structurel"]
        else:
            m = ""
        
        f.write(c + ";" + ide + ";" + s + ";" + v + ";" + l + ";" + m + "\n")
    
    #Ecriture des propriétés des sols
    
    for i in range(0, n_slab):
        if ifcopenshell.util.element.get_psets(list_slab[i])["Autre"]["Catégorie"] == 'Sols' :
            c = ifcopenshell.util.element.get_psets(list_slab[i])["Autre"]["Catégorie"]
            ide = str(ifcopenshell.util.element.get_psets(list_slab[i])["Autre"]["id"])
            s = str(pied2_metre2(ifcopenshell.util.element.get_psets(list_slab[i])["Cotes"]["Surface"]))
            v = str(pied3_metre3(ifcopenshell.util.element.get_psets(list_slab[i])["Cotes"]["Volume"]))
            l = ""
            if hasattr(ifcopenshell.util.element.get_psets(list_slab[i]), "Matériaux et finitions") :
                m = ifcopenshell.util.element.get_psets(list_slab[i])["Matériaux et finitions"]["Matériau structurel"]
            else:
                m = ""
        
            f.write(c + ";" + ide + ";" + s + ";" + v + ";" + l + ";" + m + "\n")
    
    f.close()