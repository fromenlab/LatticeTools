from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

def clean_primitive(primitive):
    if (primitive.ObjectType == Rhino.DocObjects.ObjectType.Brep):
        meshed_brep = Rhino.Geometry.Mesh.CreateFromBrep(primitive, Rhino.Geometry.MeshingParameters(1))
        meshed_primitive = Rhino.Geometry.Mesh()
        for mesh in meshed_brep:
            meshed_primitive.Append(mesh)

        meshed_primitive.HealNakedEdges(0.01)
    else:
        meshed_primitive = primitive

    meshed_primitive.UnifyNormals()
    meshed_primitive.Weld(3.1415)
    if(meshed_primitive.Volume() < 0):
        meshed_primitive.Flip(True, True, True)

    return meshed_primitive

def get_cut_planes(primitive):
    primitive = rs.coercegeometry(primitive)
    bbox = primitive.GetBoundingBox(True)
    scaled_bbox = bbox
    center = bbox.Center
    center_plane = Rhino.Geometry.Plane(center, Rhino.Geometry.Vector3d(0,0,1))
    scaled_bbox.Transform(Rhino.Geometry.Transform.Scale(center_plane, 1.2, 1.2, 1))

    x_length = scaled_bbox.Max[0] - scaled_bbox.Min[0]
    x_interval = Rhino.Geometry.Interval(-x_length/2, x_length/2)

    y_length = scaled_bbox.Max[1] - scaled_bbox.Min[1]
    y_interval = Rhino.Geometry.Interval(-y_length/2, y_length/2)

    z_vector = Rhino.Geometry.Vector3d(0,0,1)

    top_point = Rhino.Geometry.Point3d(center[0],center[1],bbox.Max[2])
    top_plane = Rhino.Geometry.Plane(top_point, -z_vector)
    top_surface = Rhino.Geometry.PlaneSurface(top_plane, x_interval, y_interval)

    bottom_point = Rhino.Geometry.Point3d(center[0],center[1],bbox.Min[2])
    bottom_plane = Rhino.Geometry.Plane(bottom_point, z_vector)
    bottom_surface = Rhino.Geometry.PlaneSurface(bottom_plane, x_interval, y_interval)

    return [Rhino.Geometry.Mesh.CreateFromSurface(surface, Rhino.Geometry.MeshingParameters(1)) for surface in [top_surface, bottom_surface]]

def get_symmetry_planes(primitive):
    bbox = primitive.GetBoundingBox(True)

    min_coord_x = bbox.Min[0]*1.2
    max_coord_x = bbox.Max[0]*1.2
    x_interval = Rhino.Geometry.Interval(min_coord_x, max_coord_x)
    
    min_coord_y = bbox.Min[1]*1.2
    max_coord_y = bbox.Max[1]*1.2
    y_interval = Rhino.Geometry.Interval(min_coord_y, max_coord_y)
    
    min_coord_z = bbox.Min[2]*1.2
    max_coord_z = bbox.Max[2]*1.2
    z_interval = Rhino.Geometry.Interval(min_coord_z, max_coord_z)

    zx_x_interval = Rhino.Geometry.Interval(bbox.Min[0]*1.2, bbox.Max[0]*1.2)
    zx_z_interval = Rhino.Geometry.Interval((bbox.Min[2]-bbox.Center[2])*1.2, (bbox.Max[2]-bbox.Center[2])*1.2)
    yz_y_interval = Rhino.Geometry.Interval(bbox.Min[1]*1.2, bbox.Max[1]*1.2)
    yz_z_interval = Rhino.Geometry.Interval((bbox.Min[2]-bbox.Center[2])*1.2, (bbox.Max[2]-bbox.Center[2])*1.2)

    plane_point = bbox.Center

    XY_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(0,0,-1)), x_interval, y_interval)
    YZ_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(-1,0,0)), yz_y_interval, yz_z_interval)
    ZX_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(0,-1,0)), zx_z_interval, zx_x_interval)

    return [Rhino.Geometry.Mesh.CreateFromSurface(surface, Rhino.Geometry.MeshingParameters(1)) for surface in [XY_cut, YZ_cut, ZX_cut]]

