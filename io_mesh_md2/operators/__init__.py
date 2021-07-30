from io_mesh_md2.operators import export_md2
from io_mesh_md2.operators import import_md2

modules = (
    export_md2,
    import_md2,
)

def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()