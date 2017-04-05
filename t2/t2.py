# FCG 2017.1
# Alexandre Werneck

# Trabalho 2 - FindContours
import sys
import cv2

class FindContour(object):
	def __init__(self, img=None):
		self.img = img
		self.pixels_gray = None
		self.smooth      = None
		self.ret         = None
		self.thresh1     = None
		
	def find(self, imgFile=None):
		self.img = cv2.imread(imgFile)
		self.pixels_gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
		self.smooth = cv2.GaussianBlur(self.pixels_gray,(5,5),0)
		self.ret,self.thresh1 = cv2.threshold(self.smooth,155,255,cv2.THRESH_BINARY)
		cv2.imwrite('image.jpg', self.thresh1) 

# Main
if __name__ == '__main__':
	img = sys.argv[1]
	findC = FindContour()
	findC.find(img)

	exit()
