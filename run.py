# pip install virtualenv
# # .\env\Scripts\activate.ps1
# pip install flask
# python run.import osimport os  # Make sure this is includedimport osimport os
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image  # Import Pillow for image manipulation

# Initialize Flask app
app = Flask(__name__)

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'image' not in request.files:
            return 'No file part'

        file = request.files['image']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return 'No selected file'

        # If the file is valid, save it
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Convert the image to grayscale
            convert_to_grayscale(file_path)

            return redirect(url_for('display_image', filename=filename))

    return 'Error uploading image'

# def convert_to_grayscale(image_path):
#     """Convert the uploaded image to grayscale."""
#     img = Image.open(image_path)
#     grayscale_img = img.convert('L')  # Convert to grayscale ('L' mode is for black and white)
#     grayscale_img.save(image_path)  # Overwrite the original image file
def convert_to_grayscale(image_path):
    """Convert the uploaded image to grayscale and add a white background if it's transparent."""
    img = Image.open(image_path)
    img = img.convert('RGBA')  # Ensure the image has an alpha channel (transparency)
    
    # Create a white background image
    white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))  # Create white background (255, 255, 255 is white)
    
    # Paste the original image onto the white background
    white_bg.paste(img, (0, 0), img)
    
    # Convert to grayscale
    grayscale_img = white_bg.convert('L')  # Convert to grayscale ('L' mode is for black and white)
    
    # Save the new grayscale image (overwrite the original file or save it elsewhere)
    grayscale_img.save(image_path)

    return grayscale_img

@app.route('/display/<filename>')
def display_image(filename):
    return render_template('display.html', filename=filename)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/products")
def products():
    return "This is the product page"

if __name__ == '__main__':
    app.run(debug=True, port=8000)
