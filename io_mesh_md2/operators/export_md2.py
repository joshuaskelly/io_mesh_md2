import bpy

from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper


class ExportMd2(bpy.types.Operator, ExportHelper):
    """Export a Quake 2 MD2 file"""

    bl_idname = 'export_mesh.md2'
    bl_label = 'Export MD2'
    bl_options = {'PRESET'}

    filename_ext = '.md2'
    filter_glob: StringProperty(
        default='*.md2',
        options={'HIDDEN'}
    )

    check_extension = True

    def execute(self, context):
        from . import export_md2
        keywords = self.as_keywords(ignore=("filter_glob",))

        return save(self, context, **keywords)

def save(operator, context, **kwargs):
    raise NotImplementedError


def menu_func_import(self, context):
    ##self.layout.operator(ExportMd2.bl_idname, text='Quake MD2 (.md2)')
    pass


def register():
    bpy.utils.register_class(ExportMd2)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ExportMd2)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)