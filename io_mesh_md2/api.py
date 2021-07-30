import os
import struct

from functools import lru_cache

from vgio.quake2.md2 import Md2 as Md2File
from vgio.quake2.md2 import is_md2file

from . import pcx


def _get_skin_path(md2_path, skin_name):
    image_file = os.path.basename(skin_name)
    image_path = os.path.dirname(md2_path)

    return os.path.join(image_path, image_file)


class Skin:
    def __init__(self, md2, skin):
        self._file = md2
        self._skin = skin

    @property
    @lru_cache(maxsize=1)
    def _image(self):
        image_path = _get_skin_path(self._file.filepath, self._skin.name)

        with open(image_path, 'rb') as file:
            image = pcx.Pcx.read(file)

        return image

    @property
    @lru_cache(maxsize=1)
    def width(self):
        return self._image.width

    @property
    @lru_cache(maxsize=1)
    def height(self):
        return self._image.height

    @property
    @lru_cache(maxsize=1)
    def name(self):
        return os.path.basename(self._skin.name)

    @property
    @lru_cache(maxsize=1)
    def pixels(self):
        image = self._image

        format = f'<{len(image.pixels)}B'
        palette = tuple(struct.iter_unpack('<BBB', image.palette))
        palette = [(p[0] / 255, p[1] / 255, p[2] / 255, 1) for p in palette]
        pixels = struct.unpack(format, image.pixels)

        flipped = []
        for row in reversed(range(image.height)):
            flipped += pixels[row * image.width:(row + 1) * image.width]

        pixels = flipped
        pixels = [rgba for index in pixels for rgba in palette[index]]

        return pixels


class Md2:
    def __init__(self, file):
        self._file = Md2File.open(file)
        self._file.close()
        self._file.filepath = file

    @property
    @lru_cache(maxsize=1)
    def skins(self):
        def skin_exists(skin):
            return os.path.exists(_get_skin_path(self._file.filepath, skin.name))

        for skin in filter(skin_exists, self._file.skins):
            yield Skin(self._file, skin)

    def get_frame(self, index):
        frame = self._file.frames[index]
