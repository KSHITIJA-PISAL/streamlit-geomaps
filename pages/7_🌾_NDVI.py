import streamlit as st
import leafmap.foliumap as leafmap
import requests
from folium.plugins import Draw
import json
st.set_page_config(layout="wide")

# API base URL
webservice_api_base =  "https://gis.mahapocra.gov.in/webservices" #"http://172.23.108.64/webservices"

markdown = """
A Streamlit map template
<https://github.com/opengeos/streamlit-map-template>
"""
st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

# Title and description
st.title("Generating NDVI")
st.markdown("""
This app is a demonstration of generating Normalized Difference Vegetation Index based on the Area of Interest (AOI) selected by the user.
""")

with st.expander("See demo"):
    st.video("Assets/NDVI_demo.mp4")

row1_col1, row1_col2 = st.columns([3, 1])
width = None
height = 700
tiles = None

with row1_col2:

    # Function to fetch districts from the API
    def load_districts():
        api_endpoint = f"{webservice_api_base}/get_districts"
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            data = response.json()
            districts = data.get("data", [])
            return [(district['dtncode'], district['dtname'], district['xmax'], district['xmin'],district['ymax'],district['ymin']) for district in districts]
        except requests.exceptions.RequestException as e:
            st.error(f"Error loading districts: {e}")
            return []

    # Function to fetch talukas for the selected district
    def load_talukas(dtncode):
        api_endpoint = f"{webservice_api_base}/get_talukas?dtncode={dtncode}"
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            data = response.json()
            talukas = data.get("data", [])
            return [(taluka['thncode'], taluka['thname'], taluka['xmax'], taluka['xmin'],taluka['ymax'],taluka['ymin']) for taluka in talukas]
        except requests.exceptions.RequestException as e:
            st.error(f"Error loading talukas: {e}")
            return []

    # Function to fetch villages for the selected taluka
    def load_villages(thncode):
        api_endpoint = f"{webservice_api_base}/get_villages?thncode={thncode}"
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            data = response.json()
            villages = data.get("data", [])
            return [(village['vincode'], village['vlname'], village['xmax'], village['xmin'],village['ymax'],village['ymin']) for village in villages]
        except requests.exceptions.RequestException as e:
            st.error(f"Error loading villages: {e}")
            return []

    # District selection
    districts = load_districts()
    district_name = st.selectbox("Select District", [district[1] for district in districts], on_change= None)

    # Taluka selection based on the selected district
    selected_district_code = next(district[0] for district in districts if district[1] == district_name)
    talukas = load_talukas(selected_district_code)
    taluka_name = st.selectbox("Select Taluka", [taluka[1] for taluka in talukas], on_change= None)

    # Village selection based on the selected taluka
    selected_taluka_code = next(taluka[0] for taluka in talukas if taluka[1] == taluka_name)
    villages = load_villages(selected_taluka_code)
    village_name = st.selectbox("Select Village", [village[1] for village in villages], on_change= None)

with row1_col1:
    AOI= st.file_uploader('Upload geojson file of the AOI', ['geojson'], accept_multiple_files=False, )
    # Initialize leafmap Map instance
    m = leafmap.Map(center=[18.7515, 76.7139], zoom=7, tiles="OpenStreetMap", add_zoom_control=False, add_search_control=False)

    # Initialize leafmap Draw control (leafmap has its own draw tool)
    Draw(
        draw_options={'polyline': False, 'polygon': False, 'rectangle': False, 'circle': False, 'marker': False, 'circlemarker': False},
        edit_options={'edit': False, 'remove': False},
        export=True).add_to(m)

    # Adding WMS layer from GeoServer
    m.add_wms_layer(
        url='http://gis.mahapocra.gov.in:6655/geoserver/PoCRA_Dashboard_V2/wms',
        layers='PoCRA_Dashboard_V2:mh_districts',
        name='District Border'
    )

    # Check if a file is uploaded
    if AOI is not None:
        # Read the GeoJSON file
        geojson_data = json.load(AOI)

        # Add the GeoJSON data to the map
        m.add_geojson(geojson_data, 'AOI')

    # Display the map in Streamlit
    m.to_streamlit(width, height)

