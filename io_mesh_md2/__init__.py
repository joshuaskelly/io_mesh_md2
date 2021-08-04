bl_info = {
    'name': 'Quake II MD2 format',
    'author': 'Joshua Skelton',
    'version': (1, 0, 0),
    'blender': (2, 90, 0),
    'location': 'File > Import-Export',
    'description': 'MD2 IO meshes, UVs, materials, and textures.',
    'warning': '',
    'wiki_url': 'https://github.com/joshuaskelly/io_mesh_md2/wiki',
    'tracker_url': 'https://github.com/joshuaskelly/io_mesh_md2/issues',
    'support': 'COMMUNITY',
    'category': 'Import-Export'
}

__version__ = '.'.join(map(str, bl_info['version']))


if 'reload' in locals():
    import importlib as il
    il.reload(reload)
    reload.all()


import io_mesh_md2.reload as reload


def register():
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
