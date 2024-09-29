from PyPDF2 import PdfReader, PdfWriter  # Import PdfWriter

def cropper(start, end, file):
    inputPdf = PdfReader(open(file, "rb")) 
    outPdf = PdfWriter()  # Use PdfWriter here
    ostrem = open(file.split(".")[0] + "cropped.pdf", "wb") 
    
    for page_num in range(start, end + 1):  
        outPdf.addPage(inputPdf.getPage(page_num))

    outPdf.write(ostrem)
    ostrem.close()

cropper(1, 3, "Self.pdf")
