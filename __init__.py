import pytris
import json

for i in pytris.main(headless = True):
    if "LOSS" in i:
        break
    #print(json.loads(i))
