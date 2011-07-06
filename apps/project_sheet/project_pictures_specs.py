from imagekit.specs import ImageSpec
from imagekit import processors
from imagekit.processors import ImageProcessor
from imagekit.lib import ImageColor

class Center(ImageProcessor):
    width = None
    height = None
    background_color = '#000000'

    @classmethod
    def process(cls, img, fmt, obj):
        if cls.width and cls.height:
            background_color = ImageColor.getrgb(cls.background_color)
            bg_picture = Image.new("RGB", (cls.width, cls.height), background_color)

            ## paste it
            bg_w, bg_h = bg_picture.size
            img_w, img_h = img.size
            xo, yo = (bg_w - img_w) / 2, (bg_h - img_h) / 2

            bg_picture.paste(img, (xo, yo, xo + img_w, yo + img_h))
        return bg_picture, fmt

# first we define our thumbnail resize processor 
class ResizeThumb(processors.Resize):
    width = 95
    height = 65
    crop = True

# first we define our thumbnail resize processor 
class ResizeIDCard(processors.Resize):
    width = 137
    height = 71
    crop = True

# now we define a display size resize processor
class ResizeDisplay(processors.Resize):
    width = 700

class PreResizeMosaic(processors.Resize):
    width = 200

class CenterMosaic(processors.Resize):
    width = 40
    height = 40
    crop = True


class CenterDisplay(Center):
    width = 700
    height = 460


class EnhanceThumb(processors.Adjustment):
    """
    Adjustment processor to enhance the image at small sizes
    """
    contrast = 1.2
    sharpness = 1.1

# now we can define our thumbnail spec 
class Thumbnail(ImageSpec):
    access_as = 'thumbnail_image'
    pre_cache = True
    processors = [ResizeThumb, EnhanceThumb]

# and our display spec
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
