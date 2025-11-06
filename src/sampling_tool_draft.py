import streamlit as st
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import json
import geopandas as gpd
from shapely.geometry import shape, Point, Polygon
import pandas as pd
import zipfile
import tempfile
import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
from PIL import Image
import io
import base64

# --- Configuration and Initialization ---

st.set_page_config(layout="wide", page_title="LULC Digitization Tool")

st.title("Interactive LULC Digitization")
st.markdown("Select an LULC class, draw a feature (Point or Polygon) on the map, and the data will be captured and tagged.")

# Initialize session state
if 'sampling_data' not in st.session_state:
    st.session_state.sampling_data = {'type': 'FeatureCollection', 'features': []}
if 'feature_count' not in st.session_state:
    st.session_state.feature_count = 0
if 'last_recorded_feature' not in st.session_state:
    st.session_state.last_recorded_feature = None
if 'classes_df' not in st.session_state:
    st.session_state.classes_df = None
if 'AOI_GDF' not in st.session_state:
    st.session_state.AOI_GDF = None
if 'geotiff_bounds' not in st.session_state:
    st.session_state.geotiff_bounds = None
if 'geotiff_overlay' not in st.session_state:
    st.session_state.geotiff_overlay = None
if 'center_lat' not in st.session_state:
    st.session_state.center_lat = 0  
if 'center_lon' not in st.session_state:
    st.session_state.center_lon = 0 
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 2 
if 'initial_fit_done' not in st.session_state:
    st.session_state.initial_fit_done = False
if 'LULCTable' not in st.session_state:
    st.session_state.LULCTable = None
if 'training_gdf' not in st.session_state:
    st.session_state.training_gdf = None
if 'TrainField' not in st.session_state:
    st.session_state.TrainField = None

# --- Top Section: Layer Upload and LULC Class Selection ---
st.markdown("---")
st.subheader("Configuration")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("**Upload LULC Classes (CSV)**")
    csv_file = st.file_uploader(
        "CSV File",
        type=['csv'],
        help="CSV should have columns: ID, LULC_Type, color_palette (hexcode format: #RRGGBB)",
        label_visibility="collapsed"
    )
    
    if csv_file is not None:
        try:
            df_lulc = pd.read_csv(csv_file)
            required_cols = ['ID', 'LULC_Type', 'color_palette']
            if all(col in df_lulc.columns for col in required_cols):
                def is_valid_hex(color):
                    if isinstance(color, str) and color.startswith('#') and len(color) == 7:
                        try:
                            int(color[1:], 16)
                            return True
                        except ValueError:
                            return False
                    return False
                
                invalid_colors = df_lulc[~df_lulc['color_palette'].apply(is_valid_hex)]
                if not invalid_colors.empty:
                    st.error(f"Invalid hex colors in rows: {invalid_colors['ID'].tolist()}")
                    st.session_state.classes_df = None
                else:
                    st.session_state.classes_df = dict(zip(df_lulc['LULC_Type'], df_lulc['color_palette']))
                    st.session_state.LULCTable = df_lulc  # Store the DataFrame for later use
                    st.success(f"✓ Loaded {len(st.session_state.classes_df)} classes")
            else:
                st.error(f"CSV must contain: {', '.join(required_cols)}")
                st.session_state.classes_df = None
                st.session_state.LULCTable = None
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            st.session_state.classes_df = None
            st.session_state.LULCTable = None

