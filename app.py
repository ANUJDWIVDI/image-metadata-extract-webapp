
from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
from PIL.ExifTags import TAGS
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Home page with upload button
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if file was uploaded
    if 'image' not in request.files:
        print("NO IMAGE UPLOADED")
        return redirect(url_for('home'))
    file = request.files['image']
    # Check if file has valid extension
    if not allowed_file(file.filename):
        print(" TYPE NOT ALLOWED")
        return redirect(url_for('home'))
    # Save file and get metadata
    filename = secure_filename(file.filename)
    image_path = os.path.abspath(os.path.join(app.root_path, 'static', 'uploads', filename))
    file.save(image_path)
    metadata = get_metadata(image_path)

    print("CHECKING METADATA")
    metadata = get_metadata(image_path)

    print(metadata)

    if metadata is None:
        return render_template('home.html', prev='Unable to extract metadata from that image try another')

    print("Getting map urls")
    map_url = get_map_url(metadata['lat'], metadata['lon'])
    image_url = url_for('static', filename=f'uploads/{filename}')
    return render_template('result.html', map_url=map_url, image_url=image_url, map_metadata=metadata)


# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Map APIs
def get_map_url(lat, lon):
    # Mapbox
    mapbox_access_token = "p.rGwEmY1gTbDxGnPSX_nd6w"
    if mapbox_access_token:
        return f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/static/pin-s+ff0000({lon},{lat})/{lon},{lat},13,0/300x200?access_token={mapbox_access_token}'
    return None

# Extract metadata from image
def get_metadata(image_path):
    print("ENTER GET - METADATA")
    try:
        print("------ TRY ENTER ------")
        with Image.open(image_path) as img:
            print("IMAGE OPEN")
            exif_data={}
            info = img._getexif()
            if info is None:
                print(" ------- No EXIF DATA FOUND -----")
                return None
            else:
                print(" -------XXXXXXXXXXXXXX   EXIF DATA FOUND    XXXXXXXXXXXXXXX-----")
                print(info)
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    exif_data[decoded] = value

                camera_make = exif_data.get('Make')
                camera_model = exif_data.get('Model')
                software = exif_data.get('Software')
                date_time_original = exif_data.get('DateTimeOriginal')
                latitude = exif_data.get(34853)[2][0][0] / exif_data.get(34853)[2][0][1] if 34853 in exif_data else None
                longitude = exif_data.get(34853)[4][0][0] / exif_data.get(34853)[4][0][1] if 34853 in exif_data else None

                metadata = {
                    'camera_make': camera_make,
                    'camera_model': camera_model,
                    'software': software,
                    'date_time_original': date_time_original,
                    'lat': latitude,
                    'lon': longitude
                }

                return metadata
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':
    app.run(debug=True)

