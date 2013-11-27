from FPDF import *

class FPDF_WB(FPDF):
	def __init__(this, orientation='P',unit='mm',format='A4'):
		FPDF.__init__(this, orientation,unit,format)
		this._reset_TextState()

	def _checkstate(this):
		if this.TextState['i'] != this.TextState['j']:
			this.MultiCellWB(0,0,0)

	def _reset_TextState(this):
		this.TextState={'sep':-1, 'l':0, 'ns':0, 'nl':1, 'i':0, 'j':0, 's':'', 'o':['BT'], 'ET':0, 'First':1}

	def CellWB(this, w,h=0,txt='',border=0,ln=0,align='',fill=0,link=''):
		print 'Cell (%s)' % txt
		#Output a cell
		k=this.k
		if(this.y+h>this.PageBreakTrigger and not this.InFooter and this.AcceptPageBreak()):
			#Automatic page break
			x=this.x
			ws=this.ws
			if(ws>0):
				this.ws=0
				this._out('0 Tw')
			this.AddPage(this.CurOrientation)
			this.x=x
			if(ws>0):
				this.ws=ws
				this._out(sprintf('%.3f Tw',ws*k))
		if(w==0):
			w=this.w-this.rMargin-this.x
		s=''
		if(fill==1 or border==1):
			if(fill==1):
				if border==1:
					op='B'
				else:
					op='f'
			else:
				op='S'
			s=sprintf('%.2f %.2f %.2f %.2f re %s ',this.x*k,(this.h-this.y)*k,w*k,-h*k,op)
		if(is_string(border)):
			x=this.x
			y=this.y
			if(strpos(border,'L')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-y)*k,x*k,(this.h-(y+h))*k)
			if(strpos(border,'T')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-y)*k,(x+w)*k,(this.h-y)*k)
			if(strpos(border,'R')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',(x+w)*k,(this.h-y)*k,(x+w)*k,(this.h-(y+h))*k)
			if(strpos(border,'B')!=-1):
				s+=sprintf('%.2f %.2f m %.2f %.2f l S ',x*k,(this.h-(y+h))*k,(x+w)*k,(this.h-(y+h))*k)
		if(txt!=''):
			if(align=='R'):
				dx=w-this.cMargin-this.GetStringWidth(txt)
			elif(align=='C'):
				dx=(w-this.GetStringWidth(txt))/2.0
			else:
				dx=this.cMargin
			if(this.ColorFlag):
				#~ s+='q '+this.TextColor+' '
				this.TextState['o'].append(this.TextColor)
			txt2=str_replace(')','\\)',str_replace('(','\\(',str_replace('\\','\\\\',txt)))
			if this.TextState['First']:
				this.TextState['o'].append(sprintf('%.2f %.2f Td (%s) Tj ',(this.x+dx)*k,(this.h-(this.y+.5*h+.3*this.FontSize))*k,txt2))
				this.TextState['First']=0
			else:
				this.TextState['o'].append(sprintf('(%s) Tj ',txt2))
			if(this.underline):
				this.TextState['o'].append(this._dounderline(this.x+dx,this.y+.5*h+.3*this.FontSize,txt))
			#~ if(this.ColorFlag):
				#~ s+=' Q'
			if(link):
				this.TextState['o'].append(this.Link(this.x+dx,this.y+.5*h-.5*this.FontSize,this.GetStringWidth(txt),this.FontSize,link))
		if this.TextState['ET']:
			this._out('\n'.join(this.TextState['o'])+'\nET')
		this.lasth=h
		if(ln>0):
			#Go to next line
			this.y+=h
			if(ln==1):
				this.x=this.lMargin
		else:
			this.x+=w

	def MultiCellWB(this,w,h,txt,border=0,align='J',fill=0):
		print 'STATE', this.TextState
		b=0
		if(border):
			if(border==1):
				border='LTRB'
				b='LRT'
				b2='LR'
			else:
				b2=''
				if(strpos(border,'L')!=-1):
					b2+='L'
				if(strpos(border,'R')!=-1):
					b2+='R'
				if (strpos(border,'T')!=-1):
					b=b2+'T'
				else:
					b=b2

		#Output text with automatic or explicit line breaks
		cw=this.CurrentFont['cw']
		if(w==0):
			w=this.w-this.rMargin-this.x
		wmax=(w-2*this.cMargin)*1000

		if not is_string(txt):
			# Flush buffer
			this.CellWB(w,h,substr(this.TextState['s'],this.TextState['j'],this.TextState['i']-this.TextState['j']),b,2,align,fill)
			this.TextState['sep']=-1
			this.TextState['j']=this.TextState['i']
			return

		this.TextState['s']+=str_replace("\r",'',txt)
		nb=len(this.TextState['s'])

		while(this.TextState['i']<nb):
			#Get next character
			c=this.TextState['s'][this.TextState['i']]
			if(c=="\n"):
				print 'DEBUG: NEWLINE...'
				this.TextState['ET']=1
				#Explicit line break
				if(this.ws>0):
					this.ws=0
					this.TextState['o'].insert(1,'0 Tw')
				this.CellWB(w,h,substr(this.TextState['s'],this.TextState['j'],this.TextState['i']-this.TextState['j']),b,2,align,fill)
				this.TextState['i']+=1
				this.TextState['sep']=-1
				this.TextState['j']=this.TextState['i']
				this.TextState['l']=0
				this.TextState['ns']=0
				this.TextState['nl']+=1
				if(border and this.TextState['nl']==2):
					b=b2
				continue
			if(c==' '):
				this.TextState['sep']=this.TextState['i']
				this.TextState['ls']=this.TextState['l']
				this.TextState['ns']+=1
			this.TextState['l']+=cw[c]*this.FontSize
			if(this.TextState['l']>wmax):
				print 'MAX REACHED...'
				this.TextState['ET']=1
				#Automatic line break
				if(this.TextState['sep']==-1):
					if(this.TextState['i']==this.TextState['j']):
						this.TextState['i']+=1
					if(this.ws>0):
						this.ws=0
						this.TextState['o'].insert(1,'0 Tw')
						#this._out('0 Tw')
					this.CellWB(w,h,substr(this.TextState['s'],this.TextState['j'],this.TextState['i']-this.TextState['j']),b,2,align,fill)
				else:
					if(align=='J'):
						if this.TextState['ns']>1:
							this.ws=(wmax-this.TextState['ls'])/1000.0/(this.TextState['ns']-1)
						else:
							this.ws=0
						this.TextState['o'].insert(1,sprintf('%.3f Tw',this.ws*this.k))
					this.CellWB(w,h,substr(this.TextState['s'],this.TextState['j'],this.TextState['sep']-this.TextState['j']),b,2,align,fill)
					this.TextState['i']=this.TextState['sep']+1
				this.x=this.lMargin
				this.TextState['sep']=-1
				this.TextState['j']=this.TextState['i']
				this.TextState['l']=0
				this.TextState['ns']=0
				this.TextState['nl']+=1
				this.TextState['ET']=0
				this.TextState['o']=['BT']
				this.TextState['First']=1
				if(border and nl==2):
					b=b2
			else:
				this.TextState['i']+=1
		#Last chunk

	def SetFontWB(this, family,style='',size=0):
		this._checkstate()
		#Select a font; size given in points
		family=strtolower(family)
		if(family==''):
			family=this.FontFamily
		if(family=='arial'):
			family='helvetica'
		elif(family=='symbol' or family=='zapfdingbats'):
			style=''
		style=strtoupper(style)
		if(strpos(style,'U')!=-1):
			this.underline=1
			style=str_replace('U','',style)
		else:
			this.underline=0
		if(style=='IB'):
			style='BI'
		if(size==0):
			size=this.FontSizePt
		#Test if font is already selected
		if(this.FontFamily==family and this.FontStyle==style and this.FontSizePt==size):
			return
		#Test if used for the first time
		fontkey=family+style
		if fontkey not in this.fonts:
			#Check if one of the standard fonts
			if fontkey in this.CoreFonts:
				if fontkey not in fpdf_charwidths:
					#Load metric file
					name=os.path.join(FPDF_FONT_DIR,family)
					if(family=='times' or family=='helvetica'):
						name+=strtolower(style)
					execfile(name+'.py')
					if fontkey not in fpdf_charwidths:
						this.Error('Could not include font metric file for'+fontkey)
				i=len(this.fonts)+1
				this.fonts[fontkey]={'i':i,'type':'core','name':this.CoreFonts[fontkey],'up':-100,'ut':50,'cw':fpdf_charwidths[fontkey]}
			else:
				this.Error('Undefined font: '+family+' '+style)
		#Select it
		this.FontFamily=family
		this.FontStyle=style
		this.FontSizePt=size
		this.FontSize=size/this.k
		this.CurrentFont=this.fonts[fontkey]
		if(this.page>0):
			this.TextState['o'].append(sprintf('/F%d %.2f Tf',this.CurrentFont['i'],this.FontSizePt))

	def SetTextColorWB(this, r,g=-1,b=-1):
		#Set color for text
		this._checkstate()
		if((r==0 and g==0 and b==0) or g==-1):
			this.TextColor=sprintf('%.3f g',r/255.0)
		else:
			this.TextColor=sprintf('%.3f %.3f %.3f rg',r/255.0,g/255.0,b/255.0)
		this.ColorFlag=(this.FillColor!=this.TextColor)

	def SetFontSizeWB(this, size):
		#Set font size in points
		if(this.FontSizePt==size):
			return
		this.FontSizePt=size
		this.FontSize=size/this.k
		if(this.page>0):
			this.TextState['o'].append(sprintf('/F%d %.2f Tf',this.CurrentFont['i'],this.FontSizePt))
