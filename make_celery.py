#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 19:59:42 2023

@author: theophile
"""

from app import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]