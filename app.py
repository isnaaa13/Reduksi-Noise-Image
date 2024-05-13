from flask import Flask, render_template, request, flash
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'static/upload/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def calculate_psnr(original, noisy):
    mse = np.mean((original - noisy) ** 2)
    max_pixel = 255.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def reduce_noise(image, kernel_size, sigma):
    return cv2.medianBlur(image, kernel_size)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return render_template('index.html')
        
        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return render_template('index.html')
        
        if file:
            if file.mimetype not in ['image/jpeg', 'image/png']:
                flash('Invalid file type. Please upload JPEG or PNG file.', 'error')
                return render_template('index.html')
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            original_image = cv2.imread(filepath)

            psnrs = {}

            # Ambil nilai kernel_size dan sigma dari form
            kernel_size = int(request.form['kernel_size'])
            sigma = float(request.form['sigma'])

            # Hanya menggunakan filter median untuk mengurangi noise
            filtered_image = reduce_noise(original_image, kernel_size=kernel_size, sigma=sigma)
            psnrs["median"] = calculate_psnr(original_image, filtered_image)
                 
            # Save filtered image to the folder with the filter name
            filtered_filename = 'median_{}'.format(filename)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], filtered_filename), filtered_image)

            return render_template('result.html', filename=filename, psnrs=psnrs)

if __name__ == '__main__':
    app.run(debug=True)
