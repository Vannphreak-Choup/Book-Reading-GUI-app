
# this file is used to store the data of the app, such as the pdf files, the selected files
pdf_files = {}
selected_files = None

# the document object of the opened pdf file
doc = None
# the list of the images of the pdf pages, we need to store them in a list to prevent them from being garbage collected
pdf_images = []
# the dictionary of the file labels, we need to store them in a dictionary to prevent them from being garbage collected
file_labels = {}

