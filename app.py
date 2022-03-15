import base64
from folium import IFrame
import io
import base64
from PIL import Image
import pandas as pd
import geopandas as gpd

import folium
from flask import Flask
from os import listdir
from waitress import serve

app = Flask(__name__)

def insert_marker(location, m, impath=None):
        
        encoded = base64.b64encode(open(impath, 'rb').read())

        buffer = io.BytesIO()
        imgdata = base64.b64decode(encoded)
        img = Image.open(io.BytesIO(imgdata))
        new_img = img.resize((480, 480))  # x, y
        new_img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue())

        html = '<div class="img-with-text"> <img src="data:image/png;base64,{}"> <p>{}</p> </div>'.format

        iframe = IFrame(html(img_b64.decode('UTF-8'), location['description']), width=480+40, height=480+40)
        popup = folium.Popup(iframe, max_width=520)

        folium.Marker(location=[location['lat'], location['lon']], tooltip=location["Location"], popup = popup, 
        icon=folium.Icon(color = 'gray')).add_to(m) 

@app.route('/ireland')
def render_map():
    m = folium.Map(location=[52.3429054,-7.2714076], zoom_start=7.4)

    trip_locations = pd.read_csv("locations1.csv")
    trip_locations['geometry'] = gpd.points_from_xy(trip_locations['lon'], trip_locations['lat'])

    points = []
    for i in range(len(trip_locations)):
        points.append([trip_locations.iloc[i]['lat'], trip_locations.iloc[i]['lon']])
        
        image_list = listdir("image_locations/" + trip_locations.iloc[i]["Location"])
        if len(image_list) > 0:
            path = 'image_locations/' + trip_locations.iloc[i]["Location"] + '/' + image_list[0]
        else:
            path = 'image_locations\\Dunmore head, Kerry, Ireland\\IMG_2546.JPEG'
        insert_marker(trip_locations.iloc[i], m, impath=path)

    ls = folium.PolyLine(points, color='blue')
    ls.add_child(folium.Popup("outline Popup on Polyline"))
    ls.add_to(m)

    return m._repr_html_()	
	
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=6001, threads=1)
    # app.run(debug = False)   