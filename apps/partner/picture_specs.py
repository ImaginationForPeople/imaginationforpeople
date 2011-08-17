"""
Specification for image manipulation thru imagekit
"""
from imagekit.specs import ImageSpec
from imagekit import processors

class ResizeThumb(processors.Resize):
    """
    Resizing processor for displaying
    """
    width = 400

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

