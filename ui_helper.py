import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    """Convert local image to base64 for inline HTML use"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_header():
    """Header Inline"""
    image_path = os.path.join(os.path.dirname(__file__), "logos", "header_logo.png")
    if os.path.exists(image_path):
        img_base64 = get_base64_of_bin_file(image_path)
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="EpistemX Logo" class="header-logo">'
    else:
        img_html = '<p>EpistemX</p>'

    st.markdown(f"""
<style>
.header-inline {{
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 50px;
  width: calc(100% - 50px);
  height: 70px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  box-shadow: 4px 2px 12px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 999999 !important;
}}
.header-logo {{
  height: 45px;
  width: auto;
  margin-left: -50px;
}}
.block-container {{
  padding-top: 100px !important;
}}
section[data-testid="stSidebar"] {{
  margin-top: 70px !important;
}}
section[data-testid="stExpandSidebarButton"] {{
  margin-top: 70px !important;
}}
</style>

<div class="header-inline">
  {img_html}
</div>
""", unsafe_allow_html=True)

def show_hero_banner():
    """Display hero section with banner as backdrop"""
    banner_path = os.path.join(os.path.dirname(__file__), "logos", "banner.png")
    if os.path.exists(banner_path):
        img_base64 = get_base64_of_bin_file(banner_path)
        st.markdown(f"""
<style>
.hero-banner {{
  position: relative;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  min-height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background-image: url('data:image/png;base64,{img_base64}');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}}

.hero-overlay {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(1px);
}}

.hero-content {{
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 60px 40px;
  color: white;
}}

.hero-content h2 {{
  font-size: 1.8em;
  font-weight: 400;
  margin-bottom: 15px;
  text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.7);
  letter-spacing: 0.5px;
  color: white;
}}

.hero-content h1 {{
  font-size: 3.5em;
  font-weight: 700;
  margin-bottom: 25px;
  line-height: 1.2;
  text-shadow: 3px 3px 12px rgba(0, 0, 0, 0.8);
  color: white;
}}

.hero-content p {{
  font-size: 1.2em;
  line-height: 1.6;
  max-width: 800px;
  margin: 0 auto;
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7);
  color: white;
  opacity: 0.95;
}}
</style>

<div class="hero-banner">
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <h2>Selamat Datang di</h2>
    <h1>Platform Pemetaan Tutupan Lahan<br>EpistemX</h1>
    <p>Teknologi pemetaan untuk menjawab kebutuhan data spasial berkualitas dalam mendukung upaya pencegahan deforestasi dan restorasi lanskap.<br>
    Dirancang dengan sistem modular dan berakar kuat terhadap keilmuan dan perkembangan teknologi, platform ini diharapkan dapat memberikan fasilitas bagi seluruh kalangan pengguna.</p>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.warning("Banner logo not found")



# def show_footer():
#     """Footer EpistemX global with logo"""
#     footer_logo_path = os.path.join(os.path.dirname(__file__), "logos", "footer.png")
#     if os.path.exists(footer_logo_path):
#         img_base64 = get_base64_of_bin_file(footer_logo_path)
#         logo_html = f'<img src="data:image/png;base64,{img_base64}" alt="Footer Logo" class="footer-logo">'
#     else:
#         logo_html = '<p></p>'

#     st.markdown(f"""
#         <hr style="margin-top: 40px; opacity: 0.2;">
#         <div class="footer">
#             {logo_html}
#             <p>© 2025 <strong>EpistemX</strong> • Designed by Azizy</p>
#             <div class="footer-links">
#                 <a href="https://github.com/mhmmdazizy" target="_blank">GitHub</a> ·
#                 <a href="mailto:mazizy@cifor-icraf.org">Email</a>
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

def show_footer():
    """Footer EpistemX global with logo"""
    footer_logo_path = os.path.join(os.path.dirname(__file__), "logos", "footer.png")
    if os.path.exists(footer_logo_path):
        img_base64 = get_base64_of_bin_file(footer_logo_path)
        logo_html = f'<img src="data:image/png;base64,{img_base64}" alt="Footer Logo" class="footer-logo">'
    else:
        logo_html = '<p></p>'

    # Inline SVG icons (putih agar cocok di background ungu/pink)
    github_icon = """
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="black" viewBox="0 0 24 24">
        <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303
        3.438 9.8 8.205 11.385.6.113.82-.258.82-.577
        0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61
        -.546-1.385-1.333-1.754-1.333-1.754-1.089-.744.084-.729.084-.729
        1.205.084 1.84 1.237 1.84 1.237 1.07 1.835 2.809 1.304 3.495.997
        .108-.776.418-1.305.762-1.605-2.665-.3-5.466-1.335-5.466-5.93
        0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176
        0 0 1.005-.322 3.3 1.23a11.48 11.48 0 013.003-.404
        c1.02.005 2.045.137 3.003.404 2.28-1.552 3.285-1.23 3.285-1.23
        .645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22
        0 4.61-2.805 5.625-5.475 5.92.435.375.81 1.096.81 2.22
        0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57
        C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
    </svg>
    """

    email_icon = """
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="black" viewBox="0 0 24 24">
        <path d="M12 13.065l-11.994-6.065v14h23.988v-14l-11.994 6.065zm11.994-9.065h-23.988l11.994 6.032 11.994-6.032z"/>
    </svg>
    """

    st.markdown(f"""
        <hr style="margin-top: 20px; margin-bottom: 0; opacity: 0.15;">
        <div class="footer">
            {logo_html}
            <p>© 2025 <strong>EpistemX</strong> • Designed by Azizy</p>
            <div class="footer-links">
                <a href="https://github.com/epistem-io/EpistemXBackend" target="_blank" class="footer-icon">{github_icon}</a>
                <a href="mailto:hello@epistemx.io" class="footer-icon">{email_icon}</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

