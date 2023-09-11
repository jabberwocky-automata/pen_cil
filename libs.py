####

import random
import numpy as np
from PIL import Image, ImageDraw

##

def construct_lineDrawingImgFromImg(img, base_color, line_params, _sort):
	print('constructing line-img...')
	l_p = line_params

	gradations = len(l_p)

	img = img.convert('L') if not img.mode == 'L' else img

	# store unique-values from the original-img w/ their counts in a dictionary
	img_data = unique_sorted(img, _sort)
	if gradations < len(img_data['uniques']):
		img = img.quantize(colors=gradations)
		img_data = unique_sorted(img, _sort)

	oput_size = img.size

	iput_arr = np.array(img)
	oput_transparentImg = Image.new('RGBA', oput_size, (0,0,0,0))

	uniques = img_data['uniques']
	lu = len(uniques)
	for u, unique in enumerate(uniques):
		print(f'\tconstructing img for unique-color:{u+1} of {lu}...',end='\r')
		line_img = Image.new('RGBA', oput_size, (0,0,0,0))

		line_param = l_p[u]
		# construct line-pattern-img
		if 'hatch' in line_param['pattern']:
			line_img = gen_hatchImg(line_param, oput_size)
		elif line_param['pattern'] == 'circles':
			line_img = gen_circleImg(line_param, oput_size)
		else:
			print()
			exit(print('unsupported pattern-type...'))

		darkness = line_param['darkness']
		# recolorize line-img w/ preset shades
		line_img = redarken(line_img, darkness)

		threshold = line_param['threshold']
		# replace pixels above threshold of randomly_generated reals w/ base_color
		if threshold > 0:
			line_img = remove_randompixelsBelowThreshold(line_img, threshold, base_color)

		# mask line-img w/ pixels in the original-img == unique, & paste to the oput-img
		mask = np.zeros((*iput_arr.shape,4), dtype='uint8')
		mask[iput_arr == unique] = [0,0,0,255]
		mask = Image.fromarray(mask)

		tint = line_param['tint']
		line_img = tint_lineImg(tint, line_img)

		oput_transparentImg.paste(line_img, mask=mask)

	oput_img = Image.new('RGBA', oput_size, base_color)
	oput_img.paste(oput_transparentImg, mask=oput_transparentImg)

	print()

	return oput_img

def tint_lineImg(tint, line_img):
	if not tint['flag']:
		return line_img
	oput_size = line_img.size
	tint_img = Image.new('RGBA', oput_size, tint['color'])
	blend_img = Image.new('RGBA', oput_size, (0,0,0,0))
	blend_img.paste(tint_img, mask=line_img)
	func_str = tint['blend']['mode']
	times = tint['blend']['times']
	opacity = tint['blend']['opacity']
	line_img = blend(line_img, blend_img, func_str=func_str, times=times, opacity=opacity)

	return line_img


def gen_hatchImg(line_param, oput_size):
	lp = line_param

	width, height = oput_size
	width *= 2
	height *= 2
	line_img = Image.new('RGBA', (width, height), (0,0,0,0))
	draw = ImageDraw.Draw(line_img)

	pattern = lp['pattern']
	spacing = lp['spacing']
	start = lp['start']
	amplitude = lp['sine']['amplitude']
	frequency = lp['sine']['frequency']
	rot = lp['rot']

	y_offsets = range(start, height, spacing)
	num_waves = len(y_offsets)

	x_values = np.linspace(0, width, num=width)

	for i in range(num_waves):
		phase = 0

		amplitude_variations = [random.uniform(-1, 1) for _ in range(len(x_values))]

		amplitudes = [amplitude + var for var in amplitude_variations]

		y_values = [amplitude * np.sin(2 * np.pi * frequency * x + phase) + y_offsets[i]
                    for x, amplitude in zip(x_values, amplitudes)]

		for j in range(1, len(x_values)):
			x1, y1 = x_values[j - 1], y_values[j - 1]
			x2, y2 = x_values[j], y_values[j]
			draw.line([(x1, y1), (x2, y2)], fill=(0,0,0,255), width=2)

	if not rot == 0:
		line_img = line_img.rotate(rot)

	if pattern == 'crosshatch':
		ch = line_img.copy().rotate(rot+90)
		line_img.paste(ch,mask=ch)

	w2, h2 = oput_size[0]//2, oput_size[1]//2
	line_img = line_img.crop((w2, h2, w2*3, h2*3))

	return line_img

