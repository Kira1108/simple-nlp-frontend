import os
from pathlib import Path

LABEL_SET_FOLDER = Path("./labelsets")

def create_default_label(db, k, v):
    db.update_metafield(**{k:v})
    
def get_labelset_names():
    files = os.listdir(LABEL_SET_FOLDER)
    return [f.split(".")[0] for f in files]

def get_options(label_set_name:str):
    path = LABEL_SET_FOLDER / f"{label_set_name}.txt"
    with open(path, "r") as f:
        return [l.strip() for l in f.readlines()]
    
    
def save_labelset(name, content):
    path = LABEL_SET_FOLDER / f"{name}.txt"
    with open(path, "w") as f:
        f.write(content)