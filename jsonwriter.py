import numpy as np
import json
import pathlib

def output_json(csvfile, name, power):
    #load the csvfile
    data = np.genfromtxt(csvfile, skip_header=0, delimiter=',')
    
    #make a dict of it, as naji suggested!
    name = [{'x':i, 'y':j} for i,j in data] 
    string_dict = {'name': name, 'Leaf_real': power}
    
    #find the filename and put ut in the desired path
    fpath = pathlib.Path(csvfile)
    print(fpath.stem)
    
    #and write it to .json file
    with open(f'./static/json/{fpath.stem}.json', 'w') as json_file:
        json.dump(string_dict, json_file, indent = 4)


if __name__ == "__main__":
    path = 'static/csv/egolfSimData.csv'
    output_json(path,'Leaf_real', 80)