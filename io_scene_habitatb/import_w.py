# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


import bpy, struct, bmesh, mathutils, re, os, glob
import time, struct

from . import const

export_filename = None

######################################################
# IMPORT MAIN FILES
######################################################
def load_w_file(file):
    scn = bpy.context.scene

    mesh_count = struct.unpack('<l', file.read(4))[0]

    main_w = bpy.data.objects.new(bpy.path.basename(export_filename), None )
    bpy.context.scene.objects.link(main_w)

    for mesh in range(mesh_count):

        # get mesh name
        mesh_name = bpy.path.basename(export_filename)
        
        # add a mesh and link it to the scene
        me = bpy.data.meshes.new(mesh_name)
        ob = bpy.data.objects.new(mesh_name, me)
        ob.parent = main_w

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(me)

        # link object to scene
        scn.objects.link(ob)
        scn.objects.active = ob

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # create layers and set names
        uv_layer = bm.loops.layers.uv.new("uv")    
        vc_layer = bm.loops.layers.color.new("color")
        va_layer = bm.loops.layers.color.new("alpha")
        flag_layer = bm.faces.layers.int.new("flags")
        texture_layer = bm.faces.layers.int.new("texture")

        # read bound ball
        bound_ball_center = struct.unpack("<3f", file.read(12))
        bound_ball_radius = struct.unpack("<f", file.read(4))[0]

        # read bbox
        xlo, xhi = struct.unpack("<ff", file.read(8))
        ylo, yhi = struct.unpack("<ff", file.read(8))
        zlo, zhi = struct.unpack("<ff", file.read(8))

        polygon_count = struct.unpack("<h", file.read(2))[0]
        vertex_count = struct.unpack("<h", file.read(2))[0]

        polygons = []

        # read polygons
        for p in range(polygon_count):
            polygon = {}
            polygon["type"] = struct.unpack("<h", file.read(2))[0]
            polygon["texture"] = struct.unpack("<h", file.read(2))[0]
            polygon["vertex_indices"] = struct.unpack("<4h", file.read(8))
            polygon["colors"] = struct.unpack("<4L", file.read(16))
            polygon["uv"] = struct.unpack("<8f", file.read(32))
            polygons.append(polygon)

        vertices = []

        # read vertices
        for v in range(vertex_count):
            vertex = {}
            vertex["position"] = struct.unpack("<3f", file.read(12))
            vertex["normal"] = struct.unpack("<3f", file.read(12))
            vertices.append(vertex)

        
        # add it all to the mesh
        for vert in range(vertex_count):
            location = vertices[vert]["position"]
            bm.verts.new((location[0] * 0.01, location[2] * 0.01, location[1] * -0.01)) # RV units are giant!!

        # ensure lookup table before continuing
        bm.verts.ensure_lookup_table()

        for p in range(polygon_count):
            poly = polygons[p]
            indices = poly["vertex_indices"]
            uvs = poly["uv"]
            colors = poly["colors"]

            # check if the poly is quad
            is_quad = poly["type"] & const.QUAD
            if is_quad and len(set(indices)) == 3:
                is_quad = False
            num_loops = 4 if is_quad else 3


            # check if it's a valid face
            # if len(set(indices)) > 2:
            try:
                face = None
                if is_quad:
                  face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]], bm.verts[indices[3]]))
                else:
                  face = bm.faces.new((bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]])) 
                  
                # set layer properties
                for loop in range(num_loops):
                  # set uvs
                  uv = (uvs[loop * 2], 1 - uvs[loop * 2 + 1])
                  face.loops[loop][uv_layer].uv = uv
                  
                  # set colors
                  color_b = float(colors[0]) / 255
                  color_g = float(colors[1]) / 255
                  color_r = float(colors[2]) / 255
                  color_a = 1.0 - (float(colors[3]) / 255)
                  
                  # apply colors and alpha to layers
                  face.loops[loop][vc_layer] = mathutils.Color((color_r, color_g, color_b))
                  face.loops[loop][va_layer] = mathutils.Color((color_a, color_a, color_a))
                  
                # setup face
                face[flag_layer] = poly["type"]
                face[texture_layer] = poly["texture"]
                face.smooth = True
                face.normal_flip()

            except ValueError as e:
                print(e)


        # calculate normals
        bm.normal_update()
        
        # free resources
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bm.to_mesh(me)
        bm.free()

        # set new object type to mesh
        ob.revolt.rv_type = "WORLD"
    

      

######################################################
# IMPORT
######################################################
def load_w(filepath,
             context):

    print("importing w: %r..." % (filepath))

    time1 = time.clock()
    file = open(filepath, 'rb')

    # start reading our pkg file
    load_w_file(file)

    print(" done in %.4f sec." % (time.clock() - time1))
    file.close()


def load(operator,
         context,
         filepath="",
         ):

    global export_filename
    export_filename = filepath
    
    load_w(filepath,
             context,
             )

    return {'FINISHED'}