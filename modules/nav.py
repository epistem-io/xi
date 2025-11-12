import streamlit as st

def Navbar():
    """The sidebar navigation using page_link with Indonesian translations"""
    with st.sidebar:
        # Home page
        st.page_link('home.py', label='Beranda')
        
        # Module pages with Indonesian labels
        st.page_link('pages/1_Module_1_Generate_Image_Mosaic.py', 
                    label='Modul 1: Buat Gabungan Citra')
        
        st.page_link('pages/2_Module_2_Classification_scheme.py', 
                    label='Modul 2: Tentukan Skema Klasifikasi')
        
        st.page_link('pages/3_Module_3_Generate_ROI.py', 
                    label='Modul 3: Penentuan Data Latih')
        
        st.page_link('pages/4_Module_4_Analyze_ROI.py', 
                    label='Modul 4: Analisis Area Sampel')
        
        st.page_link('pages/5_Module_6_Classification_and_LULC_Creation.py', 
                    label='Modul 6: Buat Peta Tutupan Lahan')
        
        st.page_link('pages/6_Module_7_Thematic_Accuracy.py', 
                    label='Modul 7: Uji Akurasi Petamu')
        
        st.page_link('pages/7_About.py', 
                    label='Tentang Epistem-X')
        
        # Separator
        st.markdown("---")
        
        # About section
        st.markdown("### Tentang Wahana")
        st.info("""
        **Epistem-X** adalah wahana pemetaan tutupan dan penggunaan lahan berbasis citra satelit, 
        yang dikembangkan untuk mendukung perencanaan bentang lahan dan solusi alami perubahan iklim.  
        Aplikasi ini merupakan **implementasi Fase 1**, yang berfokus pada pengembangan prototipe awal 
        yang mencakup seluruh alur kerja penting dalam pembuatan peta tutupan/penggunaan lahan.

        **Epistem-X** dibangun menggunakan pustaka **Streamlit** dan **Google Earth Engine (GEE)** 
        untuk menyediakan antarmuka analisis yang transparan, kolaboratif, dan mudah diakses oleh parapihak.
        """)
        
        # Logo
        logo = "logos/artwork_sidebar.png"
        try:
            st.sidebar.image(logo)
        except:
            pass  # Logo file not found, continue without it