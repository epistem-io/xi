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
                    label='Modul 3: Buat Area Sampel')
        
        st.page_link('pages/4_Module_4_Analyze_ROI.py', 
                    label='Modul 4: Analisis Area Sampel')
        
        st.page_link('pages/5_Module_6_Classification_and_LULC_Creation.py', 
                    label='Modul 6: Buat Peta Tutupan Lahan')
        
        st.page_link('pages/6_Module_7_Thematic_Accuracy.py', 
                    label='Modul 7: Uji Akurasi Petamu')
        
        # Separator
        st.markdown("---")
        
        # About section
        st.markdown("### Tentang")
        st.info("""
        Contoh kerja modul 1 dan 3 dari platform pemetaan tutupan lahan Epistem. Diadaptasi dari:
        <https://github.com/opengeos/streamlit-map-template>
        """)
        
        # Logo
        logo = "logos/logo_epistem.png"
        try:
            st.image(logo)
        except:
            pass  # Logo file not found, continue without it