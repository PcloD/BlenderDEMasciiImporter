import bpy, bmesh
import os

from bpy.props import *
from bpy_extras import object_utils

print ('Changing active folder from ' + os.getcwd() + ' to ' + bpy.path.abspath("//"))
os.chdir(bpy.path.abspath("//"))

# USER PARAMETERS
FOLDERNAME = 'FILES'
RESCALE = 0.01

n = 0

ncols = 0
nrows = 0
xllcorner = 0
yllcorner = 0
cellsize = 0
NODATA_value = 0

filenames = []

for file in os.listdir('./'+FOLDERNAME):
    if file.endswith(".asc"):
        filenames.append('./'+FOLDERNAME+'/'+file)

for fn in filenames:
    
    l = 0
    x = 0
    y = 0
    
    vertices = []
    faces = []

    with open(fn) as lines:
        for line in lines:
            l = l + 1
            # Acquire parameters
            if l < 7:
                s = line.split(' ')
                if s[0] == "ncols":
                    ncols = int(s[1])
                elif s[0] == "nrows":
                    nrows = int(s[1])
                elif s[0] == "xllcorner":
                    xllcorner = float(s[1])
                elif s[0] == "yllcorner":
                    yllcorner = float(s[1])
                elif s[0] == "cellsize":
                    cellsize = float(s[1])
                elif s[0] == "NODATA_value":
                    NODATA_value = float(s[1])
                continue
            # Generate vertices
            v = []
            for heightstring in line.strip().split(' '):
                H = float(heightstring)
                v = [float(x), float(y), H]
                vertices.append(v)
                x = x + cellsize
            x = 0
            y = y + cellsize

    # Generate grid faces
    for i in range (0, ncols-1):
        for j in range (0, nrows-1):
            f = [i+j*ncols, i+j*ncols+1, i+ncols+j*ncols+1, i+ncols+j*ncols]
            if vertices[f[0]][2] == NODATA_value or vertices[f[1]][2] == NODATA_value or vertices[f[2]][2] == NODATA_value or vertices[f[3]][2] == NODATA_value :
                continue
            else:
                faces.append(f)

    mesh = bpy.data.meshes.new(name='Terrain'+str(n))
    n = n+1
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    object_utils.object_data_add(bpy.context, mesh)

    # Now hunt NODATA verices in the mesh

    # deselect all in the mesh
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")

    #back to object mode
    bpy.ops.object.mode_set(mode="OBJECT")
    obj = bpy.context.active_object 

    # force vertex selection mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False) 

    # conditional selection
    for v in obj.data.vertices:
        if (v.co[2] == NODATA_value):
            v.select = True
        else:
            v.select = False

    # RESCALE
    bpy.ops.transform.resize(value=(RESCALE, RESCALE, RESCALE), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.transform.translate(value=(xllcorner * RESCALE, yllcorner * RESCALE, 0), constraint_axis=(True, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

            
    bpy.ops.object.mode_set(mode="EDIT")
    # DELETE THOSE VERTICES
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode="OBJECT")