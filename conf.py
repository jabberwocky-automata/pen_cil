####

from PIL import Image
import libs

####

img = Image.open('a.png')

# sort by_uniques (ie, color-value), else by counts; sorts in direction of low_toHigh, else from high to low
# patterns: hatch, crosshatch, circles
# darkness: 0-12, 12 == pure-black
# threshold --> replaces pencil w/ base_color below threshold-value; 0 results in no pixels being replaced
base_color = (255,255,225,255)
_sort={'by_uniques':False,'low_toHigh':False}
line_params = [{'pattern':'circles','spacing':10,'start':0,'darkness':11,'sine':{'amplitude':2,'frequency':.08},'threshold':.3,'rot':60,
                'tint':{'flag':False,'color':(0,0,255,255),'blend':{'mode':'soft_light','times':1,'opacity':1}}},
               {'pattern':'crosshatch','spacing':8,'start':0,'darkness':11,'sine':{'amplitude':2,'frequency':.00},'threshold':.3,'rot':0,
                'tint':{'flag':False,'color':(255,255,0,255),'blend':{'mode':'soft_light','times':1,'opacity':1}}},
               {'pattern':'crosshatch','spacing':1,'start':0,'darkness':3,'sine':{'amplitude':2,'frequency':.02},'threshold':.6,'rot':0,
                'tint':{'flag':False,'color':(0,0,255,255),'blend':{'mode':'soft_light','times':1,'opacity':1}}},
               {'pattern':'hatch','spacing':8,'start':0,'darkness':11,'sine':{'amplitude':2,'frequency':.03},'threshold':.3,'rot':45,
                'tint':{'flag':False,'color':(255,255,0,255),'blend':{'mode':'soft_light','times':1,'opacity':1}}},
               {'pattern':'crosshatch','spacing':1,'start':0,'darkness':3,'sine':{'amplitude':2,'frequency':.02},'threshold':.6,'rot':0,
                'tint':{'flag':False,'color':(0,0,255,255),'blend':{'mode':'soft_light','times':1,'opacity':1}}}]

line_img = libs.construct_lineDrawingImgFromImg(img, base_color, line_params, _sort)
line_img.save('line_img.png')
