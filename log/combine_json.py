from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import json
from collections import OrderedDict
import log_utils

class CombineJson(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Logging - Combine JSON", "combinejson", """Combines a list of JSON inputs into a single JSON object for output.""", "LatticeTools", "Log")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("c0713250-616c-43a8-b863-d7eeda3534f4")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "input_json", "input_json", "JSON objects to combine")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "combined_json", "combined_json", "Combined inputs")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        result = self.RunScript(p0)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)
        
    def get_Internal_Icon_24x24(self):
        o = "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"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, input_json):
        merged = log_utils.combine_inputs(input_json)
        combined_json = json.dumps(merged, sort_keys=False, indent=4, separators=(',', ': '))

        return combined_json