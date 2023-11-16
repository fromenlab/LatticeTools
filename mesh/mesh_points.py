from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp

out_mesh = None

def to_json(key, value):
    return '"{}" : "{}"'.format(key, value)

def to_json_value_object_pair(key, value):
    return '"{}" : {{{}}}'.format(key, value)

def get_mesh_report(report_instance, additional_params = None):
    naked_count = 0
    naked_edges = out_mesh.GetNakedEdges()
    if naked_edges is not None:
        naked_count = len(naked_edges)
        
    properties = []
    report = to_json("report_version", report_instance)
    valid = to_json("valid_mesh", out_mesh.IsValid)
    naked = to_json("naked_edges", naked_count)
    closed = to_json("closed_mesh", out_mesh.IsClosed)
    manifold = to_json("manifold_mesh", out_mesh.IsManifold(True))
    disjoint = to_json("disjoint_count", out_mesh.DisjointMeshCount)
    vertices = to_json("vertex_count", out_mesh.Vertices.Count)
    memory = to_json("memory_estimate_mb", out_mesh.MemoryEstimate()*1e-6)
    log = to_json("log_invalid", out_mesh.IsValidWithLog()[1])
    
    properties.extend([report, valid, naked, closed, manifold, disjoint, vertices, memory, log])
    if additional_params:
        properties.extend(additional_params)

    properties_json = '{{{}}}'.format(to_json_value_object_pair(report_instance, ','.join(properties)))

    return properties_json

def get_cut_planes(surfaces, translation_factor = 0):
        planes = set()
        for surface in surfaces:
            print(type(surface))
            reference_point = surface.GetBoundingBox(False).Center
            normal_vector = surface.NormalAt(surface.ClosestMeshPoint(reference_point, 0.0))
            surface.Translate(translation_factor*normal_vector)
            planes.add(surface)
                    
        return planes

