# -*- coding: utf-8 -*-
# +
import sys
import os
import json
from collections import defaultdict
from datetime import datetime
import tempfile
import subprocess
import random
import urllib
import zipfile

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from tqdm.notebook import tqdm

import joblib

import ipywidgets as widgets
from IPython.display import display
import markdown

from azureml.core import Workspace, Dataset

from dotenv import load_dotenv, set_key

from github import Github


def turn_to_luis_utterance(turn: dict, intent_name: str, label_to_entity: dict) -> dict:
    """Convertit un turn du jeu de données en une utterance labellisée pour LUIS."""
    
    text = turn["text"]
    
    # Intent par défaut
    intent = "None"

    entity_labels = []
    for i in turn["labels"]["acts_without_refs"]:
        for l in i["args"]:
            k = l["key"]
            v = l["val"]
            
            if k == "intent":
                # Si il y a le label "intent", il s'agit d'une demande
                # de réservation.
                intent = intent_name
            elif k and v:
                # Les autres labels sont des entités
                if k in label_to_entity.keys():
                    start_char_index = text.lower().find(v.lower())
                    if start_char_index == -1:
                        continue
                    
                    end_char_index = start_char_index + len(v) - 1
                    
                    # On met en forme l'entité au format LUIS
                    entity_labels.append({
                        "entity": label_to_entity[k],
                        "startPos": start_char_index,
                        "endPos": end_char_index,
                        "children": []
                    })
    
    # On met en forme le texte labellisé au format LUIS
    res = {
        "text": text,
        "intent": intent,
        "entities": entity_labels,
    }
    return res


def turns_to_LUIS(
    frames: list,
    intent_name: str,
    label_to_entity: dict
) -> pd.DataFrame:
    """Convertit les turns utilisateur du jeu de données pour LUIS."""
    
    res = []
    # Pour chaque dialogue
    for frame in frames:
        # On crée un id pour identifier les tours de chaque dialogue
        user_turn_id = 0
        
        # Pour chaque tour du dialogue
        for turn in frame["turns"]:
            # On vérifie si il s'agit bien de l'utilisateur
            if turn["author"] == "user":
                # On ajoute l'id du tour
                row = {"user_turn_id": user_turn_id}
                user_turn_id += 1
                
                # On ajoute l'utterance au format LUIS
                row.update(turn_to_luis_utterance(turn, intent_name, label_to_entity))
                
                # On ajoute le résultat à la liste
                res.append(row)
    
    # On convertit les données en DataFrame
    df = pd.DataFrame(res)
    
    # On ajoute le nombre d'entitées labellisées dans le texte
    df["entity_total_nb"] = df["entities"].apply(len)
    
    # Pour chaque entitée, on ajoute le nombre de fois qu'elle apparait
    for entity_name in label_to_entity.values():
        df[f"{entity_name}_nb"] = df["entities"].apply(
            lambda x: len(list(
                filter(lambda x1: x1["entity"] == entity_name, x)
            ))
        )
    
    # On ajoute le nombre de mot dans le texte
    df["text_word_nb"] = df["text"].apply(lambda x: len(x.split()))
    
    return df

