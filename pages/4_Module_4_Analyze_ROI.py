"""
Module 4: Spectral Separability Analysis

This module facilitate the user to perform spectral separability analysis for their training data

Architecture:
- Backend (module_4.py and module_4_part2.py): Pure backend process without UI dependencies
- Frontend (this file): Streamlit UI with session state management
- State synchronization ensures data persistence across page interactions
"""

import streamlit as st
from epistemx.shapefile_utils import shapefile_validator, EE_converter
from epistemx.module_4 import sample_quality
from epistemx.module_4_part2 import spectral_plotter
from modules.nav import Navbar
import matplotlib.pyplot as plt
import numpy as np
import geemap.foliumap as geemap
import geopandas as gpd
import traceback
import tempfile
import zipfile
import os

#Page configuration
st.set_page_config(
    page_title="Perform ROI Analysis", #visible in the browser
    page_icon="logos/logo_epistem_crop.png",
    layout="wide"
)

# Load custom CSS
def load_css():
    """Load custom CSS for EpistemX theme"""
    try:
        with open('.streamlit/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Apply custom theme
load_css()

#title of the module
st.title("Analisis Pemisahan Data Area Sampel (Region of Interest/ROI)")
st.divider()
st.markdown("""Modul ini memungkinkan pengguna melakukan analisis keterpisahan antar kelas tutupan/penggunaan lahan di dalam wilayah analisis yang anda tentukan. 
Sebelum melakukan analisis, pengguna harus mengunggah data referensi tiap-tiap kelas tutupan/penggunaan lahan yang sudah ditentukan dalam format yang kompatibel. 
Data ini harus memuat ID kelas unik dan nama kelas yang sesuai. Setelah data referensi diunggah, 
pengguna dapat melakukan analisis keterpisahan dengan langkah-langkah berikut:""")
st.markdown("1. Pilih attibute data latih, yaitu ID dan nama kelas")
st.markdown("2. Pilih parameter keterpisahan yang terdiri dari resolusi spasial dan jumlah maksimum piksel untuk setiap kelas. Platform ini menggunakan metode Transformed Divergence (TD) untuk melakukan analisis keterpisahan")

# Add navigation sidebar
Navbar()

st.markdown("Ketersedian gabungan citra satelit dari modul 1")
#Check if landsat data from module 1 is available
if 'composite' in st.session_state:
    st.success("Gabungan citra satelit tersedia!")
    # Display information about available imagery
    if 'collection_metadata' in st.session_state:
        metadata = st.session_state['Image_metadata']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jumlah Citra", metadata.get('total_images', 'N/A'))
        with col2:
            st.metric("Periode Perekaman", metadata.get('date_range', 'N/A'))
        with col3:
            st.metric("Rata - Rata Tutupan Awan", f"{metadata.get('cloud_cover', {}).get('mean', 'N/A')}%")
#Preview the landsat mosaic
    if st.checkbox("Pratinjau Gabungan Citra Satelit"):
        composite = st.session_state['composite']
        vis_params = st.session_state['visualization']
        aoi = st.session_state['AOI']
        centroid = aoi.geometry.centroid.iloc[0]
        m = geemap.Map(center=[centroid.y, centroid.x], zoom=7)
        m.addLayer(composite, vis_params, "Landsat Mosaic")
        m.addLayer(aoi, {}, "AOI", True, 0.5)
        m.to_streamlit(height=600)
else:
    st.warning("Gabungan Citra Satelit tidak ditemukan. Mohon jalankan Modul 1 terlebih dahulu.")
    st.stop()
st.divider()
#User input ROI upload
st.subheader("A. Unggah Wilayah Minat (Shapefile)")
st.markdown("saat ini platform hanya mendukung shapefile dalam format .zip")
uploaded_file = st.file_uploader("Unggah area minat dalam berkas zip (.zip)", type=["zip"])
aoi = None
#define AOI upload function
if uploaded_file:
    # Extract the uploaded zip file to a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # write uploaded bytes to disk (required before reading zip)
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Find the .shp file in the extracted files (walk subfolders)
        shp_files = []
        for root, _, files in os.walk(tmpdir):
            for fname in files:
                if fname.lower().endswith(".shp"):
                    shp_files.append(os.path.join(root, fname))

        if len(shp_files) == 0:
            st.error("No .shp file found in the uploaded zip.")
        else:
            try:
                # Read the shapefile
                gdf = gpd.read_file(shp_files[0])
                st.success("ROI loaded successfully!")
                validate = shapefile_validator(verbose=False)
                converter = EE_converter(verbose=False)
                st.markdown("ROI table preview:")
                st.write(gdf)
                # Validate and fix geometry
                gdf_cleaned = validate.validate_and_fix_geometry(gdf, geometry="mixed")
                
                if gdf_cleaned is not None:
                    # Convert to EE geometry safely
                    aoi = converter.convert_roi_gdf(gdf_cleaned)
                    
                    if aoi is not None:
                        st.success("ROI conversion completed!")
                        # Show a small preview map centered on AOI
                        # Store in session state
                        st.session_state['training_data'] = aoi
                        st.session_state['training_gdf'] = gdf_cleaned
                        st.text("Region of Interest distribution:")
                        centroid = gdf_cleaned.geometry.centroid.iloc[0]
                        preview_map = geemap.Map(center=[centroid.y, centroid.x], zoom=6)
                        preview_map.add_geojson(gdf_cleaned.__geo_interface__, layer_name="AOI")
                        preview_map.to_streamlit(height=600)
                    else:
                        st.error("Failed to convert ROI to Google Earth Engine format")
                else:
                    st.error("Geometry validation failed")
                    
            except Exception as e:
                st.error(f"Error reading shapefile: {e}")
                st.info("Make sure your shapefile includes all necessary files (.shp, .shx, .dbf, .prj)")
st.divider()
#Training data separability analysis
#Used the previously uploaded ROI
if "training_gdf" in st.session_state:
    gdf_cleaned = st.session_state["training_gdf"]
    st.subheader("B. Lakukan Analisis Keterpisahan Sampel")
    st.markdown("Pilih kolom yang sesuai dari Area Sampel Anda yang merujuk pada ID Kelas numerik dan Nama Kelas.")   
    
    #Dropdown for class_property (numeric IDs)
    class_property = st.selectbox(
        "Pilih kolom yang memuat ID Kelas numerik, (contoh: 1, 2, 3, 4, dst.):",
        options=gdf_cleaned.columns.tolist(),
        index=gdf_cleaned.columns.get_loc("CLASS_ID") if "CLASS_ID" in gdf_cleaned.columns else 0,
        key="class_property"
    )
    #Dropdown for class_name_property (class names)
    class_name_property = st.selectbox(
        "Pilih kolom tabel atribute yang berisi nama kelas (contoh: Hutan, Badan Air, Permukiman, dll):",
        options=gdf_cleaned.columns.tolist(),
        index=gdf_cleaned.columns.get_loc("CLASS_NAME") if "CLASS_NAME" in gdf_cleaned.columns else 0,
        key="class_name_property"
    )
    st.session_state["selected_class_property"] = class_property
    st.session_state["selected_class_name_property"] = class_name_property

    
    #Separability Parameters
    st.subheader("Parameter Analisis")
    #Hardcode method to Transformed Divergence
    method = "TD"
    #Add information for separability approach
    st.info("Metode Analisis Keterpisahan: Transformed Divergence (TD)")
    st.markdown("""
    Metode ini mengukur keterpisahan statisk antara kelas penutup lahan melalui analisis perbedaan nilai rata - rata (mean) dan struktur kovarian. 
    Nilai TD memiliki rentang 0 - 2, dimana nilai yang lebih tinggi mengacu kepada keterpisahan yang lebih baik.
    """)
    #user input (scale and max pixels). Note user did not have a lot to do, just make it default
    scale = st.number_input("Resolusi Spasial:", min_value=10, max_value=1000, value=30, step=10, 
                            help="Higher values = lower resolution but faster processing")
    max_pixels = st.number_input("Maximum pixels per class:", min_value=1000, max_value=10000, value=5000, step=500,
                                help="Lower values = faster processing but less representative sampling")

    #Single command to complete the analysis
    if st.button("Jalankan Analisis Keterpisahan", type="primary", use_container_width=True):
        if "training_data" not in st.session_state:
            st.error("Mohon unggah Shapefile Area Sampel yang valid terlebih dahulu.")
        else:
            try:
                #get the properties 
                class_prop = st.session_state["selected_class_property"]
                class_name_prop = st.session_state["selected_class_name_property"]
                #Create progress bar
                progress = st.progress(0)
                status_text = st.empty()
                #Intialize analyzer
                status_text.text("Langkah 1/5: Memulai proses analisis...")
                analyzer = sample_quality(
                    training_data=st.session_state["training_data"],
                    image=st.session_state["composite"],
                    class_property=class_prop,
                    region=st.session_state["AOI"],
                    class_name_property=class_name_prop,           
                )
                st.session_state["analyzer"] = analyzer
                st.session_state["analyzer_class_property"] = class_prop
                st.session_state["analyzer_class_name_property"] = class_name_prop
                progress.progress(20)
                #ROI statistics
                status_text.text("Langkah 2/5: Menghitung statistik area sampel")
                sample_stats_df = analyzer.get_sample_stats_df()
                st.session_state["sample_stats"] = sample_stats_df
                progress.progress(40)

                #Extract spectral values
                status_text.text("Langkah 3/5: Mengekstraks nilai spektral dari berbagai band… Proses ini memakan waktu beberapa menit.")
                try:
                    print(f"Debug: About to extract spectral values with scale={scale}, max_pixels={max_pixels}")
                    print(f"Debug: Analyzer class_property={analyzer.class_property}")
                    print(f"Debug: Analyzer class_name_property={analyzer.class_name_property}")
                        
                    pixel_extract = analyzer.extract_spectral_values(scale=scale, max_pixels_per_class=max_pixels)
                        
                    if pixel_extract.empty:
                            st.error("No spectral data was extracted. Please check your training data and image overlap.")
                            st.stop()
                        
                    print(f"Debug: Successfully extracted {len(pixel_extract)} pixels")
                    st.session_state["pixel_extract"] = pixel_extract
                    progress.progress(60)
                        
                except Exception as extract_error:
                        print(f"Debug: Extract error details: {extract_error}")
                        print(f"Debug: Extract error type: {type(extract_error)}")
                        traceback.print_exc()
                        raise extract_error

                #Compute pixel statistics
                status_text.text("Langkah 4/5: Menghitung statistik piksel...")
                try:
                    print("Debug: About to compute pixel statistics")
                    pixel_stats_df = analyzer.get_sample_pixel_stats_df(pixel_extract)
                    print(f"Debug: Pixel stats computed successfully, shape: {pixel_stats_df.shape}")
                    st.session_state["pixel_stats"] = pixel_stats_df
                    progress.progress(80)
                        
                except Exception as stats_error:
                    print(f"Debug: Pixel stats error: {stats_error}")
                    traceback.print_exc()
                    raise stats_error
                #Run separability analysis
                status_text.text("Langkah 5/5: Menjalankan analisis keterpisahan…")
                separability_df = analyzer.get_separability_df(pixel_extract, method=method)
                lowest_sep = analyzer.lowest_separability(pixel_extract, method=method)
                summary_df = analyzer.sum_separability(pixel_extract)
                #store all separability data
                st.session_state["separability_results"] = separability_df
                st.session_state["lowest_separability"] = lowest_sep
                st.session_state["separability_summary"] = summary_df
                st.session_state["separability_method"] = method
                st.session_state["analysis_complete"] = True
                progress.progress(100)
                st.success("Analisis Selesai!")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.write("Mohon periksa kembali Area Sampel dan parameter analisis Anda, lalu coba lagi.")
    #display the result
if st.session_state.get("analysis_complete", False):
    st.divider()
    st.subheader("C. Hasil Analisis")
    st.markdown("""
    Analisis keterpisahan menghasilkan beberapa tabel:
    - **Statistik Area Minat:** 
    - **Statistik Dasar Piksel:**
    - **Ringkasan Keterpisahan:**
    - **Keterpisahan Setiap Pasangan Kelas**
    
    """)
    #Display the results in table format
    #ROI Stats
    with st.expander("ROI Statistics", expanded=False):
        if "sample_stats" in st.session_state:
            st.dataframe(st.session_state["sample_stats"], use_container_width=True)
        else:
            st.write("Statistik sampel tidak tersedia.")
    #Pixel stats
    with st.expander("Statistik Piksel", expanded=True):  
        if "pixel_stats" in st.session_state:
            st.dataframe(st.session_state["pixel_stats"], use_container_width=True)
        else:
            st.write("Statistik piksel tidak tersedia.")
    #Separability summary
    with st.expander("Ringkasan Analisis Keterpisahan", expanded=True):
        if "separability_summary" in st.session_state:
            st.dataframe(st.session_state["separability_summary"], use_container_width=True)
            
            #Add interpretation
            summary = st.session_state["separability_summary"].iloc[0]
            total_pairs = summary.get('Total Pairs', 0)
            good_pairs = summary.get('Good Separability Pairs', 0)
            weak_pairs = summary.get('Weak Separability Pairs', 0)
            poor_pairs = summary.get('Poor Separability Pairs', 0)
            
            if total_pairs > 0:
                good_pct = (good_pairs / total_pairs) * 100
                if good_pct >= 70:
                    st.success(f"Sangat Baik! {good_pct:.1f}% dari pasangan kelas memiliki pemisahan data yang baik")
                elif good_pct >= 50:
                    st.warning(f"Menengah: {good_pct:.1f}% dari pasangan kelas memiliki pemisahan data yang baik")
                else:
                    st.error(f"Buruk: Hanya {good_pct:.1f}% dari pasangan kelas memiliki pemisahan data yang baik")
            
            # Add detailed interpretation guide
            st.markdown("---")
            st.markdown("**Interpretasi Nilai Transformed Divergence (TD):**")
            st.markdown("""
            - **TD ≥ 1.8**: 🟢 **Good Separability** - Kelas - Kelas dapat dipisahkan secara spektral dan kemungkinan dapat diklasifikasikan secara akurat
            - **1.0 ≤ TD < 1.8**: 🟡 **Weak/Marginal Separability** - Terdapat tumpang tindih yang dapat menyebabkan kesalahan klasifikasi antara kedua kelas
            - **TD < 1.0**: 🔴 **Poort Separability** - Terdapat tumpang tindih signifikan, terdapat risiko tinggi kesalahan klasifikasi dan bahkan tidak terpisahkan sama sekali
            """)
            
        else:
            st.write("Ringkasan analisis keterpisahan data tidak tersedia.")           
    # Detailed Separability Results
    with st.expander("Detailed Separability Results", expanded=False):
        if "separability_results" in st.session_state:
            st.dataframe(st.session_state["separability_results"], use_container_width=True)
        else:
            st.write("No detailed separability results available")
    # Most Problematic Class Pairs
    with st.expander("Most Problematic Class Pairs", expanded=True):
        if "lowest_separability" in st.session_state:
            st.markdown("*Pasangan kelas ini memiliki tingkat pemisahan data terendah dan dapat menyebabkan kerancuan klasifikasi:*")
            st.dataframe(st.session_state["lowest_separability"], use_container_width=True)
        else:
            st.write("No problematic pairs data available")            

st.divider()
st.subheader("D. Plot the Region of Interest")
st.markdown("You can visualize the ROI using several plots, namely histogram, box plot, and scatter plot. This allows the user to assess the overlap between classes, which might led to difficulties in separating them")
if (st.session_state.get("analysis_complete", False) and 
    "pixel_extract" in st.session_state and
    "analyzer" in st.session_state and
    not st.session_state["pixel_extract"].empty):

    #initialize the plotter
    try:
        plotter = spectral_plotter(st.session_state["analyzer"])
        pixel_data = st.session_state["pixel_extract"]
        #verification
        available_bands = [b for b in plotter.band_names if b in pixel_data.columns]
        if not available_bands:
            st.error("No valid spectral bands found in the extracted pixel data.")
            st.stop()
        #Tabs for different visualization
        viz1, viz2, viz3, viz4 = st.tabs([
            "Histograms",
            "Box Plots",
            "Scatter Plot",
            "3D Scatter Plot"
        ])
        #Tab 1: Facet Histograms
        with viz1:
            st.markdown("### Distribution of Spectral Values by Class")
            st.markdown("Interactive histograms showing all classes overlaid for easy comparison. " \
                       "Click legend items to show/hide specific classes.")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                selected_hist_bands = st.multiselect(
                    "Select bands to plot:",
                    options=available_bands,
                    default=available_bands[:3] if len(available_bands) >= 3 else available_bands,
                    key="hist_bands"
                )
            with col2:
                bins = st.slider("Number of bins:", min_value=10, max_value=50, value=30, step=5)
            with col3:
                hist_opacity = st.slider("Opacity:", 0.3, 0.9, 0.6, 0.1, key="hist_opacity")
            
            if st.button("Generate Histograms", key="btn_histogram", type="primary"):
                if selected_hist_bands:
                    with st.spinner("Generating interactive histograms..."):
                        try:
                            figures = plotter.plot_histogram(
                                pixel_data, 
                                bands=selected_hist_bands, 
                                bins=bins,
                                opacity=hist_opacity
                            )
                            for fig in figures:
                                st.plotly_chart(fig,width='stretch')
                            st.success("✅ Histograms generated!")
                            st.info("💡 **Tip:** Click on legend items to show/hide classes.")
                        except Exception as e:
                            st.error(f"Error generating histograms: {str(e)}")
                else:
                    st.warning("Please select at least one band.")
        
        #Tab 2: Box Plots
        with viz2:
            st.markdown("### Box Plots - Spectral Value Distribution")
            st.markdown("Interactive box plots showing median, quartiles, and outliers for each class. " \
                       "Hover over boxes to see statistical details.")
            
            selected_box_bands = st.multiselect(
                "Select bands to plot:",
                options=available_bands,
                default=available_bands[:5] if len(available_bands) >= 5 else available_bands,
                key="box_bands"
            )
            
            if st.button("Generate Box Plots", key="btn_boxplot", type="primary"):
                if selected_box_bands:
                    with st.spinner("Generating interactive box plots..."):
                        try:
                            figures = plotter.plot_boxplot(
                                pixel_data, 
                                bands=selected_box_bands
                            )
                            for fig in figures:
                                st.plotly_chart(fig,width='stretch')
                            st.success("✅ Box plots generated successfully!")
                            st.info("💡 **Tip:** Hover over boxes to see min, max, median, and quartile values.")
                        except Exception as e:
                            st.error(f"Error generating box plots: {str(e)}")
                else:
                    st.warning("Please select at least one band.")
        
        # TAB 3: SINGLE SCATTER PLOT
        with viz3:
            st.markdown("### Feature Space Scatter Plot")
            st.markdown("Visualize the relationship between two spectral bands and assess class separability in 2D feature space.")
            
            available_bands = [b for b in plotter.band_names if b in pixel_data.columns]
            
            if len(available_bands) >= 2:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    x_band = st.selectbox(
                        "X-axis band:",
                        options=available_bands,
                        index=0 if "RED" not in available_bands else available_bands.index("RED"),
                        key="scatter_x"
                    )
                
                with col2:
                    y_band = st.selectbox(
                        "Y-axis band:",
                        options=available_bands,
                        index=1 if "NIR" not in available_bands else available_bands.index("NIR"),
                        key="scatter_y"
                    )
                
                with col3:
                    alpha = st.slider("Point transparency:", 0.1, 1.0, 0.6, 0.1)
                
                # Additional options
                col4, col5 = st.columns(2)
                with col4:
                    add_ellipse = st.checkbox("Add confidence ellipses", value=False, 
                                            help="Shows 2-sigma confidence ellipses for each class")
                with col5:
                    color_palette = st.selectbox("Color palette:", 
                                                ["tab10", "Set3", "Paired", "husl", "Accent"], 
                                                index=0,  help="Preview will update when you change selection")
                    colors = plt.cm.get_cmap(color_palette)(np.linspace(0, 1, 10))
                    color_boxes = ""
                    for i in range(10):
                        color_hex = '#{:02x}{:02x}{:02x}'.format(
                            int(colors[i][0]*255), 
                            int(colors[i][1]*255), 
                            int(colors[i][2]*255),
                            int(colors[i][2]*255)
                        )
                        color_boxes += f'<span style="display:inline-block; width:20px; height:20px; background-color:{color_hex}; margin:2px; border:1px solid #ddd; border-radius:2px;"></span>'
                    
                    st.markdown(color_boxes, unsafe_allow_html=True)
                
                if st.button("Generate Scatter Plot", key="btn_scatter"):
                    with st.spinner("Generating scatter plot..."):
                        try:
                            fig = plotter.static_scatter_plot(
                                pixel_data,
                                x_band=x_band,
                                y_band=y_band,
                                alpha=alpha,
                                figsize=(12, 8),
                                color_palette=color_palette,
                                add_legend=True,
                                add_ellipse=add_ellipse
                            )
                            if fig:
                                #st.pyplot(fig)
                                st.success("Scatter plot generated successfully!")
                                st.pyplot(plt.gcf())
                                plt.close()
                                # Add interpretation
                                st.info("""
                                **Interpretation Tips:**
                                - Well-separated clusters indicate good class separability
                                - Overlapping clusters suggest potential classification confusion
                                - Ellipses show the spread and correlation of class data
                                """)
                        except Exception as e:
                            st.error(f"Error generating scatter plot: {str(e)}")
            else:
                st.warning("Need at least 2 bands for scatter plot visualization.")
   
        # TAB 4: MULTI-BAND SCATTER COMBINATIONS
        with viz4:
            st.markdown("### 3D Feature Space Exploration")
            st.markdown("Explore the spectral signatures in 3D space. Rotate, zoom, and pan to understand class relationships in three-band feature space.")
            
            if len(available_bands) >= 3:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    x_band_3d = st.selectbox(
                        "X-axis band:",
                        options=available_bands,
                        index=available_bands.index("RED") if "RED" in available_bands else 0,
                        key="scatter_3d_x"
                    )
                
                with col2:
                    y_band_3d = st.selectbox(
                        "Y-axis band:",
                        options=available_bands,
                        index=available_bands.index("GREEN") if "GREEN" in available_bands else (1 if len(available_bands) > 1 else 0),
                        key="scatter_3d_y"
                    )
                
                with col3:
                    z_band_3d = st.selectbox(
                        "Z-axis band:",
                        options=available_bands,
                        index=available_bands.index("NIR") if "NIR" in available_bands else (2 if len(available_bands) > 2 else 0),
                        key="scatter_3d_z"
                    )
                
                col4, col5 = st.columns(2)
                with col4:
                    marker_size_3d = st.slider("Point size:", 2, 8, 4, 1, key="marker_3d")
                with col5:
                    opacity_3d = st.slider("Point transparency:", 0.2, 1.0, 0.7, 0.1, key="opacity_3d")
                
                if st.button("Generate 3D Scatter Plot", key="btn_3d_scatter", type="primary"):
                    with st.spinner("Generating 3D scatter plot..."):
                        try:
                            fig = plotter.scatter_plot_3d(
                                pixel_data,
                                x_band=x_band_3d,
                                y_band=y_band_3d,
                                z_band=z_band_3d,
                                marker_size=marker_size_3d,
                                opacity=opacity_3d
                            )
                            if fig:
                                st.plotly_chart(fig,width='stretch')
                                st.success("✅ 3D scatter plot generated successfully!")
                                
                                st.info("""
                                **💡 Interactive Features:**
                                - **Rotate**: Click and drag to rotate the 3D view
                                - **Zoom**: Scroll wheel or pinch to zoom in/out
                                - **Pan**: Right-click and drag to pan
                                - **Hover**: See exact values for all three bands
                                - **Legend**: Click to show/hide classes
                                - **Reset**: Double-click to reset view
                                
                                **Analysis Tips:**
                                - Look for well-separated clusters in 3D space
                                - Rotate to find angles that best show class separation
                                - Classes that overlap in 2D may separate in 3D
                                - Common combinations: RGB, NIR-RED-GREEN, SWIR-NIR-RED
                                """)
                        except Exception as e:
                            st.error(f"Error generating 3D scatter plot: {str(e)}")
            else:
                st.warning("Need at least 3 bands for 3D scatter plot visualization.")
                st.info("The 3D scatter plot requires at least three spectral bands. " \
                    "Please ensure your analysis includes sufficient bands.")        
                st.markdown("---")
                st.markdown("**Right-click on any plot and select 'Save image as...' to download")
            
    except Exception as e:
                st.error(f"Error initializing visualization plotter: {str(e)}")
                st.info("Please ensure the separability analysis completed successfully.")
else:
    st.info("Please complete the separability analysis first to visualize training data.")
    st.markdown("""
    **Available visualizations after analysis:**
    - **Histograms**: Distribution of spectral values by class
    - **Box Plots**: Statistical summary of spectral values
    - **Scatter Plots**: 2D feature space visualization
    - **3D Scatter Plot**: 3D feature space visualization
    """)        
st.divider()
st.subheader("Module Navigation")

# Check if Module 2 is completed (has at least one class)
module_2_completed = len(st.session_state.get("classes", [])) > 0

# Create two columns for navigation buttons
col1, col2 = st.columns(2)

with col1:
    # Back to Module 3 button (always available)
    if st.button("⬅️ Back to Module 3: Generate ROI", use_container_width=True):
        st.switch_page("pages/3_Module_3_Generate_ROI.py")

with col2:
    # Forward to Module 6 button (conditional)
    if module_2_completed:
        if st.button("➡️ Go to Module 6: Supervised Classification", type="primary", use_container_width=True):
            st.switch_page("pages/5_Module_6_Classification_and_LULC_Creation.py")
    else:
        st.button("🔒 Complete Module 4 First", disabled=True,width='stretch', 
                 help="Analyze the region of interest in order to proceed")

# Optional: Show completion status
if module_2_completed:
    st.success(f"✅ Analysis Complete")
else:
    st.info("Analyze the region of interest in order to proceed")