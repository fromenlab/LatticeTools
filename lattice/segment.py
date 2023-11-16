from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import ghpythonlib.parallel
import ghpythonlib.treehelpers as th

def segment_curves_parallel(curve):
    params = curve.DivideByLength(segment_length, False)
    points = []
    points.append(curve.PointAtStart)
    for t in params:
        points.append(curve.PointAt(t))
    points.append(curve.PointAtEnd)
    return points

class SegmentLattice(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Segment Lattice", "SegmentLattice", """Convert lattice to points for meshing""", "LatticeTools", "Lattice")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("e3542eb6-8910-4014-95cc-e40a8d514f5f")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "curves", "curves", "Curves that make up the lattice")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "radius", "radius", "Minimum radius value for generating mesh")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "points", "points", "Points to input to lattice meshing component")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAADUSURBVEhLYxg5wMDUNl7f3PYMCIPYUGHqAD1LO0NDc9v/yFjf1MoAKk05MDC37UO3ACQGlaYcAA0MRrfA0NwuCCpNOTA2NmYFungz0OB/IAxi29vbs0ClqQeMrKyUQRjKHUnA1NRZ2MDMZoW+qfVv1IgkHYPMAJkFMhNqPDCVmNmUYVNMGbYuhxpPBwtA3tE3tV1OrSACmYUSRCMH0CyjgYoKYKRtQYS19RaQGFSacgA0lLaFHc2La1Dlgm4BVSscEDAws44DVpenQRjEhgoPe8DAAAAazde+0foa1AAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, curves, radius):
        global segment_length 
        segment_length = float(radius)/5
        
        if curves:
            points = ghpythonlib.parallel.run(segment_curves_parallel, curves, True)

        return points