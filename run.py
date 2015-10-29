import json
import flask
import xml.etree.ElementTree as ET
import requests
import xmltodict

app = flask.Flask(__name__)

@app.route('/<bb_name>')
def hello_world(bb_name):
    """Input: a biobrick name Ex. BBa_B0034 
    Output: Retrieves the xml for the part, converts it to JSON, returns an affirmative statement and dumps the JSON to file."""
    #request the part xml, turn it into an ElementTree
    r = requests.get("http://parts.igem.org/cgi/xml/part.cgi?part="+bb_name)
    root = ET.fromstring(r.text)
    #parse the root into a dictionary using the recursive seek_children function.
    json_dict = {}
    seek_children(root, json_dict)
    #json_dict2 = xmltodict.parse(r.text)
    #dump the dictionary into a .json file.
    json.dump(json_dict ,open(bb_name+".json", 'w'), sort_keys=True, indent=4)
    return "Converted: "+bb_name+" info to JSON from XML."


def seek_children(root, json_dict):
    """Input: An ET.root (the root of an XML tree), and a dictionary object.
    Output: Recursively builds a dictionary from xml tree with a JSON-like structure."""
    #The try case is the iterative step, the except clause is the base case.
    new_dict = {}
    try:
        #If the node has children execute the below. If the node has no children then calling "root[0]" will throw an IndexError and trigger the base case.
        if root[0] != None:
            #This if stmnt deals with the scenario where all the children of root have the same tag name.
            if len([tag for tag in root.findall(root[0].tag)]) > 1: 
                child_list =[]
                for member in root.findall(root[0].tag):
                    child_dict = {}
                    seek_children(member, child_dict)
                    child_list.append(child_dict[root[0].tag])
                json_dict[root.tag] = {root[0].tag:child_list}
            #This else block adds the current root to the json_dictionary then calls seek_children() on each of its children.
            else:
                json_dict[root.tag] = new_dict
                for child in root:
                    seek_children(child, new_dict)
    except IndexError: 
    #The base case, adds the xml tag name as a key in the json_dict with the data within the tags as the value. 
        if type(root.text) == str:
            json_dict[root.tag] = root.text.strip()
        else:
            json_dict[root.tag] = None


if __name__ == '__main__':
    app.debug = True
    app.run()
