# FCG 2017.1
# Alexandre Werneck

#### REFERENCES ####

import sys

from PIL import Image, ImageMath
from math import pow, sqrt
import numpy as np
import scipy.misc

from library import *

# Main
if __name__ == '__main__':
	#img = ImageMath.eval("convert(a, 'F')", a=Image.open('bird.jpg'))
	#img = Image.open('bird.jpg')
	#width, height = img.size

	#pixels = img.load()
	k = 30

	I = np.asarray(Image.open('bird.jpg'), dtype=np.float32)

	# height = I.shape[0]
	# width = I.shape[1]
	for i in range(I.shape[0]):
	    for j in range(I.shape[1]):
	    	I[i][j] = rgb2lab(I[i][j][0],I[i][j][1],I[i][j][2])

	scipy.misc.imsave('bird_lab.jpg', I)

	S = int( sqrt( (I.shape[0] * I.shape[1]) / k ) )

	# escreve as linhas horizontais
	for i in range(S, I.shape[0], S):
		for j in range(0, I.shape[1], 1):
			if i < I.shape[0]:
				I[i][j] = rgb2lab(255,255,255)

	# escreve as linhas verticais
	for i in range(0, I.shape[0], 1):
		for j in range(S, I.shape[1], S):
			if j < I.shape[1]:
				I[i][j] = rgb2lab(255,255,255)

	scipy.misc.imsave('bird_lab_line.jpg', I)		
	
	center_cells = []
	for i in range(0, I.shape[0], S):
		for j in range(0, I.shape[1], S):
			#if (i < I.shape[0]) and (j < I.shape[1]):
			if (i + S) > I.shape[0] :
				pos_i = i + int((I.shape[0] - i) / 2)
			else:
				pos_i = i + int(S/2)
			if (j + S) > I.shape[1] :
				pos_j = j + int((I.shape[1] - j) / 2)
			else:
				pos_j = j + int(S/2)

			I[pos_i][pos_j] = rgb2lab(255,255,255)	
			min_grad = calcGradient(I, pos_i - 1, pos_j - 1)
			pos_x    = min_grad[0]
			pos_y    = min_grad[1]
			center   = I[min_grad[0]][min_grad[1]]
			center_cells.append([center[0], center[1], center[2], pos_x, pos_y])
			I[pos_x][pos_y] = rgb2lab(0,0,0)

	scipy.misc.imsave('bird_lab_line_center.jpg', I)
				

	# label and distance
	lD = []
	for i in range(0, I.shape[0], 1):
		lD[i] = []
		for j in range(0, I.shape[1], 1):
			lD[i].append([-1, np.inf])

	k = 0
	for center in center_cells:
		s2_block = generateBlock2s(I, center[3], center[4], S)
		for x in range(s2_block[0], s2_block[2], 1):
			for y in range(s2_block[1], s2_block[3], 1):
				D = calcDistance(I, center[3], center[4], x, j, S)
				if D < lD[x][y][1] :
					lD[x][y][1] = D
					lD[x][y][0] = k
		k += 1

		
	