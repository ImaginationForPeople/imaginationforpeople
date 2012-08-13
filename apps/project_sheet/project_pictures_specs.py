#-- encoding: utf-8 --
#
# This file is part of I4P.
#
# I4P is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# I4P is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
# 
# You should have received a copy of the GNU Affero Public License
# along with I4P.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Specification for image manipulation throw imagekit
"""
from imagekit.specs import ImageSpec
from imagekit import processors
from imagekit.processors import ImageProcessor
from imagekit.lib import ImageColor, Image


class Center(ImageProcessor):
    """
    Generic image centering processor
    """
    width = None
    height = None
    background_color = '#000000'

    @classmethod
    def process(cls, img, fmt, obj):
        if cls.width and cls.height:
            background_color = ImageColor.getrgb(cls.background_color)
            #FIXME : Image is not imported but it never raises exception so ...
            bg_picture = Image.new("RGB", (cls.width, cls.height), background_color)

            ## paste it
            bg_w, bg_h = bg_picture.size
            img_w, img_h = img.size
            coord_x, coord_y = (bg_w - img_w) / 2, (bg_h - img_h) / 2

            bg_picture.paste(img, (coord_x, coord_y, coord_x + img_w, coord_y + img_h))
            
        return bg_picture, fmt


class AlphaGradient(ImageProcessor):
    """
    Make an alpha to dark gradient
    """
    @classmethod
    def process(cls, img, fmt, obj):
        if img.mode == 'RGBA':
            img = img.convert('RGB')
            
        width, height = img.size
        # create a vertical gradient...
        for y in range(0, height):

            for x in range(0, 255):
                darken = x / 255.0

                # Left one                
                r, g, b = img.getpixel((x, y))
                new_pix = (int(r*darken), int(g*darken), int(b*darken))
                img.putpixel((x, y), new_pix)

                # Right one
                r, g, b = img.getpixel((width-1-x, y))
                new_pix = (int(r*darken), int(g*darken), int(b*darken))
                img.putpixel((width-1-x, y), new_pix)
                

        return img, fmt

class ResizeThumb(processors.Resize):
    """
    Resizing processor providing media thumbnail
    """
    width = 95
    height = 65
    crop = True

class ResizeIDCard(processors.Resize):
    """
    Resizing processor providing profile ID card
    """
    width = 137
    height = 71
    crop = True

class ResizeDisplay(processors.Resize):
    """
    Resizing processor for media gallery
    """
    width = 700


class ResizeBig169(processors.Resize):
    """
    Resizing processor providing a big 16/9
    """
    width = 762
    height = 253
    crop = True
    upscale = True

class ResizeSmall169(processors.Resize):
    """
    Resizing processor providing a small 16/9
    """
    width = 290
    height = 90
    crop = True   
    upscale = True

class PreResizeMosaic(processors.Resize):
    """
    Resizing processor for mosaic
    """
    width = 200

class CenterMosaic(processors.Resize):
    # FIXME : semantic ? Center or Resize ?
    width = 40
    height = 40
    crop = True


class CenterDisplay(Center):
    """
    Image centering processor for media gallery
    """
    width = 700
    height = 460


class EnhanceThumb(processors.Adjustment):
    """
    Adjustment processor to enhance the image at small sizes
    """
    contrast = 1.2
    sharpness = 1.1

class Thumbnail(ImageSpec):
    access_as = 'thumbnail_image'
    pre_cache = True
    processors = [ResizeThumb, EnhanceThumb]

class Display(ImageSpec):
    access_as = 'display'
    increment_count = True
    processors = [ResizeDisplay, CenterDisplay]

class MosaicTile(ImageSpec):
    """
    For the Homepage
    """
    access_as = 'mosaic_tile'
    processors = [PreResizeMosaic, CenterMosaic]

class IDCard(ImageSpec):
    """
    Preview when displaying a project sheet card
    """
    access_as = 'thumbnail_idcard'
    pre_cache = True
    processors = [ResizeIDCard, EnhanceThumb]


class BigPanoHeader(ImageSpec):
    """
    A big 16/9 header
    """
    access_as = 'big_pano_header'
    pre_cache = False
    processors = [ResizeBig169]

class TagHeader(ImageSpec):
    """
    A pano header with gradient alpha
    """
    access_as = 'tag_header'
    pre_cache = False
    processors = [ResizeBig169, AlphaGradient]

class SmallPanoHeader(ImageSpec):
    """
    A small 16/9 header
    """
    access_as = 'small_pano_header'
    pre_cache = False
    processors = [ResizeSmall169]    