from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os

def write_lines(file, content):
    for line in content:
        file.write(line)
    file.close()

class Logger(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "Logging - Write", "Logger", """Writes text input to a file.""", "LatticeTools", "Log")
        return instance
    
    def get_ComponentGuid(self):
        return System.Guid("6d167ea1-8f3c-4773-b48e-50d49cfbecbb")
    
    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True
    
    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "file_path", "file_path", "Path to the file to write")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "content", "content", "Content to write to the file")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)
        
        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "write_file", "write_file", "Write the file?")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)
        
    
    def RegisterOutputParams(self, pManager):
        pass    
    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        
    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAHYcAAB2HAY/l8WUAAAK+SURBVEhLpZZdSFNhHMYHXXSh1EUQdWVE2Me0pX0ILUqLTKGPhaJkUlKxnPYhQ6ddNE1FBNOKIFNBsDRsWjbd1rQtt1Fz0605J34SFEGEJhSRRaBP27tz9Mwdj0d94Hd33t+z/f8vnCPwJeOyNHX/gYOfxIdjZ4/FJ2K5xB0/gc0bN/3NjTo0dVskHg4LDT1LxL6oVKo1Ebv3THdabHAMfVwZA6MYbnyFibSbmDh3A5aE89+2hKxLIQVpF69kX5cr2A/yYXAc3ToTXhqsGG7WBpSEha6XCCTJKVXl9x6yH+ZBp1esMfcSFpb4xhVQYPeM401PPy+MPU5M9Crgsb0lYrYShTDGE1Cgf+9EjUq7JHUtHfhsuQY4TmHGIYHb0BFU0lV2/9eGtSGxyx6Rc2gMP1wFRE4z03cGri71fEmL5p9w246TZMnMApNjECq9ZVFa9d34as0JkDNLrIZ2NDxtnQ0P25pI5L7wLeCS0/SrL2C7MPIPpfaHz4jYxrIQd3s6svKVCN8lnKbU/iy1ZOZCF4OWS/MKuQsWXlOD9QO+2+WsUhqmXFZQjAhR1BSl9oerwKZrw6RGxir2wZTnKMuhM9sQHb3vC6X2h2tE7voyjNYXs5Yw5bkllTA7PMTBWcDEZbcTOc2kJpNVXvG4wfvPx+bOcRYwr6mxqTaggC4Z7PDLryqKUFHbSJ7VWvqWV/D8tRmVcilGGHJHTTEelRVBll+IrFslqG5qm/sxvAto1F0m7BTtRXVBFp5U3EGhsoiMw4eitApGmyvgeSa8lny37hnSZXJIc5Xk6uV5l1j6oBYNL3SwukeCpEw4C+hrqn/nRLPWCFPfQJBgKXiNaDUEFaz6lclA3WmC+EjcAKX2h3rp/17VS99Lj3c3kuRUXMrMTqLU8yGfLTHiFX+2HI1PQKQo6ufppJQaSklFIPgPELblPd+Nc7MAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, file_path, content, write_file):
        ghdoc = scriptcontext.doc

        if write_file and file_path:
            # working_dir = os.path.dirname(os.path.realpath(ghdoc.Path))
            # file_path = os.path.join(working_dir, file_path)

            if (os.path.exists(file_path)):
                file = open(file_path, "a")
                if (os.stat(file_path).st_size != 0):
                    file.write("," + "\n")           
                write_lines(file, content)

            else:
                file = open(file_path, "w")
                write_lines(file, content)