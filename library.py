# FCG 2017.1
# Alexandre Werneck

#### References ####
# https://github.com/jayrambhia/superpixels-SLIC/blob/master/SLICcv.py

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
	#return 0 if ((L<0)or(L>100)) else 1

def inv_gamma_srgb(x):
	ft = t = x if (x > 0) else -x
	if t > 0.04045:
		ft = pow((t+0.055)/1.055,2.4)
	else:
		ft = t/12.92

	return ft if (x > 0) else -ft

# RGB to CIEXYZ
def rgb2ciexyz(R,G,B, reference_light=None):
	rc = inv_gamma_srgb(R)
	gc = inv_gamma_srgb(G)
	bc = inv_gamma_srgb(B)

	X = (rc*0.4124564 + gc*0.3575761 + bc*0.1804375);
	Y = (rc*0.2126729 + gc*0.7151522 + bc*0.0721750);
	Z = (rc*0.0193339 + gc*0.1191920 + bc*0.9503041);

	return (X,Y,Z)
	#return 0 if ((X<0)or(Y<0)or(Z<0)) else 1


def rgb2lab(R,G,B, reference_light=None):
	xyz = rgb2ciexyz(R,G,B,reference_light)
	lab = xyz2lab(xyz[0], xyz[1], xyz[2], 0)
	return lab

def generateBlock2s(I, x, y, S):
	pos_x = x
	pos_y = y
	if (x - S) < 0:
		pos_x = 0
	else if (x + S) > I.shape[0]:
		pos_x = I.shape[0] - 1
	else:
		pos_x = x - S

	if (y - S) < 0:
		pos_y = 0
	else if (y + S) > I.shape[1]:
		pos_y = I.shape[1] - 1
	else:
		pos_y = y - S

	return (pos_x, pos_y, pos_x + (2 * S), pos_y + (2 * S))


def calcDistance(P, ci, cj, pi, pj, mc, ms=100):
	l = ( P[ci][0] - P[cj][0] ) ** 2
	a = ( P[ci][1] - P[cj][1] ) ** 2
	b = ( P[ci][2] - P[cj][2] ) ** 2
	dc = sqrt( l + a + b )

	x = (ci - cj)**2
	y = (pi - pj)**2
	ds = sqrt( x + y )

	return sqrt( ((dc/mc)**2) + ((ds/ms)**2) )
	

def calcGradient(I, x, y):
	min_grad = np.inf
	loc_min  = I[x, y]
	for i in range(0, 3, 1):
		for j in range(0, 3, 1):
			c1 = I[i + x][j + x + 1]
			c2 = I[i + x + 1][j + x]
			c3 = I[i + x][j + y]
			if ((c1[0] - c3[0])**2)**0.5 + ((c2[0] - c3[0])**2)**0.5 < min_grad:
				min_grad = abs(c1[0] - c3[0]) + abs(c2[0] - c3[0])
				loc_min = [x + i, y + j]

	return loc_min