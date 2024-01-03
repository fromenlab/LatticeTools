from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
from Rhino.Geometry import Point3d as p3
import rhinoscriptsyntax as rs

__version__ = "1.0.0"

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "LatticeTools"
    
    def get_AssemblyDescription(self):
        return "Components for generating lattice structures."

    def get_AssemblyVersion(self):
        return __version__

    def get_AuthorName(self):
        return "irw@udel.edu"
    
    def get_Id(self):
        return System.Guid("21e63a1b-e357-4356-afa1-507d72a02888")