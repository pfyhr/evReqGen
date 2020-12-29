import numpy as np
import json
import pathlib

def output_json(csvfile, name, power):
    #this will be the ugliest workaround ever.
    data = np.genfromtxt(csvfile, skip_header=0, delimiter=',')
    string = '{"name": [{' #hard to get the fstring for name in here...
    for i,j in enumerate(data):
        string += f'"x": {data[i][0]},'
        string += f'"y": {data[i][1]}'
        string += '},{'
    string = string[:-2]
    string += '],'
    string += f'"{name}": {power}'
    string += '}' 
    print(string)

    #make json file
    fpath = pathlib.Path(csvfile)
    print(fpath.stem)
    string_dict = json.loads(string)
    with open(f'./static/json/{fpath.stem}.json', 'w') as json_file:
        json.dump(string_dict, json_file, indent = 4)


if __name__ == "__main__":
    path = 'static/csv/leafRealData.csv'
    output_json(path,'Leaf_real', 80)