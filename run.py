import json
import flask
import xml.etree.ElementTree as ET
from lxml import html
import urllib
import urllib2
# Uncomment the code below when running on google app engine. Otherwise, app will timeout when retrieving compat data.
# from google.appengine.api import urlfetch
# urlfetch.set_default_fetch_deadline(45)

app = flask.Flask(__name__)

@app.route('/')
def landing_message():
    message = {"Message": "Welcome to the RSBP to Json converter. Simply add a biobrick part id to the end of the url to retrieve part information in json.",
                "Updates": "You can now retrieve compatibility data for a part by adding '?compat=true' to the url after the part name."}
    return flask.jsonify(**message)

@app.route('/<bba_name>')
def send_BBaJson(bba_name, compat=False):
    """Input: a biobrick name Ex. BBa_B0034 
    Output: Retrieves the xml for the part, converts it to JSON, returns an affirmative statement and dumps the JSON to file."""
    if bba_name[0:3] != "BBa":
        message = {"Message": "Sorry %s is not a valid biobrick name. Please try entering again with a format similar to: BBa_B0034." % bba_name}
        return flask.jsonify(**message)
    #request the part xml, turn it into an ElementTree
    params = urllib.urlencode({"part":bba_name})
    data = urllib2.urlopen("http://parts.igem.org/cgi/xml/part.cgi?", params)
    root = ET.fromstring(data.read())
    # parse the root into a dictionary using the recursive seek_children function.
    json_dict = {} 
    seek_children(root, json_dict)
    #checks to see if the user wants to also retrieve compatibility data for the part.
    compat = flask.request.args.get('compat')
    if compat != None and compat.lower() == "true":
        json_dict["rsbpml"]["part_list"]["part"]["compatibility"] = get_compatibility(bba_name)
    # json.dump(json_dict ,open(bba_name+".json", 'w'), sort_keys=True, indent=4) # uncomment this line to dump the dictionary into a .json file.
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
                child_list.append(child_dict)
            #Adding the {child_tagname:child_list} dictionary as the child of the root tag. 
            json_dict[root.tag] = {root[0].tag:child_list}
        #This else block adds the current root to the json_dict argument then calls seek_children() on each of its children.
        else:
            new_dict = {}
            json_dict[root.tag] = new_dict
            for child in root:
                seek_children(child, new_dict)


def get_compatibility(bba_name):
    """Input: Biobrick name in the format: BBa_B0034.
    Output: Queries MediaWiki API and parses out compatibility data for that Biobrick part."""
    #Send a get request to mediawiki api to retrieve data for parsing on the part.
    params = urllib.urlencode({"action": "parse", "text":"{{:Part:%s}}" % bba_name, "prop":"text", "format":"json"})
    r = urllib2.urlopen("http://parts.igem.org/wiki/api.php?", params)
    #Load the data as json and parse it to retrieve the section of the html containing the chassis compatibility data.
    data = json.load(r)["parse"]["text"]["*"]
    compat_data = html.fromstring(data).find_class('box')
    #Iterate through the compatibility data and sort backbones into compatible and incompatible lists.
    compatible = []
    incompatible = []
    for chassis in compat_data:        
        status = chassis.text_content().split(" ")
        if status[0].lower() == "compatible":
            compatible.append(status[2])
        else:
            #The array slicing is used here to separate the name of the backbone from other text that the .split(" ") missed.
            incompatible.append(status[2][:status[2].find("]")+1])
    return [{"compatible":compatible},{"incompatible":incompatible}]


if __name__ == '__main__':
    # app.debug = True
    app.run()
