from FPDF import *
from math import *

""" Version 2
Changes since version 1:
- added def MirrorP()
- added def MirrorL()
- fixed bug in Translate(): the movement is now performed in user units instead of pts"""

class Transform(FPDF):
	def StartTransform(this):
		#save the current graphic state
		this._out('q')

	def ScaleX(this, s_x, x='', y=''):
		this.Scale(s_x, 100, x, y)
	
	def ScaleY(this, s_y, x='', y=''):
		this.Scale(100, s_y, x, y)
	
	def ScaleXY(this, s, x='', y=''):
		this.Scale(s, s, x, y)
	
	def Scale(this, s_x, s_y, x='', y=''):
		if(x == ''):
			x=this.x
		if(y == ''):
			y=this.y
		if(s_x == 0 or s_y == 0):
			this.Error('Please use values unequal to zero for Scaling')
		y=(this.h-y)*this.k
		x*=this.k
		#calculate elements of transformation matrix
		s_x/=100.0
		s_y/=100.0
		tm[0]=s_x
		tm[1]=0
		tm[2]=0
		tm[3]=s_y
		tm[4]=x*(1-s_x)
		tm[5]=y*(1-s_y)
		#scale the coordinate system
		this.Transform(tm)

	def MirrorH(this, x=''):
		this.Scale(-100, 100, x)
	
	def MirrorV(this, y=''):
		this.Scale(100, -100, '', y)
	
	def MirrorP(this, x='',y=''):
		this.Scale(-100, -100, x, y)
	
	def MirrorL(this, angle=0, x='',y=''):
		this.Scale(-100, 100, x, y)
		this.Rotate(-2*(angle-90),x,y)

	def TranslateX(this, t_x):
		this.Translate(t_x, 0, x, y)
	
	def TranslateY(this, t_y):
		this.Translate(0, t_y, x, y)
	
	def Translate(this, t_x, t_y):
		#calculate elements of transformation matrix
		tm[0]=1
		tm[1]=0
		tm[2]=0
		tm[3]=1
		tm[4]=t_x*this.k
		tm[5]=-t_y*this.k
		#translate the coordinate system
		this.Transform(tm)

	def Rotate(this, angle, x='', y=''):
		if(x == ''):
			x=this.x
		if(y == ''):
			y=this.y
		y=(this.h-y)*this.k
		x*=this.k
		#calculate elements of transformation matrix
		tm={}
		tm[0]=cos(radians(angle))
		tm[1]=sin(radians(angle))
		tm[2]=-tm[1]
		tm[3]=tm[0]
		tm[4]=x+tm[1]*y-tm[0]*x
		tm[5]=y-tm[0]*y-tm[1]*x
		#rotate the coordinate system around (x,y)
		this.Transform(tm)
	
	def SkewX(this, angle_x, x='', y=''):
		this.Skew(angle_x, 0, x, y)
	
	def SkewY(this, angle_y, x='', y=''):
		this.Skew(0, angle_y, x, y)
	
	def Skew(this, angle_x, angle_y, x='', y=''):
		if(x == ''):
			x=this.x
		if(y == ''):
			y=this.y
		if(angle_x <= -90 or angle_x >= 90 or angle_y <= -90 or angle_y >= 90):
			this.Error('Please use values between -90° and 90° for skewing')
		x*=this.k
		y=(this.h-y)*this.k
		#calculate elements of transformation matrix
		tm[0]=1
		tm[1]=tan(deg2rad(angle_y))
		tm[2]=tan(deg2rad(angle_x))
		tm[3]=1
		tm[4]=-tm[2]*y
		tm[5]=-tm[1]*x
		#skew the coordinate system
		this.Transform(tm)
	
	def Transform(this, tm):
		this._out(sprintf('%.3f %.3f %.3f %.3f %.3f %.3f cm', tm[0],tm[1],tm[2],tm[3],tm[4],tm[5]))

	def StopTransform(this):
		#restore previous graphic state
		this._out('Q')
