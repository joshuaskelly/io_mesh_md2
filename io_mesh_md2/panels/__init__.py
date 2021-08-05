from io_mesh_md2.panels import import_panel, material_import_panel


modules = (
    import_panel,
    material_import_panel,
)

def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()