const float reference_white[n_illuminants][3] = {
	/* A  */  {1.09850f,  1.0f, 0.35585f},
	/* C  */  {0.98074f,  1.0f, 1.18232f},
	/* D50 */ {0.96422f,  1.0f, 0.82521f},
	/* D55 */ {0.95682f,  1.0f, 0.92149f},
	/* D65 */ {0.95047f,  1.0f, 1.08883f},
	/* D75 */ {0.94972f,  1.0f, 1.22638f},
	/* F2 */  {0.99187f,  1.0f, 0.67395f},
	/* F7 */  {0.95044f,  1.0f, 1.08755f},
	/* F11 */ {1.00966f,  1.0f, 0.64370f},
	/* test*/ {1.00000f,  1.0f, 1.0f    } };

static double inv_gamma_sRGB( float x) {
	double ft,t=(double) (x>0)?x:-x;
	if ( t > 0.04045 ) 
	   ft = pow((t+0.055)/1.055,2.4);
	else
       ft =  t/12.92;
           
    return (x>0)?ft:-ft;
}

int corsRGBtoCIEXYZ(float R, float G, float B, float* X, float* Y, float* Z, int reference_light){
   double Rc = inv_gamma_sRGB(R);
   double Gc = inv_gamma_sRGB(G);
   double Bc = inv_gamma_sRGB(B);

   *X = (float) (Rc*0.4124564 + Gc*0.3575761 + Bc*0.1804375);
   *Y = (float) (Rc*0.2126729 + Gc*0.7151522 + Bc*0.0721750);
   *Z = (float) (Rc*0.0193339 + Gc*0.1191920 + Bc*0.9503041);

  return (*X<0||*Y<0||*Z<0) ? 0 : 1;
}

static double gamma_Lab(double t) {
	double ft, e=216.0/24389, k= 24389.0/27;
	if (t>e) 
		ft=pow(t,1.0/3); 
	else
		ft=(k*t+16)/116;
	return ft;
}

/* D65 */ {0.95047f,  1.0f, 1.08883f}

int corCIEXYZtoLab(float X, float Y, float Z, float* L, float* a, float* b, int reference_light) {
  double xr = (double)X/reference_white[reference_light][0];
  double yr = (double)Y/reference_white[reference_light][1];
  double zr = (double)Z/reference_white[reference_light][2];

  double fx = gamma_Lab(xr);
  double fy = gamma_Lab(yr);
  double fz = gamma_Lab(zr);

  *L = (float)(116*fy-16);
  *a = (float)(500*(fx-fy));
  *b = (float)(200*(fy-fz));

  return (*L<0||*L>100)?0:1;
}