#/****************************************************************************
#* Software: FPDF_Protection                                                 *
#* Version:  1.02                                                            *
#* Date:     2005/05/08                                                      *
#* Author:   Klemen VODOPIVEC                                                *
#* License:  Freeware                                                        *
#*                                                                           *
#* Modified on 2006/11/16 to support 128-bit RC4 encryption                  *
#*                                                                           *
#* You may use and modify this software as you wish as stated in original    *
#* FPDF package.                                                             *
#*                                                                           *
#* Thanks: Cpdf (http:#www.ros.co.nz/pdf) was my working sample of how to    *
#* implement protection in pdf.                                              *
#****************************************************************************/
from FPDF import *
import random, struct, md5, copy, array

class Protection(FPDF):
	def __init__(this, orientation='P',unit='mm',format='A4'):
		FPDF.__init__(this,orientation,unit,format)
		this.PDFVersion='1.4'
		this.encrypted=0           #whether document is protected
		this.Uvalue=''             #U entry in pdf document
		this.Ovalue=''             #O entry in pdf document
		this.Pvalue=''             #P entry in pdf document
		this.enc_obj_id=0          #encryption object id
		this.last_rc4_key=''       #last RC4 key encrypted (cached for optimisation)
		this.last_rc4_key_c=''     #last RC4 computed key
		this.encrypted=0
		this.padding="\x28\xBF\x4E\x5E\x4E\x75\x8A\x41\x64\x00\x4E\x56\xFF\xFA\x01\x08\x2E\x2E\x00\xB6\xD0\x68\x3E\x80\x2F\x0C\xA9\xFE\x64\x53\x69\x7A"
		

	#/**
	#* Function to set permissions as well as user and owner passwords
	#*
	#* - permissions is an array with values taken from the following list:
	#*   copy, print, modify, annot-forms
	#*   If a value is present it means that the permission is granted
	#* - If a user password is set, user will be prompted before document is opened
	#* - If an owner password is set, document can be opened in privilege mode with no
	#*   restriction if that password is entered
	#*/
	def SetProtection(this,permissions=[],user_pass='',owner_pass=None):
		options={'print':4, 'modify':8, 'copy':16, 'annot-forms':32}
		protection = 192
		for permission in permissions:
			if permission not in options:
				this.Error('Incorrect permission: '+permission)
			protection += options[permission]
		
		if (owner_pass == None):
			owner_pass=''
			for i in range(13):
				owner_pass += chr(random.randint(0,255))
		this.encrypted = 1
		this._generateencryptionkey(user_pass, owner_pass, protection)
		

	#/****************************************************************************
	#*                                                                           *
	#*                              Private methods                              *
	#*                                                                           *
	#****************************************************************************/
	def _putstream(this,s):
		if (this.encrypted):
			s = this._RC4(this._objectkey(this.n), s)
		FPDF._putstream(this,s)

	def _textstring(this,s):
		if (this.encrypted):
			s = this._RC4(this._objectkey(this.n), s)
		return FPDF._textstring(this,s)

	#/**
	#* Compute key depending on object number where the encrypted data is stored
	#*/
	def _objectkey(this,n):
		return this._md5_16(this.encryption_key+struct.pack('L',n)[:-1]+'\x00\x00')

	#/**
	#* Escape special characters
	#*/
	def _escape(this,s):
		s=str_replace('\\','\\\\',s)
		s=str_replace(')','\\)',s)
		s=str_replace('(','\\(',s)
		s=str_replace("\r",'\\r',s)
		return s

	def _putresources(this):
		FPDF._putresources(this)
		if (this.encrypted):
			this._newobj()
			this.enc_obj_id = this.n
			this._out('<<')
			this._putencryption()
			this._out('>>')
			this._out('endobj')

	def _putencryption(this):
		this._out('/Filter /Standard')
		this._out('/V 2')
		this._out('/R 3')
		this._out('/Length 128')
		this._out('/O ('+this._escape(this.Ovalue)+')')
		this._out('/U ('+this._escape(this.Uvalue)+')')
		this._out('/P '+str(this.Pvalue))

	def _puttrailer(this):
		FPDF._puttrailer(this)
		if (this.encrypted):
			this._out('/Encrypt '+str(this.enc_obj_id)+' 0 R')
			this._out('/ID [()()]')

	#/**
	#* RC4 is the standard encryption algorithm used in PDF format
	#*/
	def _RC4(this, key, text):
		if (this.last_rc4_key != key):
			k = str_repeat(key, 256/strlen(key)+1)
			rc4 = array.array('B',range(256))
			j = 0
			for i in range(256):
				t = rc4[i]
				j = (j + t + ord(k[i])) % 256
				rc4[i] = rc4[j]
				rc4[j] = t
			this.last_rc4_key = key
			this.last_rc4_key_c = copy.copy(rc4)
		else:
			rc4 = copy.copy(this.last_rc4_key_c)
		len = strlen(text)
		a = 0
		b = 0
		out = ''
		for i in range(len):
			a = (a+1)%256
			t= rc4[a]
			b = (b+t)%256
			rc4[a] = rc4[b]
			rc4[b] = t
			k = rc4[(rc4[a]+rc4[b])%256]
			out+=chr(ord(text[i]) ^ k)
		return out

	#/**
	#* Get MD5 as binary string
	#*/
	def _md5_16(this,string):
		return md5.new(string).digest()

	#/**
	#* Compute O value (rev.3)
	#*/
	def _Ovalue(this, user_pass, owner_pass):
		O = this._md5_16(owner_pass)
		for i in range(50):
			O = this._md5_16(O)
		owner_RC4_key = substr(O,0,16)
		O = this._RC4(owner_RC4_key, user_pass)
		for i in range(19):
			new_key = array.array('B', owner_RC4_key)
			for j in range(16):
				new_key[j] ^= (i+1)
			O = this._RC4(new_key.tostring(), O)
		return O
			

	#/**
	#* Compute U value (rev.3)
	#*/
	def _Uvalue(this):
		U = this._RC4(this.encryption_key, this._md5_16(this.padding))
		for i in range(19):
			new_key = array.array('B', this.encryption_key)
			for j in range(16):
				new_key[j] ^= (i+1)
			U = this._RC4(new_key.tostring(), U)
		for i in range(16):
			U += chr(random.randint(0,255))
		return U

	#/**
	#* Compute encryption key (rev.3)
	#*/
	def _generateencryptionkey(this, user_pass, owner_pass, protection):
		# Pad passwords
		user_pass = substr(user_pass+this.padding,0,32)
		owner_pass = substr(owner_pass+this.padding,0,32)
		# Compute O value
		this.Ovalue = this._Ovalue(user_pass,owner_pass)
		# Compute encyption key
		tmp = this._md5_16(user_pass+this.Ovalue+chr(protection)+"\xFF\xFF\xFF")
		for i in range(50):
			tmp = this._md5_16(tmp)
		this.encryption_key = substr(tmp,0,16)
		# Compute U value
		this.Uvalue = this._Uvalue()
		# Compute P value
		this.Pvalue = -((protection^255)+1)

if __name__ == '__main__':
	pdf=Protection()
	pdf.SetProtection(['print'], 'MyPassword')
	pdf.Open()
	pdf.AddPage()
	pdf.SetFont('Arial')
	pdf.Write(10,'You can print me but not copy my text. I am password-protected!')
	pdf.Output('Protected.pdf','F')