with col2:
    st.markdown("**Upload Training Data (Shapefile ZIP)**")
    training_file = st.file_uploader(
        "Training Shapefile ZIP",
        type=['zip'],
        help="Upload existing training data as ZIP file containing .shp, .shx, .dbf, and .prj files",
        label_visibility="collapsed"
    )

    if training_file is not None:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(training_file, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                shp_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
                if shp_files:
                    shp_path = os.path.join(tmpdir, shp_files[0])
                    training_gdf = gpd.read_file(shp_path)
                    
                    # Show field selection for class field
                    st.markdown("**Select Class Field:**")
                    class_field = st.selectbox(
                        "Class Field",
                        options=training_gdf.columns.tolist(),
                        help="Select the field that contains LULC class names or IDs",
                        label_visibility="collapsed"
                    )
                    
                    if st.button("Load Training Data", use_container_width=True):
                        st.session_state.training_gdf = training_gdf
                        st.session_state.TrainField = class_field
                        
                        # Convert existing training data to the same format as drawn features
                        existing_features = []
                        for idx, row in training_gdf.iterrows():
                            feature = {
                                'type': 'Feature',
                                'geometry': row.geometry.__geo_interface__,
                                'properties': {
                                    'feature_id': idx + 1,
                                    'LULC_Class': str(row[class_field]),
                                    'Class_Color': '#FF0000',  
                                    'LULC_ID': idx + 1,  
                                    'source': 'uploaded' 
                                }
                            }
                            existing_features.append(feature)
                        
                        # Add existing features to sampling_data
                        st.session_state.sampling_data['features'].extend(existing_features)
                        st.session_state.feature_count = len(st.session_state.sampling_data['features'])
                        
                        st.success(f"✓ Loaded {len(existing_features)} training features")
                        st.rerun()
                else:
                    st.error("No .shp file found in ZIP")
        except Exception as e:
            st.error(f"Error loading training data: {e}")

with col3:
    st.markdown("**Upload AOI (Shapefile ZIP)**")
    aoi_file = st.file_uploader(
        "AOI Shapefile ZIP",
        type=['zip'],
        help="Upload a ZIP file containing .shp, .shx, .dbf, and .prj files",
        label_visibility="collapsed"
    )
    
    if aoi_file is not None:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(aoi_file, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
                
                shp_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
                if shp_files:
                    shp_path = os.path.join(tmpdir, shp_files[0])
                    st.session_state.AOI_GDF = gpd.read_file(shp_path)
                    
                    # Set map center and zoom based on AOI
                    if st.session_state.AOI_GDF.crs and st.session_state.AOI_GDF.crs != 'EPSG:4326':
                        aoi_wgs84 = st.session_state.AOI_GDF.to_crs('EPSG:4326')
                    else:
                        aoi_wgs84 = st.session_state.AOI_GDF
                    
                    # Calculate center from AOI bounds
                    bounds = aoi_wgs84.total_bounds
                    center_lat = (bounds[1] + bounds[3]) / 2
                    center_lon = (bounds[0] + bounds[2]) / 2
                    st.session_state.center_lat = center_lat
                    st.session_state.center_lon = center_lon
                    
                    # Calculate appropriate zoom level based on AOI size
                    lat_diff = bounds[3] - bounds[1]
                    lon_diff = bounds[2] - bounds[0]
                    max_diff = max(lat_diff, lon_diff)
                    
                    if max_diff > 10:
                        zoom = 6
                    elif max_diff > 5:
                        zoom = 7
                    elif max_diff > 2:
                        zoom = 8
                    elif max_diff > 1:
                        zoom = 9
                    elif max_diff > 0.5:
                        zoom = 10
                    elif max_diff > 0.1:
                        zoom = 11
                    elif max_diff > 0.05:
                        zoom = 12
                    else:
                        zoom = 13
                    
                    st.session_state.map_zoom = zoom
                    st.session_state.initial_fit_done = False 
                    
                    st.success(f"✓ AOI: {len(st.session_state.AOI_GDF)} feature(s)")
                else:
                    st.error("No .shp file found in ZIP")
                    st.session_state.AOI_GDF = None
        except Exception as e:
            st.error(f"Error loading shapefile: {e}")
            st.session_state.AOI_GDF = None

with col4:
    st.markdown("**Upload Custom Basemap (GeoTIFF)**")
    geotiff_file = st.file_uploader(
        "GeoTIFF File",
        type=['tif', 'tiff'],
        help="Upload a georeferenced GeoTIFF file",
        label_visibility="collapsed"
    )
    
    if geotiff_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_file:
                tmp_file.write(geotiff_file.read())
                tmp_path = tmp_file.name
            
            with rasterio.open(tmp_path) as src:
                data = src.read()
                bounds = src.bounds
                
                st.info(f"📊 GeoTIFF Info: {data.shape[0]} bands, {data.shape[1]}x{data.shape[2]} pixels, dtype: {data.dtype}")
                
                if data.shape[0] >= 3:
                    img_data = np.dstack([data[0], data[1], data[2]])
                else:
                    img_data = data[0]
                
                # Use percentile-based scaling for better contrast
                if data.dtype == np.uint8:
                    # Already 0-255, just handle NaN
                    img_data = np.nan_to_num(img_data, nan=0)
                elif data.dtype == np.uint16:
                    # Scale from 16-bit to 8-bit
                    img_data = np.nan_to_num(img_data, nan=0)
                    # Use percentile-based scaling for better contrast
                    p2, p98 = np.percentile(img_data[img_data > 0], [2, 98])
                    img_data = np.clip((img_data - p2) / (p98 - p2) * 255, 0, 255)
                else:
                    # Float or other types - use percentile scaling
                    img_data = np.nan_to_num(img_data, nan=0)
                    valid_data = img_data[img_data > 0]
                    if len(valid_data) > 0:
                        p2, p98 = np.percentile(valid_data, [2, 98])
                        img_data = np.clip((img_data - p2) / (p98 - p2) * 255, 0, 255)
                    else:
                        img_data = np.zeros_like(img_data)
                
                img_data = img_data.astype(np.uint8)
                
                if len(img_data.shape) == 3:
                    img = Image.fromarray(img_data, mode='RGB')
                else:
                    img = Image.fromarray(img_data, mode='L')
                
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                st.session_state.geotiff_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
                st.session_state.geotiff_overlay = f"data:image/png;base64,{img_base64}"
                
                st.success("✓ GeoTIFF loaded")
            
            os.unlink(tmp_path)
        except Exception as e:
            st.error(f"Error loading GeoTIFF: {e}")
            st.session_state.geotiff_bounds = None
            st.session_state.geotiff_overlay = None


with col5:
    st.markdown("**Clear Layers**")
    if st.button("🗑️ Clear Uploaded Layers", use_container_width=True):
        st.session_state.AOI_GDF = None
        st.session_state.geotiff_bounds = None
        st.session_state.geotiff_overlay = None
        st.session_state.training_gdf = None
        st.session_state.TrainField = None
        st.session_state.center_lat = 0
        st.session_state.center_lon = 0
        st.session_state.map_zoom = 2
        st.session_state.initial_fit_done = False
        st.success("Layers cleared!")
        st.rerun()

# Use default classes if no CSV loaded
if st.session_state.classes_df is None:
    classes_df = {
        "Urban/Built-up": "#FF0000",
        "Agriculture": "#FFA500",
        "Forest": "#008000",
        "Water": "#0000FF",
        "Wetlands": "#800080"
    }
else:
    classes_df = st.session_state.classes_df

# Update existing training data colors and IDs if CSV is loaded
if st.session_state.classes_df is not None and st.session_state.LULCTable is not None:
    for feature in st.session_state.sampling_data['features']:
        if feature['properties'].get('source') == 'uploaded':
            class_name = feature['properties']['LULC_Class']
            matching_row = st.session_state.LULCTable[st.session_state.LULCTable['LULC_Type'] == class_name]
            if not matching_row.empty:
                feature['properties']['Class_Color'] = matching_row['color_palette'].iloc[0]
                feature['properties']['LULC_ID'] = int(matching_row['ID'].iloc[0])
            else:
                # Use default color if class not found in CSV
                feature['properties']['Class_Color'] = classes_df.get(class_name, '#808080')

# --- LULC Class Selection ---
st.markdown("---")
col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 2])