class MeshLattice(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Mesh - Meshing (Points)", "MeshLattice", """Convert lattice points to a printable mesh. Includes options to save with modifications for 3D printing.""", "LatticeTools", "Mesh")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("b7ffd35f-393f-4a70-8b46-c927a06c15a4")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "run", "run", "Run the script?")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Point()
        self.SetUpParam(p, "points", "points", "The lattice points for meshing")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "radius", "radius", "Radius of the lattice curves")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "dendroSettings", "dendroSettings", "Settings provided by the Dendro component")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Mesh()
        self.SetUpParam(p, "surfaces", "surfaces", "Script input surfaces.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "bake", "bake", "Bake the part into Rhino?")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "save", "save", "Save the part?")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "file_name", "file_name", "Where to save the part")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "delete", "delete", "Delete the part after saving?")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "out_mesh", "out_mesh", "Dendro-generated mesh of lattice")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "original_report", "original_report", "Mesh report for original lattice")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "mod_report", "mod_report", "Mesh report for modified lattice, with minimal alterations")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "cut_report", "cut_report", "Mesh report for trimmed lattice")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "volume", "volume", "Volume of the final lattice in document units")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "area", "area", "Surface area of the final lattice in document units")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        p5 = self.marshal.GetInput(DA, 5)
        p6 = self.marshal.GetInput(DA, 6)
        p7 = self.marshal.GetInput(DA, 7)
        p8 = self.marshal.GetInput(DA, 8)
        result = self.RunScript(p0, p1, p2, p3, p4, p5, p6, p7, p8)

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
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAJoSURBVEhLY4ACVm1D4/lZpTVv2dg4Q6FixAIOIFYHYkkwDwcIXbJp7/9VOw7975uz7B+QHwPEakDMBJKE0gpA7AHEhcpq6ls8vH3uJ6RkfK9taP43d/GKv/JKan9EJKW/CIiInGBiYqoAqmMFYjhoWLp53//u2Sv+n716+/+hk+f+Tpsz/3dqZvZvO0fndxLSsn8UVDR+axmY/jE0t/2/fN3m/w9fvEXBIHEY1jW2ADkyA2I0BDTMX7fzf8fMZRgaV6zfgqIZhAlZAMIgMyFGQwBOC0CGoWse3BbsOXzi/72nr+AakS2wdfb8Hx6b/L+tZ9L/vJKq/1EJaf89/UP/W9q7/r965+H/XQeO/Z+/dPX/lq4JuC0AGWRi5fDfxSvgf1hM0v+a5g6wpSADYJbmFFXALYVhmBwMg8yEGA0BKBYgY5Bh6JqHhwVGFnb/nTz8/gdFxP1Pzsr/v3XPwf8Xrt+BqwGZCTEaAuAWTJg+539mfik4Mt18gsCReebyjf+bd+7/P3PB0v8N7T3giLz18BmKpTAH2Th5/I+IS8FtAbImEB56+QBdI9UtOH/9LorGVRu3Y2gGxsW/nfsP/Z02e8GforLKv5Ex8Z9ExaV+ggpEfROrvzpG5qDCLhtiNATALajpnPrP2MLqfnxSyq9J02b9Lqms+SUjr/RXRErmq5C4xC0eXv4VQPUFQAwqulWAGFYsMwKxEhCHA3EqEIPqCTiAW1DZPe0vkK8NxKA6QBmItYCYD4gpAtgsoCoYtYAgqJ29ahvEgraJoCSmARGmHjDKLG/+2zZ9yX8Xn8APQD6sNUEhYGAAAPJCbOYDm9fdAAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, run, points, radius, dendroSettings, cut_surfaces, bake, save, file_name, delete):
        global out_mesh
        original_report = None
        cut_report = None
        volume = None
        area = None
        
        if run:
            #   Generate lattice volume and mesh
            out_mesh = ghcomp.DendroGH.PointsToVolume(points = points, point_radius = radius, settings = dendroSettings)
            out_mesh = ghcomp.DendroGH.VolumetoMesh(volume = out_mesh, volume_settings = dendroSettings)

            original_bounds = out_mesh.GetBoundingBox(True)
            original_report = get_mesh_report(report_instance = "original_report")

            #   Make checks and first repairs
            degenerate_faces = to_json("degenerate_faces", out_mesh.Faces.RemoveZeroAreaFaces(0))
            quads_to_tris = to_json("quads_to_tris", out_mesh.Faces.ConvertQuadsToTriangles())
            out_mesh.UnifyNormals()
            mesh_flipped = False
            if(out_mesh.Volume() < 0):
                out_mesh.Flip(True, True, True)
                mesh_flipped = True
            mesh_flipped = to_json("mesh_flipped", mesh_flipped)
            mod_report = get_mesh_report(report_instance = "modified_report", additional_params=[degenerate_faces, quads_to_tris, mesh_flipped])

            #    Split mesh
            if cut_surfaces:
                revised_cut = False
                planes = get_cut_planes(cut_surfaces)
                cut_mesh = Rhino.Geometry.Mesh.CreateBooleanDifference({out_mesh}, planes)[0]
                cut_bounds = cut_mesh.GetBoundingBox(True)

                if (cut_bounds.Volume/original_bounds.Volume < 0.01):
                    revised_cut = True
                    planes = get_cut_planes(cut_surfaces, translation_factor = 0.01)
                    out_mesh = Rhino.Geometry.Mesh.CreateBooleanDifference({out_mesh}, planes)[0]
                else:
                    out_mesh = cut_mesh

                revised_cut = to_json("revised_cut", revised_cut)
                face_count_cut = to_json("face_count_cut", out_mesh.Faces.Count)
                fill_success = to_json("fill_success", out_mesh.FillHoles())
                face_count_filled = to_json("face_count_filled", out_mesh.Faces.Count)
                cut_report = get_mesh_report(report_instance = "cut_report", additional_params=[revised_cut, face_count_cut, fill_success, face_count_filled])

            #   Calculate mesh properties
            volume = out_mesh.Volume()
            areaMassProperties = Rhino.Geometry.AreaMassProperties.Compute(out_mesh)
            area = areaMassProperties.Area

            #   Export
            if bake or save:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(out_mesh)
                id = str(id)

                if save:
                    rs.Command("SelID " + id)
                    rs.Command("-Export " + file_name + " Enter")
                
                    if delete:
                        rs.Command("SelID " + id)
                        rs.Command("Delete")
                
            rs.Command("ClearUndo")
            return out_mesh, original_report, mod_report, cut_report, volume, area
