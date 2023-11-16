from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os
import hashlib
from datetime import datetime
import log_utils

class SystemInfo(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Logging - System Info", "SystemInfo", """Provides a scripting component.""", "LatticeTools", "Log")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("61f4317f-f9d1-4e44-a7d2-d7c3492db396")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "refresh", "refresh", "Recalculate the component")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "project_dir", "project_dir", "The project's main directory")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "save_directory", "save_directory", "Folder to save the STL and log output")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "id_properties", "id_properties", "Key features of the part. Takes single value or list of properties")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "part_id", "part_id", "A unique ID for the generated part. Takes the format (date)-(properties fragment)-(instance fragment)")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "date_utc", "date_utc", "The UTC date and time at which computation was performed")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "mesh_path", "mesh_path", "Full path for the STL output")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "log_path", "log_path", "Full path for the log output")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "gh_file", "gh_file", "Path and name of the Grasshopper definition")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "base_unit", "base_unit", "Base unit of the Rhino and Grasshopper file (e.g. millimeter)")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "device", "device", "Device used for computation")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "rhino_build", "rhino_build", "Rhino software version")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "rhino_date", "rhino_date", "Rhino software version release date")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "gh_build", "gh_build", "Grasshopper software version")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "gh_date", "gh_date", "Grasshopper software version release date")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "core_dependencies", "core_dependencies", "Default libraries used in this definition")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "addon_dependencies", "addon_dependencies", "Installed libraries used in this definition")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        result = self.RunScript(p0, p1, p2, p3)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)
                self.marshal.SetOutput(result[2], DA, 2, True)
                self.marshal.SetOutput(result[3], DA, 3, True)
                self.marshal.SetOutput(result[4], DA, 4, True)
                self.marshal.SetOutput(result[5], DA, 5, True)
                self.marshal.SetOutput(result[6], DA, 6, True)
                self.marshal.SetOutput(result[7], DA, 7, True)
                self.marshal.SetOutput(result[8], DA, 8, True)
                self.marshal.SetOutput(result[9], DA, 9, True)
                self.marshal.SetOutput(result[10], DA, 10, True)
                self.marshal.SetOutput(result[11], DA, 11, True)
                self.marshal.SetOutput(result[12], DA, 12, True)
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAF6SURBVEhLYwgICNeUlJF9zMvL91dMXOI/NTAPL+9fkJkgsxlAjLTsvP9nrt2lKgaZKSkj95iBF+hykMD+i/f/Lz/xiCoYZBbITJBPGEBeAnFAErFr31AFg8wCmQkye9QCrHjUAoJ41AKCmL4WCAoJgTmbzz7437T7OVUwyCyQmYKCQv8Z+AUEvqzYsBUsQE0MMpNfQPALg5WtfSk3D88fSxu7/9HxSRg4Nin1f0t3//+O/skoGCQGksOmB2QWyEyQ2QwgEBoaymxiYdmrpaW7BR2rqKk/9PQP/J5TUvUZGYPEQHLY9JhYWPWAzAQbTghExCUvL6xu/L9qxyEUDBIDyUGVkQ8CQsL6QEGCHsYgMZAcVBlukJCcnmNkbP7R08f3v5ePHwb2Dwz+f/zsxf8PX7xFwSAxkBw2PSCzQGYmpmRkM4AYNx88/f/u87f/T998AGMQG2TIq/efwRjEJlUeZCbIbNpbAPKGsanZB1xBRA4GmQUyMzElIxsAgSzS87fNrvUAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, refresh, project_dir, save_directory, id_properties):
        ghdoc = scriptcontext.doc
        part_id = None
        date_utc = None
        gh_file = None
        base_unit = None
        device = None
        rhino_build = None
        rhino_date = None
        gh_build = None
        gh_date = None
        core_dependencies = None
        addon_dependencies = None


        part_id, date_utc = log_utils.make_id(id_properties)
        gh_path = os.path.realpath(ghdoc.Path)

        if not save_directory:
            save_directory = os.path.dirname(ghdoc.Path)

        file_name_base = "\\".join([save_directory, part_id])
        mesh_path = "\"{}.stl\"".format(file_name_base)
        log_path = "{}.txt".format(file_name_base)

        if project_dir:
            gh_file = gh_path.split(project_dir)[1]
        else:
            gh_file = gh_path

        base_unit = log_utils.get_units(ghdoc)
        device = log_utils.get_device()
        rhino_build, rhino_date, gh_build, gh_date = log_utils.get_software_build()


        core_libraries, addon_libraries = log_utils.get_libraries(self)

        core_dependencies = []
        for id, lib in core_libraries.iteritems():
            core_dependencies.append("{0} {1}".format(lib.Name, lib.Version))

        addon_dependencies = []
        for id, lib in addon_libraries.iteritems():
            addon_dependencies.append("{0} {1}".format(lib.Name, lib.Version))
        
        return part_id, date_utc, mesh_path, log_path, gh_file, base_unit, device, rhino_build, rhino_date, gh_build, gh_date, core_dependencies, addon_dependencies