with col_a:
    selected_class = st.selectbox(
        "**Select LULC Class for Drawing:**",
        options=list(classes_df.keys())
    )

# --- Training Data Summary ---
if st.session_state.training_gdf is not None and st.session_state.sampling_data['features']:
    st.markdown("---")
    st.subheader("Training Data Summary")
    
    # Create summary table
    try:
        gdf_summary = gpd.GeoDataFrame.from_features(st.session_state.sampling_data['features'])
        
        # Group by class and source
        summary_data = []
        for class_name in classes_df.keys():
            class_features = gdf_summary[gdf_summary['LULC_Class'] == class_name]
            uploaded_count = len(class_features[class_features.get('source', '') == 'uploaded'])
            digitized_count = len(class_features[class_features.get('source', '') != 'uploaded'])
            total_count = len(class_features)
            
            summary_data.append({
                'LULC Class': class_name,
                'Uploaded': uploaded_count,
                'Digitized': digitized_count,
                'Total': total_count,
                'Color': classes_df[class_name]
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Display summary with colors
        col_summary1, col_summary2 = st.columns([3, 1])
        
        with col_summary1:
            st.markdown("**Sample Count by Class:**")
            display_summary = summary_df[['LULC Class', 'Uploaded', 'Digitized', 'Total']].copy()
            st.dataframe(display_summary, use_container_width=True, hide_index=True)
        
        with col_summary2:
            st.markdown("**Class Colors:**")
            for _, row in summary_df.iterrows():
                if row['Total'] > 0:
                    st.markdown(f"<span style='color: {row['Color']}; font-size: 16px;'>●</span> {row['LULC Class']}", unsafe_allow_html=True)
        
        # Overall statistics
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("Total Samples", summary_df['Total'].sum())
        with col_stat2:
            st.metric("Uploaded Samples", summary_df['Uploaded'].sum())
        with col_stat3:
            st.metric("Digitized Samples", summary_df['Digitized'].sum())
        with col_stat4:
            st.metric("Active Classes", len(summary_df[summary_df['Total'] > 0]))
            
    except Exception as e:
        st.error(f"Error creating summary: {e}")

# --- Map Layer Controls ---
st.markdown("---")
st.subheader("Map Layers")
col1, col2, col3 = st.columns(3)

with col1:
    basemap_option = st.selectbox(
        "**Basemap:**",
        options=[
            "CartoDB Dark",
            "Satellite (ESRI)",
            "Satellite (Google)",
            "OpenStreetMap",
            "CartoDB Positron"
        ]
    )

with col2:
    show_aoi = st.checkbox("Show AOI Layer", value=True, disabled=st.session_state.AOI_GDF is None)

with col3:
    show_geotiff = st.checkbox("Show Custom Basemap", value=True, disabled=st.session_state.geotiff_overlay is None)

# --- Folium Map Setup ---

# Initialize the map with selected basemap
map_center = [st.session_state.center_lat, st.session_state.center_lon]
if basemap_option == "Satellite (ESRI)":
    m = folium.Map(
        location=map_center,
        zoom_start=st.session_state.map_zoom,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI"
    )
elif basemap_option == "Satellite (Google)":
    m = folium.Map(
        location=map_center,
        zoom_start=st.session_state.map_zoom,
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google"
    )
elif basemap_option == "OpenStreetMap":
    m = folium.Map(location=map_center, zoom_start=st.session_state.map_zoom, tiles="OpenStreetMap")
elif basemap_option == "CartoDB Dark":
    m = folium.Map(location=map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB dark_matter")
else: 
    m = folium.Map(location=map_center, zoom_start=st.session_state.map_zoom, tiles="CartoDB positron")

# Add GeoTIFF overlay if available and enabled
if show_geotiff and st.session_state.geotiff_overlay is not None:
    folium.raster_layers.ImageOverlay(
        image=st.session_state.geotiff_overlay,
        bounds=st.session_state.geotiff_bounds,
        opacity=0.8,
        name="Custom Basemap"
    ).add_to(m)

# Add AOI layer if available and enabled
if show_aoi and st.session_state.AOI_GDF is not None:
    try:
        if st.session_state.AOI_GDF.crs and st.session_state.AOI_GDF.crs != 'EPSG:4326':
            aoi_gdf_wgs84 = st.session_state.AOI_GDF.to_crs('EPSG:4326')
        else:
            aoi_gdf_wgs84 = st.session_state.AOI_GDF
        
        folium.GeoJson(
            aoi_gdf_wgs84,
            name="AOI Layer",
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': '#FFD700',
                'weight': 3,
                'dashArray': '5, 5',
                'fillOpacity': 0.1
            },
            tooltip="Area of Interest"
        ).add_to(m)
        
        if not st.session_state.initial_fit_done and st.session_state.AOI_GDF is not None:
            bounds = aoi_gdf_wgs84.total_bounds
            m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
            st.session_state.initial_fit_done = True
    except Exception as e:
        st.error(f"Error displaying AOI: {e}")

# Create a feature group for drawn features
feature_group = folium.FeatureGroup(name="LULC Features")

# Add existing features to the map
if st.session_state.sampling_data['features']:
    for feature in st.session_state.sampling_data['features']:
        geom_type = feature['geometry']['type']
        color = feature['properties'].get('Class_Color', '#808080')
        
        if geom_type == 'Point':
            coords = feature['geometry']['coordinates']
            folium.Marker(
                location=[coords[1], coords[0]],
                icon=folium.Icon(color='white', icon_color=color, icon='circle', prefix='fa'),
                popup=f"Feature ID: {feature['properties'].get('feature_id', feature['properties'].get('id', 'N/A'))}<br>LULC ID: {feature['properties'].get('LULC_ID', 'N/A')}<br>LULC: {feature['properties'].get('LULC_Class', 'Unknown')}"
            ).add_to(feature_group)
        
        elif geom_type == 'Polygon':
            coordinates = feature['geometry']['coordinates'][0]
            latlngs = [[coord[1], coord[0]] for coord in coordinates]
            
            folium.Polygon(
                locations=latlngs,
                color=color,
                fill_color=color,
                fill_opacity=0.4,
                weight=3,
                popup=f"Feature ID: {feature['properties'].get('feature_id', feature['properties'].get('id', 'N/A'))}<br>LULC ID: {feature['properties'].get('LULC_ID', 'N/A')}<br>LULC: {feature['properties'].get('LULC_Class', 'Unknown')}"
            ).add_to(feature_group)

feature_group.add_to(m)

# Define the Draw Control
draw_options = {
    'polyline': False,
    'rectangle': False,
    'circle': False,
    'circlemarker': False,
    'marker': True,
    'polygon': {
        "allowIntersection": False, 
        "shapeOptions": {
            "color": classes_df[selected_class], 
            "fillColor": classes_df[selected_class], 
            "fillOpacity": 0.5
        }
    },
}

draw_control = Draw(
    export=False,
    position='topleft',
    draw_options=draw_options,
    edit_options={'edit': False, 'remove': False}
)
draw_control.add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# --- Render Map  ---

map_output = st_folium(
    m,
    width=None,
    height=600,
    key="folium_map",
    returned_objects=["last_active_drawing", "center", "zoom"]
)

# Store current map state
if map_output:
    if map_output.get("center"):
        st.session_state.center_lat = map_output["center"]["lat"]
        st.session_state.center_lon = map_output["center"]["lng"]
    if map_output.get("zoom"):
        st.session_state.map_zoom = map_output["zoom"]

# --- Processing and Storing Captured Data ---

if map_output and map_output.get("last_active_drawing"):
    new_feature = map_output["last_active_drawing"]
    
    if new_feature['geometry'] != st.session_state.last_recorded_feature:
        st.session_state.feature_count += 1
        
        if 'properties' not in new_feature:
            new_feature['properties'] = {}
            
        new_feature['properties']['feature_id'] = st.session_state.feature_count
        new_feature['properties']['LULC_Class'] = selected_class
        new_feature['properties']['Class_Color'] = classes_df[selected_class]
        new_feature['properties']['source'] = 'digitized'  # Mark as digitized data
        
        # Get LULC ID from the stored DataFrame if available
        if st.session_state.LULCTable is not None:
            try:
                lulc_id = st.session_state.LULCTable[st.session_state.LULCTable['LULC_Type'] == selected_class]['ID'].iloc[0]
                new_feature['properties']['LULC_ID'] = int(lulc_id)
            except (IndexError, KeyError):
                # Fallback to default if class not found
                default_lulc_ids = {
                    "Urban/Built-up": 1,
                    "Agriculture": 2,
                    "Forest": 3,
                    "Water": 4,
                    "Wetlands": 5
                }
                new_feature['properties']['LULC_ID'] = default_lulc_ids.get(selected_class, 0)
        else:
            # Use a default mapping for built-in classes
            default_lulc_ids = {
                "Urban/Built-up": 1,
                "Agriculture": 2,
                "Forest": 3,
                "Water": 4,
                "Wetlands": 5
            }
            new_feature['properties']['LULC_ID'] = default_lulc_ids.get(selected_class, 0)
        
        st.session_state.sampling_data['features'].append(new_feature)
        st.session_state.last_recorded_feature = new_feature['geometry']
        
        st.success(f"✓ Captured Feature #{st.session_state.feature_count}: **{selected_class}** ({new_feature['geometry']['type']})")
        st.rerun()

# --- Display Results Side by Side ---

st.markdown("---")
st.subheader("Recorded LULC Features")

if st.session_state.sampling_data['features']:
    try:
        gdf = gpd.GeoDataFrame.from_features(st.session_state.sampling_data['features'])

        if 'feature_id' in gdf.columns:
            gdf_display = gdf[['feature_id', 'LULC_ID', 'LULC_Class', 'Class_Color']].copy()
        else:
            gdf_display = gdf[['id', 'LULC_Class']].copy()
            gdf_display['feature_id'] = gdf_display['id']
            
            # Add LULC_ID if missing
            if 'LULC_ID' not in gdf_display.columns:
                default_lulc_ids = {
                    "Urban/Built-up": 1,
                    "Agriculture": 2,
                    "Forest": 3,
                    "Water": 4,
                    "Wetlands": 5
                }
                gdf_display['LULC_ID'] = gdf_display['LULC_Class'].map(default_lulc_ids).fillna(0).astype(int)
            
            # Add Class_Color if missing
            if 'Class_Color' not in gdf_display.columns:
                gdf_display['Class_Color'] = '#808080'  # Default color
            
            gdf_display = gdf_display[['feature_id', 'LULC_ID', 'LULC_Class', 'Class_Color']].copy()
        
        # Add source field
        gdf_display['Source'] = gdf['source'].fillna('digitized').apply(
            lambda x: 'Uploaded' if x == 'uploaded' else 'Digitized'
        )
        
        gdf_display['Geometry_Type'] = gdf.geometry.apply(lambda geom: geom.geom_type)
        gdf_display['Geometry'] = gdf.geometry.apply(lambda geom: geom.wkt)
        
        # Reorder columns: LULC_ID, LULC_Class, Class_Color, Feature_ID, Source, Geometry_Type, Geometry
        gdf_display = gdf_display[['LULC_ID', 'LULC_Class', 'Class_Color', 'feature_id', 'Source', 'Geometry_Type', 'Geometry']]
        
        # Rename columns for better display
        gdf_display = gdf_display.rename(columns={
            'LULC_ID': 'LULC ID',
            'LULC_Class': 'LULC Class',
            'Class_Color': 'Class Color',
            'feature_id': 'Feature ID',
            'Geometry_Type': 'Geometry Type'
        })
        
        # Side by side layout: Table and Delete
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            st.markdown("**Feature Table**")
            st.dataframe(gdf_display, use_container_width=True, hide_index=True, height=300)
        
        with col_right:
            st.markdown("**Delete Feature**")
            feature_ids = gdf_display['Feature ID'].tolist()
            selected_feature_id = st.selectbox("Select Feature ID:", feature_ids, label_visibility="collapsed")
            
            if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
                st.session_state.sampling_data['features'] = [
                    f for f in st.session_state.sampling_data['features']
                    if f['properties'].get('feature_id', f['properties'].get('id')) != selected_feature_id
                ]
                st.success(f"Deleted Feature ID #{selected_feature_id}")
                st.rerun()
            
            st.markdown("---")
            
        # Statistics in horizontal layout
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Features", len(gdf_display))
        with col2:
            st.metric("LULC Classes", gdf_display['LULC Class'].nunique())
        with col3:
            points = len(gdf_display[gdf_display['Geometry Type'] == 'Point'])
            st.metric("Points", points)
        with col4:
            polygons = len(gdf_display[gdf_display['Geometry Type'] == 'Polygon'])
            st.metric("Polygons", polygons)

        # Download buttons
        st.markdown("---")
        st.subheader("Download Data")
        
        col_a, col_b, col_c = st.columns([1, 1, 2])
        
        with col_a:
            # GeoJSON download
            geojson_str = json.dumps(st.session_state.sampling_data, indent=2)
            st.download_button(
                label="📥 Download GeoJSON",
                data=geojson_str,
                file_name="LULC_digitization_data.geojson",
                mime="application/json",
                use_container_width=True
            )
        
        with col_b:
            # Earth Engine FeatureCollection format
            ee_features = []
            for feature in st.session_state.sampling_data['features']:
                ee_feature = {
                    "type": "Feature",
                    "geometry": feature['geometry'],
                    "properties": {
                        "LULC_ID": int(feature['properties'].get('LULC_ID', 0)),
                        "LULC_Class": str(feature['properties']['LULC_Class']),
                        "Class_Color": str(feature['properties']['Class_Color']),
                        "feature_id": int(feature['properties'].get('feature_id', feature['properties'].get('id', 0)))
                    }
                }
                ee_features.append(ee_feature)
            
            ee_fc = {
                "type": "FeatureCollection",
                "columns": {
                    "LULC_ID": "Integer",
                    "LULC_Class": "String",
                    "Class_Color": "String",
                    "feature_id": "Integer"
                },
                "features": ee_features
            }
            
            ee_str = json.dumps(ee_fc, indent=2)
            st.download_button(
                label="📥 Download EE FeatureCollection",
                data=ee_str,
                file_name="LULC_digitization_ee_fc.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_c:
            if st.button("🗑️ Clear All Data", type="primary", use_container_width=True):
                st.session_state.sampling_data = {'type': 'FeatureCollection', 'features': []}
                st.session_state.feature_count = 0
                st.session_state.last_recorded_feature = None
                st.success("All data cleared!")
                st.rerun()
        
    except Exception as e:
        st.error(f"Error processing GeoJSON data: {e}")
        st.json(st.session_state.sampling_data)
else:
    st.info("Start drawing points or polygons on the map to collect LULC data. The table will appear here.")