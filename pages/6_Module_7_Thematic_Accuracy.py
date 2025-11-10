import streamlit as st
from epistemx.shapefile_utils import shapefile_validator, EE_converter
from epistemx.module_7 import Thematic_Accuracy_Assessment
from modules.nav import Navbar
import pandas as pd
import geemap.foliumap as geemap
import tempfile
import zipfile
import os
import geopandas as gpd
import plotly.express as px
from ui_helper import show_footer, show_header

#Page configuration
st.set_page_config(
    page_title="Epistem-X Modul 7",
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
show_header()

st.markdown("""
<div class="breadcrumb">Modul 7 › Uji Akurasi Petamu</div>
""", unsafe_allow_html=True)

#Initialize accuracy assessment manager
@st.cache_resource
def get_accuracy_manager():
    return Thematic_Accuracy_Assessment()

manager = get_accuracy_manager()

# Add navigation sidebar
Navbar()
# Page header
st.markdown("""
<style>
.gradient-title {
  font-size: 2.5em;
  font-weight: 700;
  text-align: left;
  background: linear-gradient(90deg, var(--pink), var(--purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  margin-bottom: 0.4em;
}
</style>
<h1 class="gradient-title">Penilaian Akurasi Tematik</h1>
""", unsafe_allow_html=True)
st.divider()

st.markdown("""
Evaluasi akurasi tematik dari klasifikasi tutupan lahan Anda dari Modul 6 menggunakan data validasi independen. 
Untuk menjalankan modul ini Anda memerlukan data referensi lapangan yang berisi ID kelas dan nama kelas serupa dengan ROI
Akurasi peta tutupan lahan dievaluasi menggunakan matriks konfusi, dengan metrik kunci berikut
- **Akurasi Keseluruhan** dengan interval kepercayaan
- **Koefisien Kappa** untuk penilaian kesepakatan  
- **Skor F1** untuk kinerja tingkat kelas
""")

st.markdown("---")
#This module wont run if classification result from module 6 is not avaliable
def check_prerequisites():
    """Check if required data from previous modules is available"""
    if 'classification_result' not in st.session_state or st.session_state.classification_result is None:
        st.error("❌ Tidak ditemukan hasil klasifikasi dari Modul 6.")
        st.warning("Selesaikan Modul 6 terlebih dahulu untuk menghasilkan peta klasifikasi tutupan lahan.")
        st.stop()
    else:
        st.success("✅ Peta klasifikasi dimuat dari Modul 6")
        return st.session_state.classification_result

#Initialize the functions
lcmap = check_prerequisites()
#function to upload the ground reference data (similar to module 3, but in a function)
def process_shapefile_upload(uploaded_file):
    """Process uploaded shapefile and convert to Earth Engine format"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save uploaded file
            zip_path = os.path.join(tmpdir, "upload.zip")
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract zip file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            # Find shapefile
            shp_files = []
            for root, _, files in os.walk(tmpdir):
                for fname in files:
                    if fname.lower().endswith(".shp"):
                        shp_files.append(os.path.join(root, fname))

            if not shp_files:
                return False, "Berkas .shp tidak ditemukan dalam zip yang diunggah.", None, None

            # Read and process shapefile
            gdf = gpd.read_file(shp_files[0])
            
            #Validate and clean geometry using the helper module 
            validator = shapefile_validator(verbose=False)
            converter = EE_converter(verbose=False)
            
            gdf_cleaned = validator.validate_and_fix_geometry(gdf, geometry="mixed")
            
            if gdf_cleaned is None:
                return False, "Validasi geometri gagal", None, None
            
            # Convert to Earth Engine format using helper module
            ee_data = converter.convert_roi_gdf(gdf_cleaned)
            
            if ee_data is None:
                return False, "Gagal mengkonversi ke format Google Earth Engine", None, None
            
            return True, "Data validasi berhasil diproses", ee_data, gdf_cleaned
            
    except Exception as e:
        return False, f"Kesalahan memproses shapefile: {str(e)}", None, None

#similar to module 1 but wrap in function
def render_validation_upload():
    """Render validation data upload section"""
    st.subheader("Langkah 1: Unggah Data Referensi Lapangan")
    st.info("📁 Unggah **shapefile .zip** yang berisi sampel validasi independen Anda dengan ID kelas.")

    uploaded_file = st.file_uploader("Pilih shapefile terkompresi (.zip)", type=["zip"])

    if uploaded_file:
        with st.spinner("Memproses data validasi..."):
            success, message, ee_data, gdf_cleaned = process_shapefile_upload(uploaded_file)
            
            if success:
                st.success(f"✅ {message}")
                
                # Store in session state
                st.session_state['validation_data'] = ee_data
                st.session_state['validation_gdf'] = gdf_cleaned
                
                # Show data preview
                with st.expander("📋 Pratinjau Data"):
                    st.dataframe(gdf_cleaned.head(), use_container_width=True)
                
                # Show map preview
                st.markdown("**📍 Sebaran Titik Validasi:**")
                centroid = gdf_cleaned.geometry.centroid.iloc[0]
                preview_map = geemap.Map(center=[centroid.y, centroid.x], zoom=8)
                preview_map.add_geojson(gdf_cleaned.__geo_interface__, layer_name="Titik Validasi")
                preview_map.to_streamlit(height=500)
                
            else:
                st.error(f"❌ {message}")
                if "Make sure your shapefile includes" not in message:
                    st.info("💡 Pastikan shapefile Anda menyertakan semua file yang diperlukan (.shp, .shx, .dbf, .prj)")

#run validation data upload
render_validation_upload()
#Function for definining user input for accuracy assessment
def user_input_for_accuracy_assessment():
    """Render accuracy assessment configuration and execution"""
    st.divider()
    st.subheader("Langkah 2: Konfigurasi dan Jalankan Penilaian")

    if "validation_data" not in st.session_state or st.session_state.validation_data is None:
        st.warning("⚠️ Harap unggah data validasi Anda terlebih dahulu.")
        return

    gdf_cleaned = st.session_state.get('validation_gdf')
    if gdf_cleaned is None:
        st.error("Data validasi tidak berhasil dimuat dengan benar.")
        return

    # Configuration options
    col1, col2 = st.columns(2)
    
    with col1:
        class_prop = st.selectbox(
            "Kolom ID Kelas:",
            options=gdf_cleaned.columns.tolist(),
            index=gdf_cleaned.columns.get_loc("CLASS_ID") if "CLASS_ID" in gdf_cleaned.columns else 0,
            help="Kolom yang berisi pengenal kelas numerik (mis. 1, 2, 3, 4)"
        )
    
    with col2:
        scale = st.number_input(
            "Ukuran Piksel (meter):",
            min_value=10,
            max_value=1000,
            value=30,
            help="Resolusi spasial untuk pengambilan sampel pada peta terklasifikasi"
        )

    # Advanced options
    with st.expander("⚙️ Opsi Lanjutan"):
        confidence = st.slider(
            "Tingkat Kepercayaan untuk Interval Akurasi:",
            min_value=0.90,
            max_value=0.99,
            value=0.95,
            step=0.01,
            format="%.2f"
        )

    # Run assessment
    if st.button("🎯 Evaluasi Akurasi Peta", type="primary", use_container_width=True):
        with st.spinner("Menjalankan penilaian akurasi tematik..."):
            success, results = manager.run_accuracy_assessment(
                lcmap=lcmap,
                validation_data=st.session_state.validation_data,
                class_property=class_prop,
                scale=scale,
                confidence=confidence
            )

            if success:
                st.session_state["accuracy_results"] = results
                st.success("✅ Penilaian akurasi tematik selesai!")
                st.rerun()
            else:
                st.error(f"❌ Penilaian gagal: {results.get('error', 'Kesalahan tidak diketahui')}")

#run user inpur function
user_input_for_accuracy_assessment()

#Function to display accuracy assessment
def render_accuracy_results():
    """Render accuracy assessment results"""
    #if not initialize yet
    if "accuracy_results" not in st.session_state:
        return
    #Then initialze the session state to store the accuracy
    results = st.session_state["accuracy_results"]
    
    if 'error' in results:
        st.error(f"❌ {results['error']}")
        return

    st.divider()
    st.subheader("Hasil Penilaian Akurasi")

    #Prepared to display the key result
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Akurasi Keseluruhan", 
            f"{results['overall_accuracy']*100:.2f}%"
        )
    
    with col2:
        st.metric(
            "Koefisien Kappa", 
            f"{results['kappa']:.3f}"
        )
    
    with col3:
        ci = results['overall_accuracy_ci']
        confidence_pct = int(results['confidence_level'] * 100)
        st.metric(
            f"Interval Kepercayaan {confidence_pct}%", 
            f"{ci[0]*100:.1f}% - {ci[1]*100:.1f}%"
        )
    
    with col4:
        st.metric(
            "Ukuran Sampel", 
            f"{results['n_total']} titik"
        )

    # Class-level metrics table
    st.markdown("---")
    st.subheader("Kinerja per Kelas")

    df_metrics = pd.DataFrame({
        "ID Kelas": range(len(results['producer_accuracy'])),
        "Akurasi Produsen (%)": [round(v * 100, 2) for v in results['producer_accuracy']],
        "Akurasi Pengguna (%)": [round(v * 100, 2) for v in results['user_accuracy']],
        "Skor F1 (%)": [round(v * 100, 2) for v in results["f1_scores"]],
    })
    
    st.dataframe(df_metrics, use_container_width=True)

    # Confusion matrix visualization
    st.markdown("---")
    st.subheader("🔄 Matriks Konfusi")

    cm_array = results["confusion_matrix"]
    n_classes = len(cm_array)
    
    cm_df = pd.DataFrame(
        cm_array,
        columns=[f"Prediksi {i}" for i in range(n_classes)],
        index=[f"Aktual {i}" for i in range(n_classes)]
    )
    
    # Create heatmap
    fig = px.imshow(
        cm_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Matriks Konfusi (Kelas Aktual vs Prediksi)"
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Kelas Prediksi",
        yaxis_title="Kelas Aktual"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Export results option
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Create downloadable results
        results_summary = {
            'Overall_Accuracy_Percent': results['overall_accuracy'] * 100,
            'Kappa_Coefficient': results['kappa'],
            'Confidence_Interval_Lower': results['overall_accuracy_ci'][0] * 100,
            'Confidence_Interval_Upper': results['overall_accuracy_ci'][1] * 100,
            'Sample_Size': results['n_total'],
            'Scale_Meters': results['scale']
        }
        
        results_df = pd.DataFrame([results_summary])
        csv_data = results_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Unduh Ringkasan Hasil",
            data=csv_data,
            file_name="accuracy_assessment_results.csv",
            mime="text/csv",
           use_container_width=True
        )
    
    with col2:
        # Download detailed metrics
        detailed_csv = df_metrics.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Metrik Kelas",
            data=detailed_csv,
            file_name="class_level_accuracy.csv",
            mime="text/csv",
           use_container_width=True
        )

def render_navigation():
    """Render navigation options"""
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Kembali ke Modul 6", use_container_width=True):
            st.switch_page("pages/5_Module_6_Classification_and_LULC_Creation.py")
    
    with col2:
        st.info("💡 Kembali ke Modul 6 untuk meningkatkan model klasifikasi Anda jika diperlukan")

# Render results and navigation
render_accuracy_results()
render_navigation()