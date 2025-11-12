import streamlit as st
import leafmap.foliumap as leafmap
from epistemx import auto_initialize
from modules.nav import Navbar
import os
import tempfile
from ui_helper import show_footer, show_header, show_hero_banner

st.set_page_config(
    page_title="Epistem-X Beranda",
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
        pass  # CSS file not found, continue without custom styling

# Apply custom theme
load_css()
# Show header
show_header()

# Set up temporary directory for leafmap
if not os.path.exists('/tmp'):
    os.makedirs('/tmp', exist_ok=True)
os.environ['TMPDIR'] = '/tmp'

# Initialize Earth Engine once when the app starts
if 'ee_initialized' not in st.session_state:
    try:
        result = auto_initialize()
        st.session_state.ee_initialized = result
        if result:
            st.success("Earth Engine berhasil diinisialisasi!")
        else:
            st.error("Gagal menginisialisasi Earth Engine. Mohon periksa autentikasi Anda.")
    except Exception as e:
        st.error(f"Earth Engine initialization error: {e}")
        st.session_state.ee_initialized = False

# Add navigation sidebar
Navbar()

# Display hero banner with title overlay
show_hero_banner()

st.markdown('<div class="module-header">📋 Modul - Modul Epistem</div>', unsafe_allow_html=True)

st.markdown("""
<div class="epistemx-card">
    <div class="steps">
        <div class="step">
            <strong>1. Modul 1: Buat Gabungan Citra</strong>
            <p>Modul ini menghasilkan citra satelit yang siap pakai dengan kualitas yang terbaik</p>
        </div>
        <div class="step">
            <strong>2. Modul 2: Tentukan Skema Klasifikasi</strong>
            <p>Penentuan target kelas - kelas penutup lahan yang akan dipetakan melalui platform Epistem</p>
        </div>
        <div class="step">
            <strong>3. Modul 3: Penentuan Data Latih</strong>
            <p>Membuat data untuk melatih komputer dalam melakukan pemetaan penutup lahan </p>
        </div>
        <div class="step">
            <strong>4. Modul 4: Analisis Area Sampel </strong>
            <p>Ketahui kualitas data anda melalui analisis keterpisahan</p>
        </div>
        <div class="step step-disabled">
            <strong>5. Modul 5: Tambahkan kovariat multisumber </strong>
            <p>🚧 Dalam pengembangan</p>
        </div>
            <div class="step">
            <strong>6. Modul 6: Buat Peta Penutup Lahan </strong>
            <p>Latih algoritma klasifikasi berbasis mesin, untuk menghasilkan peta penutup lahan anda</p>
        </div>
        <div class="step">
            <strong>7. Modul 7: Uji Akurasi Petamu </strong>
            <p>Bandingkan peta yang kamu hasilkan dengan data referensi</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status indicator
if st.session_state.get('ee_initialized', False):
    st.markdown('<div class="success-message">✅ Earth Engine Siap - Anda dapat melanjutkan analisis</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="warning-message">⚠️ Earth Engine Belum Diinisialisasi - Mohon periksa autentikasi</div>', unsafe_allow_html=True)

st.markdown('<div class="map-container-fullwidth">', unsafe_allow_html=True)
m = leafmap.Map(center=[-2.5, 118.0], zoom=5)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)
st.markdown('</div>', unsafe_allow_html=True)

show_footer()
