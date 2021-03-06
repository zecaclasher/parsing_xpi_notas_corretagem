# pdfTextMiner.py
# Python 2.7.6
# For Python 3.x use pdfminer3k module
# This link has useful information on components of the program
# https://euske.github.io/pdfminer/programming.html
# http://denis.papathanasiou.org/posts/2010.08.04.post.html


''' Important classes to remember
PDFParser - fetches data from pdf file
PDFDocument - stores data parsed by PDFParser
PDFPageInterpreter - processes page contents from PDFDocument
PDFDevice - translates processed information from PDFPageInterpreter to whatever you need
PDFResourceManager - Stores shared resources such as fonts or images used by both PDFPageInterpreter and PDFDevice
LAParams - A layout analyzer returns a LTPage object for each page in the PDF document
PDFPageAggregator - Extract the decive to page aggregator to get LT object elements
'''

import os
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
# Import this to raise exception whenever text extraction from PDF is not allowed
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator

''' This is what we are trying to do:
1) Transfer information from PDF file to PDF document object. This is done using parser
2) Open the PDF file
3) Parse the file using PDFParser object
4) Assign the parsed content to PDFDocument object
5) Now the information in this PDFDocumet object has to be processed. For this we need
   PDFPageInterpreter, PDFDevice and PDFResourceManager
6) Finally process the file page by page 
7) Set file name according to content (specific purpose)
8) save it
9) Rename pdf according to the content.
'''

def convert_pdf(my_file):
	password = ""
	extracted_text = ""

	# Open and read the pdf file in binary mode
	fp = open(my_file, "rb")

	# Create parser object to parse the pdf content
	parser = PDFParser(fp)

	# Store the parsed content in PDFDocument object
	document = PDFDocument(parser, password)

	# Check if document is extractable, if not abort
	if not document.is_extractable:
		raise PDFTextExtractionNotAllowed
		
	# Create PDFResourceManager object that stores shared resources such as fonts or images
	rsrcmgr = PDFResourceManager()

	# set parameters for analysis
	laparams = LAParams()

	# Create a PDFDevice object which translates interpreted information into desired format
	# Device needs to be connected to resource manager to store shared resources
	# device = PDFDevice(rsrcmgr)
	# Extract the decive to page aggregator to get LT object elements
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)

	# Create interpreter object to process page content from PDFDocument
	# Interpreter needs to be connected to resource manager for shared resources and device 
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	# Ok now that we have everything to process a pdf document, lets process it page by page
	for page in PDFPage.create_pages(document):
		# As the interpreter processes the page stored in PDFDocument object
		interpreter.process_page(page)
		# The device renders the layout from interpreter
		layout = device.get_result()
		# Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
		for lt_obj in layout:
			if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
				# # For debug only:
				# current_text = lt_obj.get_text()
				# print(current_text)
				# # ---------------
				extracted_text += lt_obj.get_text()

				
	#close the pdf file
	fp.close()

	# Get valuable informations
	data_list = extracted_text.split("\n")
	num_nota = data_list[data_list.index("Nº Nota:") + 1]
	data_nota = data_list[2].split(" ")[-1]
	data_split = data_nota.split("/")
	formato_data = str(data_split[2]) + str(data_split[1]) + str(data_split[0])
	cod_cliente = str(data_list[12])

	# Set filename with the information.
	file_name = cod_cliente + "-" + formato_data + "-NC"+ num_nota +  ".txt"
	log_file = os.path.join(base_path, "txt" ,file_name)
	print("Saving:",log_file)

	with open(log_file, "wb") as my_log:
		my_log.write(extracted_text.encode("utf-8"))
	print("Done !!")
	return file_name



base_path = os.path.dirname(os.path.realpath(__file__))

my_files = os.path.join(base_path,"pdf")



for file in os.listdir(my_files):
	if file.endswith(".pdf"):
		name = convert_pdf(os.path.join(my_files,file))
		os.system("mv '"+ os.path.join(my_files,file) + "'  '" + os.path.join(my_files,name[0:-3]) + "pdf'")