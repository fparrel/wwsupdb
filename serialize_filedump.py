import json

def save_rivers(rivers):
    with open('rivers-current.json','w') as f:
        json.dump(rivers.values(),f)

def load():
    with open('rivers-merged-cleaned.json','r') as f:
        rivers_array = json.load(f)
    for river in rivers_array:
        yield (river['name'],river)

def load_rivers():
    return dict(load())