def gen_circleImg(line_param, oput_size):
	spacing = line_param['spacing']
	spacing = int(squeeze_interval(spacing, 0, 12, 216, 27))
	circle_img = Image.new('RGBA', oput_size, (0,0,0,0))
	draw = ImageDraw.Draw(circle_img)

	radius = min(oput_size) // spacing

	num_circles_x = oput_size[0] // (2 * radius)
	num_circles_y = oput_size[1] // (2 * radius)

	spacing_x = oput_size[0] / (num_circles_x * 2)
	spacing_y = oput_size[1] / (num_circles_y * 2)

	for i in range(num_circles_x*2):
		for j in range(num_circles_y*2):
			x = (2 * i + 1) * spacing_x / 2
			y = (2 * j + 1) * spacing_y / 2

			draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], outline=(0, 0, 0, 255))

	return circle_img

def remove_randompixelsBelowThreshold(img, threshold, recolor):
	arr = np.array(img)

	b = np.random.rand(*arr.shape)

	mask = np.all(b < threshold, axis=-1)

	arr[mask] = recolor

	img = Image.fromarray(arr.astype('uint8'))

	return img

def squeeze_interval(value, old_min, old_max, new_min, new_max):
	value = max(min(value, old_max), old_min)
	ratio = (value - old_min) / (old_max - old_min)
	squeezed_value = new_min + (new_max - new_min) * ratio

	return squeezed_value

def redarken(img, darkness_level):
	arr = np.array(img)

	darkness_colors = darknesses(darkness_level)
	ldc = len(darkness_colors)

	random_integers = np.random.randint(0, ldc-1, size=(1080, 1080))
	non_zero_mask = np.any(arr != [0,0,0,0], axis=-1)

	darkened_arr = np.zeros_like(arr)
	for i in range(ldc-1):
		condition = (random_integers == i) & non_zero_mask
		darkened_arr[condition] = darkness_colors[i]

	return Image.fromarray(darkened_arr)

def darknesses(level):
	if level == 12:
		return [(0,0,0,255)]*2
	if level == 11:
		return [(3, 3, 3, 255), (80, 80, 80, 255), (86, 86, 86, 255), (92, 92, 92, 255), (104, 104, 104, 255), (113, 113, 113, 255), (73, 73, 73, 255), (27, 27, 27, 255), (34, 34, 34, 255), (61, 61, 61, 255)]
	if level == 10:
		return [(19, 19, 19, 255), (26, 26, 26, 255), (93, 93, 93, 255), (102, 102, 102, 255), (120, 120, 120, 255), (128, 128, 128, 255), (140, 140, 140, 255), (82, 82, 82, 255), (37, 37, 37, 255), (71, 71, 71, 255)]
	if level == 9:
		return [(20, 20, 20, 255), (26, 26, 26, 255), (34, 34, 34, 255), (97, 97, 97, 255), (105, 105, 105, 255), (115, 115, 115, 255), (123, 123, 123, 255), (135, 135, 135, 255), (85, 85, 85, 255), (40, 40, 40, 255)]
	if level == 8:
		return [(22, 22, 22, 255), (28, 28, 28, 255), (35, 35, 35, 255), (93, 93, 93, 255), (123, 123, 123, 255), (136, 136, 136, 255), (142, 142, 142, 255), (130, 130, 130, 255), (105, 105, 105, 255), (49, 49, 49, 255)]
	if level == 7:
		return [(23, 23, 23, 255), (29, 29, 29, 255), (35, 35, 35, 255), (112, 112, 112, 255), (122, 122, 122, 255), (143, 143, 143, 255), (102, 102, 102, 255), (41, 41, 41, 255), (72, 72, 72, 255), (92, 92, 92, 255)]
	if level == 6:
		return [(27, 27, 27, 255), (37, 37, 37, 255), (49, 49, 49, 255), (128, 128, 128, 255), (147, 147, 147, 255), (116, 116, 116, 255), (134, 134, 134, 255), (140, 140, 140, 255), (57, 57, 57, 255), (71, 71, 71, 255)]
	if level == 5:
		return [(44, 44, 44, 255), (51, 51, 51, 255), (57, 57, 57, 255), (63, 63, 63, 255), (139, 139, 139, 255), (145, 145, 145, 255), (154, 154, 154, 255), (165, 165, 165, 255), (130, 130, 130, 255), (120, 120, 120, 255)]
	if level == 4:
		return [(67, 67, 67, 255), (73, 73, 73, 255), (79, 79, 79, 255), (162, 162, 162, 255), (168, 168, 168, 255), (181, 181, 181, 255), (189, 189, 189, 255), (91, 91, 91, 255), (156, 156, 156, 255), (174, 174, 174, 255)]
	if level == 3:
		return [(93, 93, 93, 255), (99, 99, 99, 255), (112, 112, 112, 255), (207, 207, 207, 255), (215, 215, 215, 255), (233, 233, 233, 255), (120, 120, 120, 255), (130, 130, 130, 255), (181, 181, 181, 255), (138, 138, 138, 255)]
	if level == 2:
		return [(153, 153, 153, 255), (160, 160, 160, 255), (168, 168, 168, 255), (239, 239, 239, 255), (227, 227, 227, 255), (218, 218, 218, 255), (174, 174, 174, 255), (180, 180, 180, 255), (205, 205, 205, 255), \
                (187, 187, 187, 255)]
	if level == 1:
		return [(164, 164, 164, 255), (183, 183, 183, 255), (191, 191, 191, 255), (246, 246, 246, 255), (240, 240, 240, 255), (233, 233, 233, 255), (202, 202, 202, 255), (209, 209, 209, 255), (221, 221, 221, 255), \
                (188, 188, 188, 255)]
	if level == 0:
		return [(197, 197, 197, 255), (204, 204, 204, 255), (248, 248, 248, 255), (211, 211, 211, 255), (242, 242, 242, 255), (217, 217, 217, 255), (235, 235, 235, 255), (224, 224, 224, 255), (207, 207, 207, 255), \
                (214, 214, 214, 255)]

