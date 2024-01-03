import clr

__version__ = "1.0.0"
file_name = "LatticeTools-" + __version__ + ".ghpy"

clr.CompileModules(file_name, 
                   "LatticeTools.py",
                   "log/log_utils.py", "log/combine_json.py", "log/system_info.py", "log/write_file.py",
                   "prepare/primitive_origin.py",
                   "lattice/populate.py", "lattice/segment.py",
                   "mesh/mesh_points.py", "mesh/mesh_volume.py")