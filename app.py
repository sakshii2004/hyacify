from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

import numpy as np
from tensorflow.keras.preprocessing import image
import tensorflow as tf
from tensorflow import keras
from PIL import Image
from tensorflow.keras.models import load_model
model = load_model('model.h5')


def load_and_preprocess_single_image(image_path):
    img = Image.open(image_path).convert("RGBA")  # Ensure four channels (RGBA)
    img = img.resize((224, 224))  # Resize as needed
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    img_array = img_array[:, :, :4]  # Keep only RGB channels
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img, img_array

def predict(processed_image):
    predictions = model.predict(processed_image)
    #class_names = ['Water Lettuce', 'Heartleaf False Pickerelweed', 'Common Water Hyacinth', 'Common Duckweeds','Non-Invasive']
    predicted_class_index = np.argmax(predictions)
    return predicted_class_index
    
def prep_predict(image_path):
    prepped_image = load_and_preprocess_single_image(image_path)
    prediction = predict(prepped_image[1])
    return(prediction)

water_lettuce = "We have detected Water Lettuce. It is called Pistia stratiotes. It has distinctive floating rosette-like leaves and it may seem benign, but it poses a significant threat to aquatic ecosystems. Rapid multiplication of this invasive species leads to the formation of dense mats on the water surface, hindering sunlight penetration and depleting oxygen levels. The aggressive growth of Water Lettuce disrupts native vegetation, impacting the balance of ecosystems and jeopardizing the habitat for indigenous species. Please make a difference by reporting this to us."
pickerelweed = "We have detected Heartleaf False Pickerelweed (Monochoria korsakowii). It is an aquatic plant that appears deceptively attractive with its heart-shaped leaves and delicate purple flowers, but its presence can be threatening to aquatic ecosystems. This species is native to Asia and has found its way into various water bodies around the world, often outcompeting native vegetation and disrupting the balance of the ecosystem. This invasive plant forms dense mats on the water surface, impeding sunlight penetration and hindering the growth of native aquatic plants. Its rapid proliferation can lead to the depletion of oxygen levels in the water, adversely affecting fish and other aquatic organisms. Please make a difference by reporting this to us."
common_water = "We have detected the Common Water Hyacinth. It is scientifically known as Eichhornia crassipes, is a highly invasive aquatic plant that poses a significant threat to aquatic ecosystem. It is characterized by vibrant green leaves and distinctive lavender flowers. The Water Hyacinth may seem visually appealing, but its ecological impact is severe. This invasive plant forms dense mats on the water's surface, reducing sunlight penetration and hindering the oxygen exchange essential for aquatic life. The consequences of its unchecked growth result in the displacement of native vegetation, altered water chemistry and a decline in biodiversity. Please make a difference by reporting this to us. "
common_duckweed = "We have detected Common Duckweeds. It is also called Lemna minor, it looks harmless but can have profound and detrimental effects on local ecosystems. This plant has tiny floating fronds and it may go unnoticed, but its invasive characteristics demand attention. Featuring minute green leaves that form dense mats on the water's surface, Common Duckweeds can have a substantial impact on aquatic habitats. Despite their small size, these plants have a remarkable ability to multiply rapidly, obstructing sunlight and impeding the crucial oxygen exchange necessary for aquatic life. Common Duckweeds lack the vibrant allure of some invasive species, but their ecological consequences are equally severe. Please make a difference by reporting this to us."
non_invasive = "Great news! We have not detected any invasive species. The analysis indicates that the aquatic plant in the provided photo is identified as a non-invasive species. Non-invasive plants contribute positively to ecosystem balance and biodiversity. If you have any more photos or questions, feel free to continue using our service. Keep up the good work in promoting a healthy aquatic environment! "

descriptions = [water_lettuce, pickerelweed, common_water, common_duckweed, non_invasive]

app = Flask(__name__)
app.secret_key = 'we_will_win'  # Set your secret key here

UPLOAD_FOLDER = r'static\uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def show_homepage():
  return render_template('index.html')


@app.route("/report")
def report_location():
  return render_template('report.html')

@app.route("/impact")
def impact_testimonials():
  return render_template('testimonials.html')

@app.route("/contact-us")
def contact_us():
  return render_template('contact-us.html')

@app.route("/about-us")
def about_us():
  return render_template('about.html')


def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('detection_page', filename=filename))
        
    return render_template('test.html')

@app.route('/detection_page/<filename>')
def detection_page(filename):
   filepath = ("static/uploads/"+filename)
   pred = prep_predict(filepath)   
   return render_template("upload-predict.html", filename=filename, pred = pred, desc = descriptions)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
