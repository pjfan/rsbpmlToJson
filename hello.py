import json
import flask
import xml.etree.ElementTree as ET
import requests
import xmltodict

app = flask.Flask(__name__)

@app.route('/<bb_name>')
def hello_world(bb_name):
  """Input: a biobrick name in the format BBa_#### 
  Output: Retrieves the xml for the part, converts it to JSON, returns an affirmative statement and saves the JSON."""
  #request the part xml, turn it into an ElementTree
  r = requests.get("http://parts.igem.org/cgi/xml/part.cgi?part="+bb_name)
  root = ET.fromstring(r.text)
  #parse the root into a dictionary of dictionaries/lists.
  json_dict = {}
  seek_children(root, json_dict)
  #json_dict2 = xmltodict.parse(r.text)
  #dump the dictionary into a .json file.
  json.dump(json_dict ,open(bb_name+".json", 'w'), sort_keys=True)
  return "Converted: "+bb_name+" info to JSON from XML."


def seek_children(root, json_dict):
  new_dict = {}
  """Input: An ET.root variable, and a dictionary object.
  Output: Builds a dictionary from xml tree with a JSON-like structure."""
  #The try case is the iterative step, the except clause is the base case.
  try:
    #If the node has children execute the below. If the node has no children "root[0]" will throw an error, the base case.
    if root[0] != None:
      #This if stmnt deals with what to do when all the child elements have the same name.
      if len([tag for tag in root.findall(root[0].tag)]) > 1:
        #When all elements have the same tag names. 
        child_list =[]
        for member in root.findall(root[0].tag):
          child_dict = {}
          seek_children(member, child_dict)
          child_list.append(child_dict[root[0].tag])
        json_dict[root.tag] = {root[0].tag:child_list}
      else:
        #What to do if you're not at a leaf node.
        json_dict[root.tag] = new_dict
        for child in root:
          seek_children(child, new_dict)

  except IndexError: 
    #The base case
    if type(root.text) == str:
      json_dict[root.tag] = root.text.strip()
    else:
      json_dict[root.tag] = None


if __name__ == '__main__':
  app.debug = True
  app.run()
