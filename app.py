import os
import pdfplumber
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the upload directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Use environment variables for sensitive data
GOOGLE_API_KEY = os.getenv("AIzaSyDT44DwhkyBDfA8pjggMguusRaMEyp0VhM")  # Set this in your environment
GEN_AI_URL = "https://generativelanguage.googleapis.com/v1beta2/models/gemini-1.5-flash:generateText"

@app.route('/')
def upload_form():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Upload PDF</title>
    </head>
    <body>
      <h2>Upload a PDF</h2>
      <form action='/upload-pdf' method='post' enctype="multipart/form-data">
          <label for="pdf">Choose a PDF file:</label>
          <input type="file" name="pdf" accept="application/pdf" required />
          <br><br>
          <input type='submit' value='Upload PDF!' />
      </form>
    </body>
    </html>
    '''

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "No file part", 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return "No selected file", 400

    # Save the file to the upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
    pdf_file.save(file_path)

    try:
        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf(file_path)

        # Send the extracted text to Google Gemini API
        gemini_response = send_to_gemini(extracted_text)

        return jsonify({
            'message': 'PDF processed successfully',
            'gemini_output': gemini_response
        })
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return "Failed to process PDF.", 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text()
    return all_text

def send_to_gemini(pdf_text):
    prompt = """
    I have a PDF document containing a student's exam results. The document has the following sections:

    1. Front Page: 
       - Student Enrollment: A number in the format "0801CSXXXXXXX".
       - Table: A table with 5 rows representing questions and 6 columns (a, b, c, d, e, Total).
       - Grand Total: The total marks obtained.

    2. Other Pages:
       - Page Number: A number printed in the upper right corner of each page.
       - Marks: A number representing the total marks for that page, also printed in the upper right corner.

    Please extract the following information from the PDF:

    - Student Enrollment
    - Page-wise Marks: An array of objects, each containing "page_no" and "marks".
    - Total Marks: The total marks obtained.
    - Table Marks: An array of objects, each containing "question_no" (1 to 5), and the marks for columns "a", "b", "c", "d", "e", and "total".

    Example output in JSON format:
    {
      "enrollment": "0801CS191041",
      "page_wise_marks": [
        {
          "page_no": 2,
          "marks": 6
        },
        {
          "page_no": 3,
          "marks": 70
        }
      ],
      "total_marks": 22,
      "table_marks": [
        {
          "question_no": 1,
          "a": 0,
          "b": 2,
          "c": 2,
          "d": null,
          "e": 1,
          "total": 5
        }
      ]
    }
    """

    headers = {
        'Authorization': f'Bearer {GOOGLE_API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        "prompt": {
            "text": prompt + pdf_text  # Append PDF text to prompt
        },
        "temperature": 0.7
    }

    response = requests.post(GEN_AI_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('result', 'No result found')
    else:
        return f"Error: {response.status_code} - {response.text}"

if __name__ == '__main__':
    app.run(debug=True)
