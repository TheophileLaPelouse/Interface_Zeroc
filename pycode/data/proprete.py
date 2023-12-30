#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 18:39:41 2023

@author: theophilemounier
"""

def mise_au_propre(csv, path_to_save) : 
    with open(csv, 'r') as f :
        text = f.read()
        text = text.replace('Ã¨', 'è').replace('Ã±', 'ñ').replace('Ã©', 'é')
    with open(path_to_save, 'w') as f: 
        f.write(text)
        