class Primitive(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Primitive - Prepare (Origin)", "Primitive", """Converts an input primitive to a mesh for lattice generation. Center input at (0,0,0).""", "LatticeTools", "Prepare")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("f88468d1-acbe-40ba-bdf7-5cb2c77196d2")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Geometry()
        self.SetUpParam(p, "primitive", "primitive", "Base shape to populate with lattice geometry. Centered at (0,0,0).")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "primitive", "primitive", "The primitive as a closed mesh")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "cut_surfaces", "cut_surfaces", "Top and bottom surfaces, oriented for trimming the lattice")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "symmetry_surfaces", "symmetry_surfaces", "Surfaces for octant-based symmetry")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "octant", "octant", "Primitive mesh octant (-1, -1, -1)")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "quarter", "quarter", "Primitive mesh quarter (-1, -1)")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        result = self.RunScript(p0)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)
                self.marshal.SetOutput(result[2], DA, 2, True)
                self.marshal.SetOutput(result[3], DA, 3, True)
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAK9SURBVEhLYyAGhGUWmwan5ESmpdVzQYUoB+GpRVbGNk63uXh4/wmJiv+XV9H4z8HJ9U9V1/CtnVfgnojkPHGoUtKBW1DUcl5+wf+xuZX/155+8H/v3S9gvPH80/+ts1f/d/QJ+S+rrPYtKrPYGKqFeOAWGLVYTEr2/9IDV+AGo+M9dz7/T6to+S8oIvbHPzqtyj0kZq6pjfN1O8/AA4GxmVlQozBBWFqxHQ+fwP/F+y9jNRgdN05f9l/X1Oq/k2/o/5z6nv9RmSX/xaXl/hvZOt7EGl+mdi43YrLLsRpGLN586cV/YNz9B/kGaiwDQ3x+vYCNq98xYTGJ/xvOPsaqkRS86vgdUIL4H1lUL8IAiihxSZlfDt5BYAlsGsjBajqG/wPiMzMY7L1CdnqFJ2BVRC4GJQIJWYX/ISm5IQySCsrfJ67cjVUhuXjOtpP/RSWkf4PDn09Q+O+KozexKiQHrzhy47+qtgEikvXM7R4mFtViVUwqnrvj9H9Qrrf3CdkKNhwEQGkf5B1rV9//i/ZexKqRWAxyqLmTx3mo0QgQnVvP5+Adso1PQOgfKPywaSYGF7dNAeWB21BjMYGtm9/h6OwyrJqJwaCcbOsZuB9qHCYIjM0okFNW+7/j+lusBuDD26+9+S+rpPrfPza1GGocdqBjYv3EMzQOw5KFey781ze3AWMQG1kOZLhHSOx/kF6oMbhBVFaxvI6pxVOQT6KySv/nNfT99wyL/w+KH5eAyBWugZErgUX5P5AYSA4ULCCXgwyPySlWhBqDCuzr61kC4rNSkSsRkFdBaRlUAIIMDkkttIdKMYDYIDGQHCjM8QYLyHBFFc0vIuJS/7l5+f6Bszc1QUhCdgqo3ACVHxHpRf+tnD3PQqWoA0DBAqp3QYZLySn+945I7oJKUQ+AggXkcpDhofX1bFDhoQAYGADLMuz3NxXYUwAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, primitive):
        primitive = clean_primitive(primitive)
        cut_surfaces = get_cut_planes(primitive)
        symmetry_surfaces = get_symmetry_planes(primitive)
        octant = Rhino.Geometry.Mesh.CreateBooleanDifference({primitive}, symmetry_surfaces)
        quarter = Rhino.Geometry.Mesh.CreateBooleanDifference({primitive}, symmetry_surfaces[1:3])
        
        return primitive, cut_surfaces, symmetry_surfaces, octant, quarter
