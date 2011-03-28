from imagekit.specs import ImageSpec
from imagekit import processors
from imagekit.processors import ImageProcessor
from imagekit.lib import *

class Center(ImageProcessor):
    width = None
    height = None
    background_color = '#FFFFFF'

    @classmethod
    def process(cls, img, fmt, obj):
        if cls.width and cls.height:
            background_color = ImageColor.getrgb(cls.background_color)
            bg = Image.new("RGB", (cls.width, cls.height), background_color)

            ## paste it
            W, H = bg.size
            w, h = img.size
            xo, yo = (W - w) / 2, (H - h) / 2

            bg.paste(img, (xo, yo, xo + w, yo + h))
        return bg, fmt

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

class CenterDisplay(Center):
    width = 700
    height = 460

# now let's create an adjustment processor to enhance the image at small sizes 
class EnhanceThumb(processors.Adjustment):
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



class IDCard(ImageSpec):
    access_as = 'thumbnail_idcard'
    pre_cache = True
    processors = [ResizeIDCard, EnhanceThumb]