def unique_sorted(data, _sort={'by_uniques':True,'low_toHigh':True}, rgba=False):
	# data can be arr or img
	# _order can be 'low' or 'h
	# if by_uniques == False, then the indices are sorted by counts
	# if not rgba (shape:(y,x,4)), then L (shape:(y,x))

	dir = 1 if _sort['low_toHigh'] == True else -1

	if not type(data) == np.array:
		data = np.array(data)

	if rgba:
		if len(data.shape) == 3:
			data = data.reshape(-1, 4)
	else:
		if len(data.shape) == 2:
			data = data.reshape(-1,)

	if not 'algo' in _sort.keys():
		_sort['algo'] = 'mergesort'

	uniques, counts = np.unique(data, axis = 0, return_counts=True)
	_uniques = np.sum(uniques,axis=1) if rgba else uniques
	sorted_indices = np.argsort(_uniques, kind=_sort['algo'])[::dir] if _sort['by_uniques'] else np.argsort(counts, kind=_sort['algo'])[::dir]
	uniques_sorted = uniques[sorted_indices]
	counts_sorted = counts[sorted_indices]

	return {'uniques':uniques_sorted,'counts':counts_sorted}

def blend(bg, fg, coords=(0,0), func_str='hard_light', times=1, opacity=1):
	fg_bg = Image.new('RGBA',bg.size)
	fg_bg.paste(fg, coords, mask=fg)
	fg = fg_bg
	func_library = {'soft_light':bm.soft_light,'lighten_only':bm.lighten_only,
					'dodge':bm.dodge,'addition':bm.addition,
					'darken_only':bm.darken_only,'multiply':bm.multiply,
					'hard_light':bm.hard_light,'difference':bm.difference,
					'subtract':bm.subtract,'grain_extract':bm.grain_extract,
					'grain_merge':bm.grain_merge,'divide':bm.divide,
					'overlay':bm.overlay,'normal':bm.normal}

	def convert(img):
		img = np.array(img)
		img = img.astype(float)

		return img

	bg = convert(bg)
	fg = convert(fg)

	for time in range(times):
		bg = func_library[func_str](bg, fg, opacity=opacity)
	bg = np.uint8(bg)
	bg = Image.fromarray(bg)
