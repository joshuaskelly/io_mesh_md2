bl_info = {
    'name': 'Quake 2 engine MD2 format',
    'author': 'Joshua Skelton',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'File > Import-Export',
    'description': 'Load a Quake 2 engine MD2 file.',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    'category': 'Import-Export'}

__version__ = '.'.join(map(str, bl_info['version']))


if 'reload' in locals():
    import importlib as il
    il.reload(reload)
    reload.all()


import io_mesh_md2.reload as reload


def register():
    from io_mesh_md2 import patch
    patch.add_local_modules_to_path()

    from io_mesh_md2 import operators
    operators.register()

    from io_mesh_md2 import panels
    panels.register()


def unregister():
    from io_mesh_md2 import operators
    operators.unregister()

    from io_mesh_md2 import panels
    panels.unregister()


if __name__ == '__main__':
    from .operators import register
    register()
