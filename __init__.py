import pytris
import json

for i in pytris.main(headless = False):
    if "LOSS" in i:
        break
    #print(json.loads(i))
