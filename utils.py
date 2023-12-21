import os
from pathlib import Path

LABEL_SET_FOLDER = Path("./labelsets")

def create_default_label(db, k, v):
    """Update metadatas with map {k:v}"""
    db.update_metafield(**{k:v})
    
def get_labelset_names():
    """Return a list of labelset names"""
    files = os.listdir(LABEL_SET_FOLDER)
    return [f.split(".")[0] for f in files]

def get_options(label_set_name:str):
    """Return a list of options for a given label set"""
    path = LABEL_SET_FOLDER / f"{label_set_name}.txt"
    with open(path, "r") as f:
        return [l.strip() for l in f.readlines()]
    
    
def save_labelset(name, content):
    """Save a labelset file to project repo"""
    path = LABEL_SET_FOLDER / f"{name}.txt"
    with open(path, "w") as f:
        f.write(content)