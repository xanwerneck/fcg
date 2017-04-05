# FCG 2017.1
# Alexandre Werneck

#### REFERENCES ####

import sys

from PIL import Image, ImageMath
from math import pow, sqrt
import numpy as np
import scipy.misc

from library import *

class SuperPixel(object):
	def __init__(self, center=None, pixels=[], index=None):
		self.center = center
		self.pixels = pixels
		self.index  = index

class Pixel(object):
	def __init__(self,l,a,b,x,y,label=-1,distance=np.inf):
		self.l = l
		self.a = a
		self.b = b
		self.x = x
		self.y = y
		self.label    = label
		self.distance = distance

class Slico(object):
	def __init__(self, k=10, superpixels=[], height=None, width=None, pixels=None):
		self.superpixels = superpixels
		self.k = k
		self.height      = height
		self.width       = width
		self.pixels      = pixels
		self.original    = None
		self.E           = np.inf
		self.S           = np.inf

	# Save Image for debug Situations
	def saveImage(self, url='file_out.jpg'):
		pix = [[(0.,0.,0.) for x in range(self.width)] for y in range(self.height)] 
		for i in range(self.height):
			for j in range(self.width):
				pixel = self.pixels[i][j]
				pix[i][j] = (pixel.l, pixel.a, pixel.b)
		scipy.misc.imsave(url, pix)

	# Save Image in the end of process
	def saveImageOriginal(self, url='file_out.jpg'):
		pix = [[(0.,0.,0.) for x in range(self.width)] for y in range(self.height)] 
		for i in range(self.height):
			for j in range(self.width):
				pix[i][j] = self.original[i,j]
		scipy.misc.imsave(url, pix)

	def displayContours(self, color):
	    dx8 = [-1, -1, 0, 1, 1, 1, 0, -1]
	    dy8 = [0, -1, -1, -1, 0, 1, 1, 1]

	    exist      = np.zeros((self.height, self.width), np.bool)
	    p_contours = []

	    for i in xrange(self.width):
	        for j in xrange(self.height):
	            nr_p = 0
	            for dx, dy in zip(dx8, dy8):
	                x = i + dx
	                y = j + dy
	                if x>=0 and x < self.width and y>=0 and y < self.height:
	                	if (self.pixels[j][i].label is not None) and (self.pixels[y][x].label is not None):
		                    if exist[y, x] == False and self.pixels[j][i].label != self.pixels[y][x].label:
		                        nr_p += 1

	            if nr_p >= 2:
	                exist[j, i] = True
	                p_contours.append([j, i])

	    for i in xrange(len(p_contours)):
	    	# CIELab Pixels update
	    	self.pixels[p_contours[i][0]][p_contours[i][1]].l = color[0]
	    	self.pixels[p_contours[i][0]][p_contours[i][1]].a = color[1]
	    	self.pixels[p_contours[i][0]][p_contours[i][1]].b = color[2]

	    	# Original RGB Pixels update
	    	self.original[p_contours[i][0], p_contours[i][1]] = (255,255,255)	

	# End of proccess SuperPixel correction of orphans Pixels
	def createConnectivity(self):
	    label    = 0
	    alabel   = 0
	    lims = (self.width * self.height) / len(self.superpixels)
	    dx4  = [-1, 0, 1, 0]
	    dy4  = [0, -1, 0, 1]
	    clusters = -1 * np.ones((self.height, self.width))
	    elements = []
	    for i in xrange(self.width):
	        for j in xrange(self.height):

	            if clusters[j, i] == -1:
	                elements = []
	                elements.append((j, i))
	                for dx, dy in zip(dx4, dy4):
	                    x = elements[0][1] + dx
	                    y = elements[0][0] + dy
	                    if (x>=0 and x < self.width and 
	                        y>=0 and y < self.height and 
	                        clusters[y, x] >=0):
	                        alabel = clusters[y, x]
	            count = 1
	            c = 0
	            while c < count:
	                for dx, dy in zip(dx4, dy4):
	                    x = elements[c][1] + dx
	                    y = elements[c][0] + dy

	                    if (x>=0 and x<self.width and y>=0 and y<self.height):
	                    	pixel_a = self.pixels[j][i]
	                    	pixel_b = self.pixels[y][x]
	                        if (clusters[y, x] == -1) and (pixel_a.label == pixel_b.label):
	                            elements.append((y, x))
	                            clusters[y, x] = label
	                            count+=1
	                c+=1

	            if (count <= lims >> 2):
	                for c in range(count):
	                    clusters[elements[c]] = alabel
	                label-=1
	            label+=1
	    
	    # Update the label of Pixels
	    for i in xrange(self.height):
	        for j in xrange(self.width):
	        	self.pixels[i][j].label = clusters[i, j]

	# Start SuperPixel process
	def initialData(self, img=None):
		# First of all - open image and convert to numpy array
		imgpixels   = np.asarray(Image.open(img), dtype=np.float32)
		# Save the original RGB image
		self.original = imgpixels
		# Get the image dimensions
		self.height   = imgpixels.shape[0]
		self.width    = imgpixels.shape[1]

		# Initialize pixels array structure
		self.pixels = [[None for x in range(self.width)] for y in range(self.height)] 

		# Convert to CIELab and create the pixels structure
		for i in range(self.height):
			for j in range(self.width):
				imgpixel = rgb2lab(imgpixels[i][j][0],imgpixels[i][j][1],imgpixels[i][j][2])
				l = imgpixel[0]
				a = imgpixel[1]
				b = imgpixel[2]
				pixel = Pixel(l,a,b,i,j)
				self.pixels[i][j] = pixel

		# Compute the number of regular grid
		# S = sqrt( N / k )
		# where N = width x height and k = number of superpixels by user
		self.S = int( sqrt( (self.height * self.width) / self.k ) )

		# Create the first center Pixels
		SuperPixelIndex = 0
		for i in range(0, self.height, self.S):
			for j in range(0, self.width, self.S):

				if (i + self.S) > self.height :
					pos_i = i + int((self.height - i) / 2)
				else:
					pos_i = i + int(self.S/2)
				if (j + self.S) > self.width :
					pos_j = j + int((self.width - j) / 2)
				else:
					pos_j = j + int(self.S/2)

				# Calculate the min gradient of a center pixel in superpixel box 3 x 3 neighborhood
				min_grad   = calcGradientNorm(self.pixels, pos_i, pos_j, self.width, self.height)
				center     = self.pixels[min_grad[0]][min_grad[1]]

				# Create superpixel object
				superpixel = SuperPixel(center, [], SuperPixelIndex)
				self.superpixels.append(superpixel)

				# Increment superpixel index
				SuperPixelIndex += 1

	# Update Steps of Slic
	def updateData(self):
		count  = 0
		max_wh = np.sqrt(self.width * self.height) * (self.k ** 1.15)

		while (count < 10) and (self.E > max_wh):

			# Assigment Step - Compute 
			#
			# For each center create a 2S x 2S area and compute
			# the distance between center pixel and i pixel in 2S area
			for superpixel in self.superpixels:
				s2_block = generateBlock2s(self.pixels, superpixel.center.x, superpixel.center.y, self.S, self.width, self.height)
				for x in range(s2_block[0], s2_block[2], 1):
					for y in range(s2_block[1], s2_block[3], 1):
						D     = calcDistance(self.pixels, superpixel.center.x, superpixel.center.y, x, y, self.S)
						pixel = self.pixels[x][y]
						if D < pixel.distance:
							pixel.distance = D
							pixel.label    = superpixel.index
							superpixel.pixels.append(pixel)

			# Update Step
			# Compute new cluster centers
			E = 0
			K = 0
			spixels = []
			for superpixel in self.superpixels:
				a_mean = []
				for x in superpixel.pixels:
					if x.label == superpixel.index:
						a_mean.append([x.l, x.a, x.b, x.x, x.y])
				if len(a_mean) > 0:
					mean       = np.mean(a_mean, axis=0)

					old_center = superpixel.center
					new_center = Pixel(mean[0],mean[1],mean[2],int(mean[3]),int(mean[4]),K,np.inf)

					error      = calcError( (new_center.l,new_center.a,new_center.b,new_center.x,new_center.y),
						(old_center.l,old_center.a,old_center.b,old_center.x,old_center.y) )
					E         += error

					spixel        = SuperPixel(new_center, [], K)
					spixels.append(spixel)

					K += 1

			self.E = E
			self.superpixels = spixels

			# Increment Step of algorithm	
			count += 1



# Main
if __name__ == '__main__':
	k   = sys.argv[1]
	img = sys.argv[2]
	pixel_class = Slico(k=int(k))
	print '---- Initial Data ----'
	pixel_class.initialData(img)
	print '---- Update Data ----'
	pixel_class.updateData()
	print '---- Create Connectivity ----'
	pixel_class.createConnectivity()
	print '---- Display Contours ----'
	pixel_class.displayContours((1900.,0.,-0.))
	print '---- Save Images SuperPixels LAB ----'
	pixel_class.saveImage('SLIC_LAB.jpg')	
	print '---- Save Images SuperPixels RGB ----'
	pixel_class.saveImageOriginal('SLIC_RGB.jpg')	

	exit()
