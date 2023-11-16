from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import ghpythonlib.parallel
import ghpythonlib.treehelpers as th

def get_bounding_box(unit_cell):
        precise_box = False
        unit_cell_bounds = unit_cell[0].GetBoundingBox(precise_box)
        for line in unit_cell:
            box = line.GetBoundingBox(precise_box)
            unit_cell_bounds = Rhino.Geometry.BoundingBox.Union(unit_cell_bounds, box)
        return unit_cell_bounds

def check_inclusion(lattice_curve, mesh):
    lattice_curve.Domain = Rhino.Geometry.Interval(0,1)
    midpoint = lattice_curve.PointAt(0.5)
    keep = mesh.IsPointInside(midpoint, 0.001, True)
    return keep

def check_curve_parallel(curve):
    curve = Rhino.Geometry.Curve.TryGetPolyline(curve)[1]
    curve = Rhino.Geometry.PolylineCurve(curve)
    intersection_points = Rhino.Geometry.Intersect.Intersection.MeshPolyline(primitive_global, curve)[0]
    if intersection_points:
        curve_params = []
        for point in intersection_points:
            curve_params.append(curve.ClosestPoint(point)[1])
        split_curve = curve.Split(curve_params)
        for section in split_curve:
            if (check_inclusion(section, primitive_global)):
                lattice_trimmed.append(section)
    else:
        if (check_inclusion(curve, primitive_global)):
            lattice_trimmed.append(curve)

def populate_lattice_parallel(voxels):
    lattice_structure = []
    for curve in unit_cell_global:
        mapped = ghcomp.BoxMapping(curve, unit_cell_bounds, voxels)[0]
        lattice_structure.append(mapped)
    return lattice_structure

def populate_connectivity_parallel(voxels):
    connect = ghcomp.BoxMapping(connectivity_global, unit_cell_bounds, voxels)[0]
    return connect

def populate_skin_parallel(voxels):
    connect = ghcomp.BoxMapping(connectivity_global, unit_cell_bounds, voxels)[0]
    # curves = Rhino.Geometry.Intersect.Intersection.MeshMeshAccurate(connect, primitive,  Rhino.RhinoMath.SqrtEpsilon*10)
    curves = ghcomp.MeshXMesh(primitive_global, connect)
    return curves


