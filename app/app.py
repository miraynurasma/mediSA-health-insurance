import streamlit as st
import time
import os
import sys
import base64
import random

# Yol ayarları
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
sys.path.append(base_dir)

from backend.cnn_model import get_model, predict_with_heatmap

st.set_page_config(page_title="MediSA Sağlık AI", page_icon="🛡️", layout="wide")

# --- ARKA PLAN İŞLEME ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    bg_img_path = os.path.join(current_dir, "assets", "medisa.png")
    img_base64 = get_base64_of_bin_file(bg_img_path)
except Exception:
    img_base64 = ""

# --- CSS İLE RENKLENDİRME VE DÜZENLEME ---
st.markdown(f"""
    <style>
    /* GENEL AYARLAR */
    * {{ user-select: text !important; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); height: 0px; }}
    .block-container {{ padding-top: 1.5rem !important; }}
    
    .stApp {{
        background: linear-gradient(rgba(10, 25, 47, 0.85), rgba(10, 25, 47, 0.85)), 
                    url("data:image/png;base64,{img_base64}");
        background-size: cover; background-attachment: fixed;
    }}

    /* --- SIDEBAR İÇERİK YAZILARINI BEYAZLATMA --- */
    [data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(20px); }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
        color: white !important; font-weight: 500 !important;
    }}
    
    /* --- BAR ÜZERİNDEKİ BAŞLIKLARI RENKLENDİRME (SIRAYLA) --- */
    
    /* Expander Genel Yapısı */
    .stExpander {{ 
        border: 1px solid rgba(255,255,255,0.1) !important; 
        background: rgba(0,0,0,0.2) !important; 
        border-radius: 10px; margin-bottom: 10px;
    }}
    
    /* Barın Üzerindeki Yazı Fontu */
    .stExpander summary p {{
        font-size: 16px !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.8);
    }}

    /* 1. Kutu: ORTOPEDİ (Mavi) */
    [data-testid="stSidebar"] .stExpander:nth-of-type(1) summary p {{ color: #4A90E2 !important; }}
    [data-testid="stSidebar"] .stExpander:nth-of-type(1) {{ border-left: 4px solid #4A90E2 !important; }}

    /* 2. Kutu: RETİNA (Turuncu) */
    [data-testid="stSidebar"] .stExpander:nth-of-type(2) summary p {{ color: #FF8200 !important; }}
    [data-testid="stSidebar"] .stExpander:nth-of-type(2) {{ border-left: 4px solid #FF8200 !important; }}

    /* 3. Kutu: MR (Açık Mavi) */
    [data-testid="stSidebar"] .stExpander:nth-of-type(3) summary p {{ color: #00B5E2 !important; }}
    [data-testid="stSidebar"] .stExpander:nth-of-type(3) {{ border-left: 4px solid #00B5E2 !important; }}

    /* 4. Kutu: CİLT (Yeşil) */
    [data-testid="stSidebar"] .stExpander:nth-of-type(4) summary p {{ color: #28a745 !important; }}
    [data-testid="stSidebar"] .stExpander:nth-of-type(4) {{ border-left: 4px solid #28a745 !important; }}

    /* 5. Kutu: TORAKS (Pembe) */
    [data-testid="stSidebar"] .stExpander:nth-of-type(5) summary p {{ color: #FF1493 !important; }}
    [data-testid="stSidebar"] .stExpander:nth-of-type(5) {{ border-left: 4px solid #FF1493 !important; }}


    /* TAB (SEKME) RENKLERİ */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px !important; justify-content: center; }}
    .stTabs [data-baseweb="tab"] {{ height: 75px !important; min-width: 180px !important; border-radius: 20px !important; color: white !important; font-weight: 700 !important; border: 2px solid rgba(255, 255, 255, 0.1) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(1) {{ background: rgba(0, 51, 160, 0.3) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {{ background: rgba(0, 51, 160, 0.7) !important; border-color: #0033A0 !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(2) {{ background: rgba(255, 130, 0, 0.3) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {{ background: rgba(255, 130, 0, 0.7) !important; border-color: #FF8200 !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(3) {{ background: rgba(0, 181, 226, 0.3) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {{ background: rgba(0, 181, 226, 0.7) !important; border-color: #00B5E2 !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(4) {{ background: rgba(40, 167, 69, 0.3) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {{ background: rgba(40, 167, 69, 0.7) !important; border-color: #28a745 !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(5) {{ background: rgba(255, 20, 147, 0.3) !important; }}
    .stTabs [data-baseweb="tab"]:nth-child(5)[aria-selected="true"] {{ background: rgba(255, 20, 147, 0.7) !important; border-color: #FF1493 !important; }}

    .glass-card {{ background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(15px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); color: white !important; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BAŞLIK VE İÇERİK ---
with st.sidebar:
    # YENİ SLOGAN VE BAŞLIK TASARIMI
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: white; font-weight: 300; font-size: 36px; margin: 0; text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);">
                MediSA
            </h1>
            <p style="color: white; font-weight: 300; font-size: 14px; letter-spacing: 2px; margin-top: 5px; opacity: 0.9; text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);">
                Sağlığın Dijital Gözü 👁️
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # 1. ORTOPEDİ (Mavi)
    with st.expander("🦴 RÖNTGEN", expanded=True):
        akut = st.toggle("🚨 Akut / Şiddetli Ağrı")
        kaza = st.toggle("🚗 Kaza Bildirimi")
        deformite = st.toggle("🦴 Deformite / Kırık")
        kısıtlılık = st.toggle("🏃 Hareket Kısıtlılığı")

    # 2. RETİNA (Turuncu)
    with st.expander("👁️ RETİNA"):
        gorme_kaybi = st.toggle("🌫️ Ani Görme Kaybı")
        bulanik = st.toggle("👓 Bulanık Görme")
        diyabet = st.toggle("🍬 Diyabet Öyküsü")

    # 3. MR (Açık Mavi)
    with st.expander("🧠 MR"):
        bas_agrisi = st.toggle("🧠 Şiddetli Baş Ağrısı")
        bas_donmesi = st.toggle("🌀 Baş Dönmesi")

    # 4. CİLT (Yeşil)
    with st.expander("🧪 CİLT"):
        kasinti = st.toggle("🟣 Şiddetli Kaşıntı")
        renk_degisimi = st.toggle("🎨 Renk Değişimi")
        hizli_buyume = st.toggle("📈 Hızlı Yayılma")

    # 5. TORAKS (Pembe)
    with st.expander("🫁 GÖĞÜS"):
        ates = st.toggle("🌡️ Yüksek Ateş")
        oksuruk = st.toggle("🗣️ Kronik Öksürük")
        nefes = st.toggle("🫁 Nefes Darlığı")

    st.divider()
    poliçe_no = st.text_input("🆔 Poliçe No", "MED-10045-S")

# --- ANA EKRAN ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🦴 Ortopedi", "👁️ Retina", "🧠 MR", "🧪 Cilt", "🫁 Göğüs"])

with tab1:
    c_l, c_r = st.columns(2, gap="large")
    with c_l:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#FFFFFF;'> 📥 Radyografi Yükle</h4>", unsafe_allow_html=True)
        file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if file: st.image(file, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color:#FFFFFF;'> 📊 Akıllı Poliçe Analizi</h4>", unsafe_allow_html=True)
        if file:
            if st.button("PROVİZYONU ANALİZ ET"):
                with st.spinner("İnceleniyor..."):
                    time.sleep(1)
                    model = get_model()
                    label, conf, heatmap = predict_with_heatmap(model, file)
                    st.image(heatmap, use_container_width=True, channels="BGR")
                    
                    if label == "fracture":
                        if kaza or (akut and (deformite or kısıtlılık)):
                            st_txt, color, bg = "PROVİZYON ONAYLANDI", "#28a745", "rgba(40, 167, 69, 0.2)"
                            msg = f"Bulgular uyumludur. {poliçe_no} kapsamında ödeme onaylanmıştır."
                            rapor_detay = f"🔍 <b>Hasar Tespiti:</b> Akut Fraktür Bulgusu<br>💰 <b>Onaylanan Tutar:</b> {random.randint(12000, 18000)} TL"
                        else:
                            st_txt, color, bg = "KAPSAM DIŞI / RED", "#ff4b4b", "rgba(255, 75, 75, 0.2)"
                            msg = "Kaza beyanı eksikliği nedeniyle provizyon reddedilmiştir."
                            rapor_detay = f"🔍 <b>Hasar Tespiti:</b> Fraktür Bulgusu (Eski Hasar)<br>❌ <b>Ret Nedeni:</b> Poliçe Özel Şartları Madde 5.1"
                    else:
                        st_txt, color, bg = "HASAR SAPTANMADI", "#D4E217", "rgba(212, 226, 23, 0.1)"
                        msg = "Analiz sonucunda tazminata konu akut hasar saptanmamıştır."
                        rapor_detay = "🔍 <b>Hasar Tespiti:</b> Negatif (Temiz Görüntü)<br>✅ <b>Dosya Durumu:</b> Tazminat ödemesi gerekmemektedir."

                    st.markdown(f"""
                        <div style="padding:15px; border-radius:12px; border:2px solid {color}; background:{bg}; color:{color}; text-align:center; font-weight:bold; font-size:22px; margin-bottom:20px;">{st_txt}</div>
                        <div style="padding:18px; border-left:5px solid {color}; background: rgba(255,255,255,0.04); border-radius: 0 15px 15px 0; color: white;">
                            <p style="margin-bottom:12px;"><b>📢 Karar Özeti:</b> {msg}</p>
                            <hr style="opacity:0.15; margin: 12px 0;">
                            <div style="line-height: 1.8;">{rapor_detay}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("İşlem için dosya yükleyiniz.")
        st.markdown('</div>', unsafe_allow_html=True)

# Ar-Ge Modülleri
for t in [tab2, tab3, tab4, tab5]:
    with t: st.markdown('<div class="glass-card" style="text-align:center;">MediSA Analiz Modülü Hazırlanıyor...</div>', unsafe_allow_html=True)

st.markdown("""<div style="position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: white; font-size: 14px; font-weight: 300; letter-spacing: 1px; text-shadow: 0 0 10px rgba(255, 255, 255, 0.8); z-index: 999;">Görüntü İşleme Dersi Projesi ✨ Miraynur Asma</div>""", unsafe_allow_html=True)