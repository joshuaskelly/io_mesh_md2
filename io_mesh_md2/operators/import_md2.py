from io_mesh_md2.api import Md2

import bpy
import bmesh

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Matrix, Vector

from io_mesh_md2.perfmon import PerformanceMonitor

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
            vec = Vector(vertex)
            a = transform @ vec
            bm.verts.new(a)

        bm.verts.ensure_lookup_table()

        # Process triangles
        for triangle in md2_file.triangles:
            bverts = [bm.verts[i] for i in triangle.vertexes]

            try:
                bm.faces.new(bverts)
            except ValueError:
                pass

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