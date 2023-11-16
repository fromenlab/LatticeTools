from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os
import hashlib
from datetime import datetime
import json
from collections import OrderedDict

##########
# External
##########

def get_libraries(self):
    # Includes logic from Giulio Piacentino
    # Source: https://www.grasshopper3d.com/forum/topics/gh-filename-is-python
    core_libraries = {}
    addon_libraries = {}
    objids = {}
    
    server = Grasshopper.Instances.ComponentServer
    for obj in self.OnPingDocument().Objects:
        if obj == self: continue #Ignore this component.
        
        objId = obj.ComponentGuid
        if objids.has_key(objId): continue
        objids[objId] = ""
        
        lib = server.FindAssemblyByObject(obj)
        if lib == None: continue
        if core_libraries.has_key(lib.Id) or addon_libraries.has_key(lib.Id): continue
        
        if lib.IsCoreLibrary:
            core_libraries[lib.Id] = lib
        else:
            addon_libraries[lib.Id] = lib
    
    return core_libraries, addon_libraries

##########
# Original
##########

def make_id(properties):
    properties_string = ','.join(map(str, properties))
    properties_fragment = (hashlib.md5(properties_string.encode("UTF-8")).hexdigest())[:3]

    date_info = datetime.now().strftime("%y%m%d")
    date_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    instance_fragment = (hashlib.sha256(date_utc.encode("UTF-8")).hexdigest())[:2]

    unique_id = '-'.join([date_info, properties_fragment, instance_fragment])
    
    return unique_id, date_utc

def get_units(ghdoc):
    scriptcontext.doc = Rhino.RhinoDoc.ActiveDoc
    base_units = rs.UnitSystemName()
    scriptcontext.doc = ghdoc
    
    return base_units

def get_device():
    device = Rhino.Runtime.HostUtils.DeviceId.ToString()

    return device

def get_software_build():
    rhino_build = str(Rhino.RhinoApp.Version)
    rhino_date = Rhino.RhinoApp.BuildDate
    gh_build = str(Grasshopper.Versioning.Version)
    gh_date = Grasshopper.Versioning.BuildDate

    return rhino_build, rhino_date, gh_build, gh_date

def combine_inputs(input_json):
    inputs = OrderedDict()
    for item in input_json:
        if item:
            item = str(item).replace("\n", "")
            inputs.update(json.loads(item, object_pairs_hook=OrderedDict))
    return inputs