import json
import flask
import xml.etree.ElementTree as ET
import requests
import xmltodict
import httplib

app = flask.Flask(__name__)

@app.route('/')
def landing_message():
    message = {"Message": "Welcome to the RSBP to Json converter. Simply add a biobrick part id after the trailing '/' in the url to retrieve part information in json."}
    return flask.jsonify(**message)

@app.route('/<bb_name>')
def send_BBaJson(bb_name):
    """Input: a biobrick name Ex. BBa_B0034 
    Output: Retrieves the xml for the part, converts it to JSON, returns an affirmative statement and dumps the JSON to file."""
    #request the part xml, turn it into an ElementTree
    # r = requests.get("http://parts.igem.org/cgi/xml/part.cgi?part="+bba_name) #uncomment this line to use the requests library instead of httplib
    conn = httplib.HTTPConnection("parts.igem.org/cgi/xml/part.cgi?part=")
    conn.request("GET", bb_name)
    r = conn.getresponse()
    root = ET.fromstring(r.read())
    # parse the root into a dictionary using the recursive seek_children function.
    json_dict = {}
    seek_children(root, json_dict)
    # json_dict = xmltodict.parse(r.read()) # uncomment this line to use xmltodict rather than the seek_children function. 
    # json.dump(json_dict ,open(bb_name+".json", 'w'), sort_keys=True, indent=4) # uncomment this line to dump the dictionary into a .json file.
    return flask.jsonify(**json_dict)

def seek_children(root, json_dict):
    """Input: An ET.root (the root of an XML tree), and a dictionary object.
    Output: Recursively builds a dictionary from an xml tree."""
    if len(root)==0:
        #The base case, when the function encounters a leaf node (a tag with no sub-elements). 
        if type(root.text) == str:
            json_dict[root.tag] = root.text.strip()
        else:
            json_dict[root.tag] = None
    else:
        #The iterative step.
        #If all children of the root have the same tag name, then each child is placed in a separate dictionary object. 
        #These dict. objects are then added to a child_list object which becomes the value of the child's tag in the resulting json.
        if len(root.findall(root[0].tag)) > 1: 
            child_list =[]
            #iterating through all the children and adding them to a list. 
            for child in root:
                child_dict = {}
                seek_children(child, child_dict)
                child_list.append(child_dict[root[0].tag])
            #Adding the {child_tagname:child_list} dictionary as the child of the root tag. 
            json_dict[root.tag] = {root[0].tag:child_list}
        #This else block adds the current root to the json_dict argument then calls seek_children() on each of its children.
        else:
            new_dict = {}
            json_dict[root.tag] = new_dict
            for child in root:
                seek_children(child, new_dict)



if __name__ == '__main__':
    # app.debug = True
    app.run()
