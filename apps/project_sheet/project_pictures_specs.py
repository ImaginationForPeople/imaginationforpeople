from imagekit.specs import ImageSpec 
from imagekit import processors 

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
    processors = [ResizeDisplay]

class IDCard(ImageSpec):
    access_as = 'thumbnail_idcard'
    pre_cache = True
    processors = [ResizeIDCard, EnhanceThumb]
