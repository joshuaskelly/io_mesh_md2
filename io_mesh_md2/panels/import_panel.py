import bpy


class MD2_PT_import_settings(bpy.types.Panel):
    bl_idname = 'MD2_PT_import_settings'
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = 'Materials'
    bl_parent_id = 'FILE_PT_operator'

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        print(operator.bl_idname)

        return operator.bl_idname == "IMPORT_MESH_OT_md2"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        sublayout = layout.column(heading="")
        sublayout.prop(operator, 'use_unfiltered_textures', text="Unfiltered Textures")


def register():
    bpy.utils.register_class(MD2_PT_import_settings)


def unregister():
    bpy.utils.unregister_class(MD2_PT_import_settings)
