# TODO: properly handle enumerated nodes

import os.path
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET
import json

from props import PropertyNode, root

# internal dict() tree parsing routine
def parseDict(pynode, xmlnode, basepath):
    overlay  = 'overlay' in xmlnode.attrib
    exists = xmlnode.tag in pynode.__dict__
    if len(xmlnode) or 'include' in xmlnode.attrib:
        # has children
        newnode = PropertyNode()
        if 'include' in xmlnode.attrib:
            filename = basepath + '/' + xmlnode.attrib['include']
            print "calling load():", filename, xmlnode.attrib
            load(filename, newnode)
        if 'n' in xmlnode.attrib:
            # enumerated node
            n = int(xmlnode.attrib['n'])
            if not exists:
                pynode.__dict__[xmlnode.tag] = []
            elif not type(pynode.__dict__[xmlnode.tag]) is list:
                savenode = pynode.__dict__[xmlnode.tag]
                pynode.__dict__[xmlnode.tag] = [ savenode ]
            tmp = pynode.__dict__[xmlnode.tag]
            pynode.extendEnumeratedNode(tmp, n)
            pynode.__dict__[xmlnode.tag][n] = newnode
        elif exists:
            if not overlay:
                # append
                # print "node exists:", xmlnode.tag, "overlay:", overlay
                if not type(pynode.__dict__[xmlnode.tag]) is list:
                    # we need to convert this to an enumerated list
                    print "converting node to enumerated:", xmlnode.tag
                    savenode = pynode.__dict__[xmlnode.tag]
                    pynode.__dict__[xmlnode.tag] = [ savenode ]
                pynode.__dict__[xmlnode.tag].append(newnode)
            else:
                # overlay (follow existing tree)
                newnode = pynode.__dict__[xmlnode.tag]
        else:
            # create new node
            pynode.__dict__[xmlnode.tag] = newnode
        for child in xmlnode:
            _parseXML(newnode, child, basepath)
    else:
        # leaf
        value = xmlnode.text
        if 'type' in xmlnode.attrib:
            if xmlnode.attrib['type'] == 'bool':
                print xmlnode.tag, "is bool"
                if value == '0' or value == 'false' or value == '':
                    value = False
                else:
                    value = True
        if 'n' in xmlnode.attrib:
            # enumerated node
            n = int(xmlnode.attrib['n'])
            if not exists:
                pynode.__dict__[xmlnode.tag] = []
            elif not type(pynode.__dict__[xmlnode.tag]) is list:
                savenode = pynode.__dict__[xmlnode.tag]
                pynode.__dict__[xmlnode.tag] = [ savenode ]
            tmp = pynode.__dict__[xmlnode.tag]
            pynode.extendEnumeratedLeaf(tmp, n, "")
            pynode.__dict__[xmlnode.tag][n] = value
            # print "leaf:", xmlnode.tag, value, xmlnode.attrib
        elif exists:
            if not overlay:
                # append
                if not type(pynode.__dict__[xmlnode.tag]) is list:
                    # convert to enumerated.
                    print "converting node to enumerated"
                    savenode = pynode.__dict__[xmlnode.tag]
                    pynode.__dict__[xmlnode.tag] = [ savenode ]
                pynode.__dict__[xmlnode.tag].append(value)
            else:
                # overwrite
                pynode.__dict__[xmlnode.tag] = value
        elif type(xmlnode.tag) is str:
            pynode.__dict__[xmlnode.tag] = value
        else:
            # print "Skipping unknown node:", xmlnode.tag, ":", value
            pass
                
# load a json file and create a property tree rooted at the given node
# supports "mytag": "include=relative_file_path.json"
def load(filename, pynode):
    try:
        f = open(filename, 'r')
        newdict = json.load(f)
        f.close()
    except:
        print filename + ": json load error:\n" + str(sys.exc_info()[1])
        return

    path = os.path.dirname(filename)
    print "path:", path
    parseDict(pynode, dict, path)

def buildDict(root, pynode):
    for child in pynode.__dict__:
        print child
        node = pynode.__dict__[child]
        if isinstance(node, PropertyNode):
            root[child] = dict()
            buildDict(root[child], node)
        elif type(node) is list:
            root[child] = []
            for i, ele in enumerate(node):
                if isinstance(ele, PropertyNode):
                    newdict = dict()
                    root[child].append( newdict )
                    buildDict(newdict, ele)
                else:
                    root[child].append(str(ele))
   
        elif type(child) is str:
            root[child] = str(node)
        else:
            print "skipping:", child, ":", str(node)
        
# save the property tree starting at pynode into a json xml file.
def save(filename, pynode=root):
    root = dict()
    buildDict(root, pynode)
    try:
        f = open(filename, 'w')
        json.dump(root, f, indent=2, sort_keys=True)
        f.close()
    except:
        print filename + ": json save error:\n" + str(sys.exc_info()[1])
        return