class UniformLattice(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Populate - Lattice (Uniform)", "UniformLattice", """Population for a uniform strut lattice""", "LatticeTools", "Lattice")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("a9dc427c-2a24-4b06-82f9-19d7fd58c75e")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "core_voxels", "core_voxels", "Voxels to populate with unit cell only")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "boundary_voxels", "boundary_voxels", "Voxels to populate with unit cell and get connectivity")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "unit_cell", "unit_cell", "Lines and curves making up the repeat unit")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "connectivity", "connectivity", "Unit cell connectivity")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "primitive", "primitive", "Trimming boundary")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "lattice_core", "lattice_core", "Core voxels populated with unit cells")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "lattice_boundary", "lattice_boundary", "Boundary voxels populated with unit cells")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "lattice_trimmed", "lattice_trimmed", "Trimmed lattice within primitive")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "lattice_boundary_connect", "lattice_boundary_connect", "Boundary voxels populated with connectivity")
        self.Params.Output.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "lattice_skin", "lattice_skin", "Net skin of the lattice")
        self.Params.Output.Add(p)
        
    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        result = self.RunScript(p0, p1, p2, p3, p4)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)
                self.marshal.SetOutput(result[2], DA, 2, True)
                self.marshal.SetOutput(result[3], DA, 3, True)
                self.marshal.SetOutput(result[4], DA, 4, True)
        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAS8SURBVEhLrVX7T5NnFC4ttNAbIDTQVsootKW0pdgrLQOj7GoGWUQuNSgjblUh4ChbpHKpCIzFwYhu3DYXEoXpfgDkoqKOYNwfsMtvS7ZFh2QK49KPQgRa2DmldB1BRtie5Eme933OOe/3vVfSDkAFpgPNfgG0Rr+AoPOgDwEjgP8JPHqk8JvI5LcdoqO1E+qzN54l1z9wIlFLTBfGIwyHp5h8aTPEBq6n7BQUyiu81DxCX//tSsrH360ZPxpzxeXZiATzZw75e5fnRabaP5MbHjrRwxh+Wv5TSMr0ZG8LMlOgaJaZW1c0Nbec+uo7S9rKPgcjUjwIXqI4zzYnOWqbAy1j8EU3tdab83rb8LKucsglN19aDeKJe8Dzw0JbIogn6tbXjriUZVeXecbcFWPDmCskVncfLEzi+AzAwT70MIb38hFXUkmXS2+7s8p8SdEE3lbw1ynMbc8TS7pWWNGyFV3NkEOYWeZiRivusWOUA0yBfCSh4BMi4Z1mAjX2Qdx9YWa5U1MzvMiKlq9hrvxUmwMmIt9T1As//oGC33BO/w9yDVlOqIl/uY4QkbYkufbearji4EQAY8+w4nTrtDinyk4LiWjZIDU4vF1iqrPHH2uwU4M5Hb5eXNa5RdnJz2f8GXsGw5Xp41gL/qjOUx72Y2rOr6qzvXaQ7wOLNFWDBPQ9cpt/I2zTGniBsVpr3wJIC/BMUvk1J9d4+A/Q7gUnS0y2JzEZJU9ACyiBrE5j48O1UImxH00fvHCAUKmhF3MoQewuaEYL0k84xbnVk6CN6EepLF/PcFSv4QBRrFj1D8b6sVUKjXER2mKgEPuBUp8BpEAcxE1yILMCc9hxmp+wzdn36rjS0o0zkk+i0FmHkuvGnLLCpnlMTizuIAx1o8uoN1Nt7bOrrf32rTzYrkuYi1r2bguB25dMYxWSyLSgYvcAJz4l8AvlRZ2zGIx6M9UVvTBAn30rzwA5yuKvpkU5lc/jC5oWoA0D0AvhL0gH1OXXJzlJbzwGHcYSqr7H3/Wns89h24ciLIRfCFri621MEStO8yO0+ThFSR/emALtPg/02OzKqei3Sn8HHbOrRYZY9yIHsr6ApiA6o3Tcs8h73QE8o3eblgFP45bjp5nwj3yxzTbNe4xbG2QR8IzG2jsXmZb3s9tEMLjiDv2FUWd44sEJf0bogOxk2yzM5SKVzblCDeF0UoMj2lB7Dxqb8yUtOPLSBmNzqwj5qfbJAGbYbTysWIsdo8Ap9kLATTNNb3Xsd0P+ftMzqInr4wvKm/Dli+7LTiBf01YNz+NFxhRI77IEin5mlOy29PhFIqGgiUDt7gNPmGFx4sXIipIvKUqvOLEG1HrdU/SfYEbFX9bZ7jqTLD0LeAXjQxMSpxkFiwzcfF2T0cMYvNpVH1x3YC5TkNAC3gtBgTehRwZXrrZ6eMX9mFTdmmXwxUPgKX0GkOMjpLUOzOtsI4sYl1jUTsATOwAefsy/wd+wd//xR94ns/GBS2Q6T+BzqTC3zovg+cQ+9HBBuSm5MCjliCd5x6DAo1LJTc3+JTbHOq0quzaDJx65z9I9K8qumOUas54GceOuQmzoesruQQFKyYH0Y2QarQR0CpCNxvYgkf4CQTF57xDRx98AAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, core_voxels, boundary_voxels, unit_cell, connectivity, primitive):
        global unit_cell_bounds
        global unit_cell_global
        global connectivity_global
        global primitive_global
        global lattice_trimmed

        unit_cell_global = unit_cell
        connectivity_global = connectivity
        primitive_global = primitive
        unit_cell_bounds = get_bounding_box(unit_cell)
        unit_cell = Rhino.Geometry.Curve.JoinCurves(unit_cell)
        if core_voxels:
            lattice_core = ghpythonlib.parallel.run(populate_lattice_parallel, core_voxels, True)
        else:
            lattice_core = []
        if boundary_voxels:
            lattice_boundary = ghpythonlib.parallel.run(populate_lattice_parallel, boundary_voxels, True)
            lattice_boundary_connect = ghpythonlib.parallel.run(populate_connectivity_parallel, boundary_voxels, True)
            lattice_skin = ghpythonlib.parallel.run(populate_skin_parallel, boundary_voxels, True)
        else:
            lattice_boundary = []
            lattice_boundary_connect = []
            lattice_skin = []

        lattice_trimmed = []
        lattice_combined = list(lattice_core) + list(lattice_boundary)
        valid_curves = list(filter(None, lattice_combined))
        ghpythonlib.parallel.run(check_curve_parallel, valid_curves, False)

        return lattice_core, lattice_boundary, lattice_trimmed, lattice_boundary_connect, lattice_skin