from FPDF.Circular import *

pdf = CircularText()
pdf.AddPage()
pdf.SetFont('Arial','',32)

text='Circular Text'
pdf.CircularText(105, 50, 30, text, 'top')
pdf.CircularText(105, 50, 30, text, 'bottom')

pdf.Output('Circular.pdf','F')
