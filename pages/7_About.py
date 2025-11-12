import streamlit as st
from modules.nav import Navbar
from ui_helper import show_footer, show_header

st.set_page_config(
    page_title="Tentang Epistem-X",
    page_icon="logos/logo_epistem_crop.png",
    layout="wide"
)

def load_css():
    """Load custom CSS for EpistemX theme"""
    try:
        with open('.streamlit/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# --- Header and Navigation ---
show_header()
Navbar() 

# Header
st.markdown("""
<div class="main-header">
    <h1>Tentang Epistem-X</h1>
    <p>Wahana pemetaan bentang lahan <i>open-source</i> yang ramah pengguna untuk pemantauan, restorasi, dan pengelolaan bentang lahan di Indonesia.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---") 

# Description
with st.container():
    st.markdown("""
    <div style="border: 2px solid #e0e0e0; border-radius: 16px; padding: 30px; margin: 0 0 20px 0; background: #ffffff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);">
        <p style="text-align: justify; line-height: 1.8; font-size: 1em; margin-bottom: 15px;">
        Epistem-X adalah platform pemetaan bentang lahan terpadu berbasis komputasi awan yang menyediakan akses ke katalog citra satelit 
        dan data spasial terbuka untuk publik. Platform ini dikembangkan secara kolaboratif dengan fokus pada kemudahan penggunaan, 
        sehingga dapat dimanfaatkan bahkan oleh pengguna dengan latar belakang teknis terbatas dalam bidang penginderaan jauh. 
        </p>
        <p style="text-align: justify; line-height: 1.8; font-size: 1em; margin-bottom: 15px;">
        Dengan memanfaatkan kekuatan Google Earth Engine, Epistem-X memungkinkan Anda mengakses katalog data satelit yang luas dan beragam 
        secara langsung. Platform ini menangani kompleksitas teknis penginderaan jauh di balik layar, sehingga Anda dapat berkonsentrasi 
        pada penyiapan data berkualitas untuk menghasilkan peta yang lebih baik.
        </p>
        <p style="text-align: justify; line-height: 1.8; font-size: 1em; margin-bottom: 0;">
        Epistem-X terwujud berkat dukungan dari kegiatan <em>Evolving Participatory Information System for Nature-based Climate Solutions</em> (Epistem).
        </p>
    </div>
    """, unsafe_allow_html=True)

with st.expander("📖 Pelajari Lebih Lanjut Tentang Kegiatan Epistem"):
    st.write("**_Evolving Participatory Information System for Nature-based Climate Solutions (Epistem)_** adalah inisiatif kolaboratif yang dirancang untuk memajukan teknologi pemetaan dalam menyediakan data spasial berkualitas tinggi. Proyek ini mendukung upaya pencegahan deforestasi dan pemulihan bentang lahan yang terdegradasi.")
    
    st.markdown("##### Tujuan")
    st.markdown("""
    * Mengembangkan teknologi pemetaan bentang lahan sumber terbuka yang mudah digunakan dan dapat diakses tanpa memerlukan peralatan atau lisensi khusus.
    * Mengoptimalkan pemanfaatan data penginderaan jauh yang tersedia secara gratis, seperti citra satelit, untuk pemantauan hutan dan bentang lahan.
    * Membangun dan memelihara basis data referensi tutupan lahan dan penggunaan lahan yang terintegrasi dalam platform pemetaan sebagai sistem sumber terbuka.
    * Mendukung berbagai pihak dalam upaya pencegahan deforestasi dan restorasi lintas sektor dan area tematik.
    """)

st.markdown("---") 

# Developers
st.markdown('<div class="module-header">Tim Pengembang</div>', unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="epistemx-card">
        <p>Algoritma backend Epistem-X dikembangkan dan dikelola secara kolaboratif. 
        Kontribusi mencakup pengembangan algoritma pemrosesan citra dan klasifikasi tutupan/penggunaan lahan
        serta penyediaan prototipe antarmuka untuk pengguna.</p>
        <p>Epistem-X dibangun oleh banyak kontributor. Lihat daftar lengkap kontributor di 
        <a href="https://github.com/epistem-io" target="_blank">https://github.com/epistem-io</a></p>
    </div>
    """, unsafe_allow_html=True)



st.markdown("---") 

# Platform architecture
st.markdown('<div class="module-header">Arsitektur</div>', unsafe_allow_html=True)

with st.container():
    st.markdown("""
    <div class="epistemx-card">
        <p>Epistem-X dibangun dengan dukungan kegiatan Epistem (<i>Evolving Participatory Information System for Nature-based Solutions</i>) dan berbagai perangkat lunak sumber terbuka lainnya.</p>
    </div>
    """, unsafe_allow_html=True)

try:
    st.image("logos/arsitektur_epistemx.png", caption="Arsitektur Sistem Epistem-X", use_container_width=True)
except FileNotFoundError:
    st.info("📊 Gambar arsitektur akan ditambahkan di sini")

show_footer()