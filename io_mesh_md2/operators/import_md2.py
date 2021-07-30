import os
import struct

import bpy
import bmesh

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector

from io_mesh_md2.perfmon import PerformanceMonitor
from io_mesh_md2.pcx import Pcx

from vgio.quake2 import md2


performance_monitor = None


class ImportMd2(bpy.types.Operator, ImportHelper):
    """Load a Quake 2 MD2 file"""

    bl_idname = 'import_mesh.md2'
    bl_label = 'Import MD2'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.md2'
    filter_glob: StringProperty(
        default='*.md2',
        options={'HIDDEN'}
    )

    def execute(self, context):
        from . import import_md2
        keywords = self.as_keywords(ignore=("filter_glob",))

        return import_md2.load(self, context, **keywords)


def load(operator,
         context,
         filepath='',
         **kwargs):

    if not md2.is_md2file(filepath):
        operator.report(
            {'ERROR'},
            f'{filepath} is not a recognized MD2 file'
        )

        return {'CANCELLED'}

    global performance_monitor
    performance_monitor = PerformanceMonitor('MD2 Import')
    performance_monitor.push_scope('Starting Import')

    # Open MD2 file
    with md2.Md2.open(filepath) as md2_file, performance_monitor.scope():
        # Create images
        default_material = None
        model_directory = os.path.dirname(filepath)
        for skin in md2_file.skins:
            skin_path = os.path.join(model_directory, os.path.basename(skin.name))
            if not os.path.exists(skin_path):
                performance_monitor.log(f'Could not find skin: {skin.name}')
                continue

            with open(skin_path, 'rb') as skin_file:
                pcx = Pcx.read(skin_file)

            palette = tuple(struct.iter_unpack('<BBB', pcx.palette))
            indexes = struct.unpack(f'<{pcx.width * pcx.height}B', pcx.pixels)
            pixels = [palette[i] for i in indexes]
            pixels = [rgb / 255 for pixel in pixels for rgb in (*pixel, 255)]

            image = bpy.data.images.new(
                skin.name,
                md2_file.skin_width,
                md2_file.skin_height
            )
            image.pixels = pixels

            # Create material
            material = bpy.data.materials.new(name=image.name)
            material.use_nodes = True
            default_material = default_material or material

            bsdf_node = material.node_tree.nodes['Principled BSDF']
            bsdf_node.inputs['Specular'].default_value = 0
            bsdf_node.inputs['Roughness'].default_value = 1

            texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.image = image
            #texture_node.interpolation = 'Closest'

            material.node_tree.links.new(bsdf_node.inputs['Base Color'], texture_node.outputs['Color'])


        # Create mesh
        name = 'MD2'
        ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()

        # Process first frame
        frame: md2.Frame = md2_file.frames[0]

        # Scale matrix
        sx, sy, sz = frame.scale
        scale = Matrix((
            (sx,  0,  0,  0),
            ( 0, sy,  0,  0),
            ( 0,  0, sz,  0),
            ( 0,  0,  0,  1)
        ))

        # Translation matrix
        tx, ty, tz = frame.translate
        translation = Matrix((
            ( 1,  0,  0, tx),
            ( 0,  1,  0, ty),
            ( 0,  0,  1, tz),
            ( 0,  0,  0,  1)
        ))

        transform = translation @ scale

        # Process vertexes
        for vertex in frame.vertexes:
            bm.verts.new(transform @ Vector(vertex))

        bm.verts.ensure_lookup_table()

        # Process triangles
        for triangle in md2_file.triangles:
            bverts = [bm.verts[i] for i in triangle.vertexes]

            try:
                # Create a new face
                bface = bm.faces.new(bverts)

            except ValueError:
                # Sometimes faces are duplicated?
                continue

            # Coordinate normalization matrix
            iw = 1 / md2_file.skin_width
            ih = 1 / md2_file.skin_height
            st_to_uv = Matrix((
                (iw,  0,  0,  0),
                ( 0, ih,  0,  0),
                ( 0,  0,  1,  0),
                ( 0,  0,  0,  1)
            ))

            # Apply UV coordinates
            sts = [md2_file.st_vertexes[i] for i in triangle.st_vertexes]
            sts = [Vector((*st, 0, 1))for st in sts]
            uvs = [(st_to_uv @ st)[:2] for st in sts]
            for uv, loop in zip(uvs, bface.loops):
                loop[uv_layer].uv = uv

            # Apply material
            if default_material:
                ob.data.materials.append(default_material)
                bface.material_index = ob.data.materials[:].index(default_material)

        # Transfer bmesh data to object mesh
        bm.to_mesh(ob.data)
        bm.free()

        # Add object to scene
        bpy.context.scene.collection.objects.link(ob)

    performance_monitor.pop_scope('Import finished.')

    return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportMd2.bl_idname, text='Quake MD2 (.md2)')


def register():
    bpy.utils.register_class(ImportMd2)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportMd2)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)