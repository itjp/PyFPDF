from transform import *

class CircularText(Transform):
	def CircularText(this, x, y, r, text, align="top", kerning=120, fontwidth=100):
		w={}
		t=0
		kerning/=100
		fontwidth/=100;		
		if(kerning==0):
			this.Error('Please use values unequal to zero for kerning')
		if(fontwidth==0):
			this.Error('Please use values unequal to zero for font width')
		for i in range(len(text)):
		#get width of every letter
			w[i]=this.GetStringWidth(text[i])
			w[i]*=kerning*fontwidth
			#total width of string
			t+=w[i]
		#circumference
		u=(r*2)*3.141592654
		#total width of string in degrees
		d=(t/u)*360
		this.StartTransform()
		# rotate matrix for the first letter to center the text
		# (half of total degrees)
		if align == 'top':
			this.Rotate(d/2, x, y)
		else:
			this.Rotate(-d/2, x, y)
			#run through the string
		for i in range(len(text)):
			if align == 'top':
				if i == 0:
				#rotate matrix half of the width of current letter + half of the width of preceding letter
					this.Rotate(-((w[i]/2)/u)*360, x, y)
				else:
					this.Rotate(-((w[i]/2+w[i-1]/2)/u)*360, x, y)
				if fontwidth != 1:
					this.StartTransform()
					this.ScaleX(fontwidth*100, x, y)
				this.SetXY(x-w[i]/2, y-r)
			else:
				#rotate matrix half of the width of current letter + half of the width of preceding letter
				if i == 0:
					this.Rotate(((w[i]/2)/u)*360, x, y)
				else:
					this.Rotate(((w[i]/2+w[i-1]/2)/u)*360, x, y)
				if fontwidth != 1:
					this.StartTransform()
					this.ScaleX(fontwidth*100, x, y)
				this.SetXY(x-w[i]/2, y+r-(this.FontSize))
			this.Cell(w[i],this.FontSize,text[i],0,0,'C')
		if fontwidth != 1:
			this.StopTransform()
		this.StopTransform()
