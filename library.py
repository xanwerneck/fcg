# FCG 2017.1
# Alexandre Werneck

#### Library ####
import numpy as np
from math import pow, sqrt

reference_white = [
	[0.95047,  1.0, 1.08883]
]

def gamma_Lab(t):
	e = 216.0/24389
	k = 24389.0/27

	if t > e:
		ft = pow(t,1.0/3)
	else:
		ft = (k*t+16)/116		

	return ft

def xyz2lab(x,y,z, reference_light=None):
	xr = x / reference_white[reference_light][0]
	yr = y / reference_white[reference_light][1]
	zr = z / reference_white[reference_light][2]

	fx = gamma_Lab(xr)
	fy = gamma_Lab(yr)
	fz = gamma_Lab(zr)

	L = float(116*fy-16);
	a = float(500*(fx-fy));
	b = float(200*(fy-fz));

	return (L,a,b)

def inv_gamma_srgb(x):
	ft = t = x if (x > 0) else -x
	if t > 0.04045:
		ft = pow((t+0.055)/1.055,2.4)
	else:
		ft = t/12.92

	return ft if (x > 0) else -ft

def rgb2ciexyz(R,G,B, reference_light=None):
	rc = inv_gamma_srgb(R)
	gc = inv_gamma_srgb(G)
	bc = inv_gamma_srgb(B)

	X = (rc*0.4124564 + gc*0.3575761 + bc*0.1804375);
	Y = (rc*0.2126729 + gc*0.7151522 + bc*0.0721750);
	Z = (rc*0.0193339 + gc*0.1191920 + bc*0.9503041);

	return (X,Y,Z)


def rgb2lab(R,G,B, reference_light=None):
	xyz = rgb2ciexyz(R,G,B,reference_light)
	lab = xyz2lab(xyz[0], xyz[1], xyz[2], 0)

	return lab

def generateBlock2s(I, x, y, S, width, height):
	x_a = x - S
	y_a = y - S
	x_a_pos = x + S
	y_a_pos = y + S
	if (x - S) < 0:
		x_a = 0
		x_a_pos = 2 * S
	elif (x + S) > height:
		x_a_pos = height - 1
		x_a = x_a_pos - (2 * S)

	if (y - S) < 0:
		y_a = 0
		y_a_pos = 2 * S
	elif (y + S) > width:
		y_a_pos = width - 1
		y_a = y_a_pos - (2 * S)

	return (x_a, y_a, x_a_pos, y_a_pos)


def calcError(center, new_center):
	return np.linalg.norm(np.subtract(new_center, center))

def calcNewCenter(color_mean, spixel, S):
	center   = spixel.center
	min_dist = np.inf
	for pixel in spixel.pixels:
		D = calcDistanceMean(pixel, color_mean[0], color_mean[1], color_mean[2])
		if D < min_dist:
			min_dist = D
			center   = pixel
	return ( center , calcError((center.l, center.a, center.b), (spixel.center.l, spixel.center.a, spixel.center.b)) )


def calcDistanceMean(pixel,pl,pa,pb,ms=40):
	l = ( pixel.l - pl ) ** 2
	a = ( pixel.a - pa ) ** 2
	b = ( pixel.b - pb ) ** 2

	dc = np.sqrt( l + a + b )

	return dc

def calcDistance(P, ci, cj, pi, pj, mc, ms=40):
	l = ( P[pi][pj].l - P[ci][cj].l ) ** 2
	a = ( P[pi][pj].a - P[ci][cj].a ) ** 2
	b = ( P[pi][pj].b - P[ci][cj].b ) ** 2
	dc = np.sqrt( l + a + b )


	x = ( pi - ci )**2
	y = ( pj - cj )**2
	ds = np.sqrt( x + y )

	comp1 = dc ** 2
	comp2 = ((ds / mc) ** 2) * (ms ** 2)
	return np.sqrt( comp1 + comp2 )
	
def calcGradientNorm(I, x, y, w, h):
	min_grad = np.inf
	loc_min  = [x, y]

	max_i = max_j = 3
	if (x + 3) >= h:
		max_i = h - (x + 1)
	if (y + 3) >= w:
		max_j = w - (y + 1)

	for i in range(0, max_i, 1):
		for j in range(0, max_j, 1):

			pix_a = (I[x + i][y].l, I[x + i][y].a, I[x + i][y].b)
			pix_b = (I[x - i][y].l, I[x - i][y].a, I[x - i][y].b)

			pix_c = (I[x][y + j].l, I[x][y + j].a, I[x][y + j].b)
			pix_d = (I[x][y - j].l, I[x][y - j].a, I[x][y - j].b)

			c1 = np.linalg.norm( np.subtract( pix_a, pix_b ) ) ** 2
			c2 = np.linalg.norm( np.subtract( pix_c, pix_d ) ) ** 2
			G  = c1 + c2
			if G < min_grad:
				min_grad = G
				loc_min  = [x + i, y + j]

	return loc_min
