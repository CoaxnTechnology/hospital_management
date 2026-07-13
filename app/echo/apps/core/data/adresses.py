import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(BASE_DIR, 'data')

def codes_postaux_json(pays = "Tunisie"):
    if pays != "Tunisie":
        return []
    with open(os.path.join(p, 'adresses.json'), mode='r', encoding='utf-8') as f:
        return f.read()


def codes_postaux():
    with open(os.path.join(p, 'adresses.json'), 'r') as f:
        return json.load(f)
