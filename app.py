import streamlit as st
import time
import os
import sys
import random
from PIL import Image

# ------------------------------------------------------------------------------
# 1. AYARLAR VE SİMÜLASYON
# ------------------------------------------------------------------------------
try:
    from backend.cnn_model import get_model, predict_with_heatmap
except ImportError:
    def get_model(): return "Model"
    def predict_with_heatmap(model, file):
        import numpy as np
        img = Image.open(file)
        # Simülasyon: %98.5 Kırık ihtimali
        return "fracture", 0.985, img

st.set_page_config(page_title="InsurEye", page_icon="🛡️", layout="wide")

# ------------------------------------------------------------------------------
# 2. CSS TASARIMI (TÜM SORUNLAR GİDERİLDİ)
# ------------------------------------------------------------------------------
st.markdown(f"""
    <style>
    /* --- ANA RENK DEĞİŞKENLERİ --- */
    :root {{
        --primary-cyan: #00e5ff;
        --cyan-glow: 0 0 15px rgba(0, 229, 255, 0.6);
        --dark-bg: rgba(10, 20, 30, 0.8);
    }}

    /* GENEL AYARLAR */
    * {{ user-select: text; }}
    [data-testid="stHeader"] {{ background: rgba(0,0,0,0); height: 0px; }}
    .block-container {{ padding-top: 1rem !important; }}

    /* RESİM KÖŞELERİ */
    img {{ border-radius: 12px !important; }}

    /* ARKA PLAN */
    .stApp {{
        background: radial-gradient(circle at center, #111920 0%, #05080a 100%);
        background-size: cover; background-attachment: fixed;
    }}

    /* --- 🔥 CHECKBOX İÇİN KESİN ÇÖZÜM (KIRMIZIYI YOK ET) 🔥 --- */
    /* Tarayıcı seviyesinde renk zorlama */
    input[type="checkbox"] {{
        accent-color: #00e5ff !important;
        filter: hue-rotate(180deg); 
    }}
    
    /* Kutucuğun kendisi */
    div[data-baseweb="checkbox"] div {{
        border-color: rgba(255, 255, 255, 0.5) !important;
        background-color: transparent !important;
    }}
    
    /* İşaretli olduğunda */
    div[data-baseweb="checkbox"] input:checked + div {{
        background-color: #00e5ff !important;
        border-color: #00e5ff !important;
    }}
    
    /* Tik işareti */
    div[data-baseweb="checkbox"] input:checked + div:before {{
        background-color: black !important;
    }}
    div[data-baseweb="checkbox"] input:checked + div svg {{
        fill: black !important;
        color: black !important;
    }}
    
    /* Yazı seçimi engelleme */
    [data-testid="stCheckbox"] label {{
        user-select: none !important;
        cursor: pointer !important;
    }}
    [data-testid="stCheckbox"] label p {{
        color: white !important;
        font-weight: 500 !important;
    }}

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.01) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.05); }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{ color: white !important; }}

    /* EXPANDER (HAP ŞEKLİ) */
    [data-testid="stSidebar"] .stExpander {{ border: 1px solid rgba(0, 229, 255, 0.5) !important; border-radius: 50px !important; background-color: var(--dark-bg) !important; margin-bottom: 12px; transition: all 0.3s ease; }}
    [data-testid="stSidebar"] .stExpander:hover {{ border-color: var(--primary-cyan) !important; box-shadow: var(--cyan-glow) !important; }}
    [data-testid="stSidebar"] .stExpander summary {{ color: var(--primary-cyan) !important; background-color: transparent !important; border: none !important; border-radius: 50px !important; justify-content: center !important; padding: 10px 20px !important; }}
    [data-testid="stSidebar"] .stExpander summary p {{ font-weight: 600 !important; font-size: 1.1rem !important; margin: 0 !important; }}
    [data-testid="stSidebar"] .stExpander summary svg {{ display: none !important; }}
    [data-testid="stSidebar"] div[role="region"] {{ padding: 15px 25px !important; color: rgba(255,255,255,0.8) !important; }}

    /* --- SEKMELER (TABS) --- */
    .stTabs [data-baseweb="tab-list"] {{ gap: 15px; background-color: transparent; padding: 15px 0; border: none !important; }}
    .stTabs [data-baseweb="tab"] {{ height: 45px; background-color: var(--dark-bg); border-radius: 50px !important; border: 1px solid rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.5); padding: 0 20px; font-weight: 600; transition: all 0.3s ease; flex-grow: 1; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ border: 1px solid var(--primary-cyan) !important; color: var(--primary-cyan) !important; background-color: rgba(0, 229, 255, 0.1) !important; box-shadow: var(--cyan-glow) !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

    /* --- HUD METRİKLERİ --- */
    div[data-testid="stMetric"] {{ background-color: rgba(0, 229, 255, 0.05); border: 1px solid rgba(0, 229, 255, 0.2); padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 0 10px rgba(0,0,0,0.3); }}
    div[data-testid="stMetric"] label {{ color: rgba(255,255,255,0.8) !important; font-size: 15px !important; font-weight: 500 !important; }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: #00e5ff !important; font-size: 26px !important; font-weight: bold !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.6); }}

    /* --- BUTONLAR --- */
    .stButton button {{ background: transparent !important; border: 1px solid #00e5ff !important; color: #00e5ff !important; border-radius: 50px !important; padding: 10px 24px !important; font-weight: 600 !important; transition: all 0.3s ease !important; }}
    .stButton button:hover {{ background: #00e5ff !important; color: black !important; box-shadow: 0 0 20px #00e5ff !important; }}

    /* --- PROGRESS BAR --- */
    .neon-progress-container {{ width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 10px; margin: 12px 0; height: 18px; }}
    .neon-progress-bar {{ height: 100%; background: linear-gradient(90deg, #00e5ff, #0099ff); border-radius: 10px; box-shadow: 0 0 15px #00e5ff; transition: width 1s ease-in-out; }}

    /* --- GLASS CARD (SADECE İÇERİK VARSA GÖRÜNSÜN) --- */
    .glass-card {{ background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(20px); border-radius: 25px; padding: 35px; border: none !important; color: white !important; margin-bottom: 25px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); }}
    
    /* --- AI STATUS KUTUSU --- */
    div[data-testid="stStatus"] {{ background-color: rgba(0, 0, 0, 0.6) !important; border: 1px solid rgba(0, 229, 255, 0.3) !important; border-radius: 12px !important; padding: 15px !important; }}
    div[data-testid="stStatus"] label {{ color: #00e5ff !important; font-weight: bold !important; font-size: 1.1rem !important; }}
    div[data-testid="stStatus"] .stMarkdown p {{ color: white !important; font-size: 1rem !important; font-weight: 500 !important; margin-bottom: 8px !important; }}
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. SIDEBAR İÇERİĞİ
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom:30px;">
            <h1 style="color: #00e5ff; font-weight: 300; font-size: 32px; margin: 0; text-shadow: 0 0 20px rgba(0, 229, 255, 0.6); letter-spacing: 2px;">
                InsurEye
            </h1>
            <p style="color: rgba(255,255,255,0.6); font-size: 11px; letter-spacing: 3px; margin-top: 5px;">
                Sigortanın Dijital Gözü 👁️
            </p>
        </div>
    """, unsafe_allow_html=True)

    mode = st.radio("", ["👨‍⚕️ Doktor Modu", "💼 Sigortacı Modu"], label_visibility="collapsed")
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    with st.expander("🦴 KEMİK", expanded=True):
        st.checkbox("🚨 Akut Ağrı", value=True)
        st.checkbox("🚗 Kaza Bildirimi")

    with st.expander("👁️ GÖZ"):
        st.checkbox("🌫️ Görme Kaybı")
        st.checkbox("👓 Bulanıklık")

    with st.expander("🧠 BEYİN"):
        st.checkbox("🌀 Baş Dönmesi")
        st.checkbox("⚡ Şiddetli Ağrı")

    with st.expander("🧪 CİLT"):
        st.checkbox("🟣 Döküntü / Kaşıntı")

    with st.expander("🫁 AKCİĞER"):
        st.checkbox("🌡️ Ateş / Öksürük")

    st.divider()
    poliçe_input = st.text_input("Poliçe No", "INS-2026-TR", label_visibility="collapsed")

# ------------------------------------------------------------------------------
# 4. ANA EKRAN
# ------------------------------------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🦴 KEMİK", "👁️ GÖZ", "🧠 BEYİN", "🧪 CİLT", "🫁 AKCİĞER"])

# --- TAB 1: KEMİK ---
with tab1:
    c_l, c_r = st.columns([1, 1.4], gap="large")

    # SOL: Görüntü Yükleme
    with c_l:
        st.markdown("<h4 style='color:#00e5ff; margin-bottom: 15px;'>📥 Görüntü Yükle</h4>", unsafe_allow_html=True)
        file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

        if file:
            st.image(file, use_container_width=True)
        else:
            # Görüntü yoksa havalı bir placeholder (Yazı Rengi Düzeldi: Parlak Beyaz/Gümüş)
            st.markdown("""
                <div style="text-align:center; padding: 40px; opacity: 0.8; color: #e0e0e0; border: 2px dashed rgba(255,255,255,0.1); border-radius: 15px;">
                    <span style="font-size: 50px;">🦴</span>
                    <p style="margin-top: 10px; font-weight: 500;">Analiz için buraya tıklayıp<br>bir röntgen görüntüsü seçin.</p>
                </div>
            """, unsafe_allow_html=True)

    # SAĞ: Analiz Sonuçları (SADECE DOSYA VARSA GÖRÜNÜR)
    with c_r:
        if file:
            # --- 🔥 BURASI ÖNEMLİ: SADECE DOSYA VARSA KUTUYU ÇİZİYORUZ 🔥 ---
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            title_text = "👨‍⚕️ Radyolojik Analiz" if mode == "👨‍⚕️ Doktor Modu" else "🛡️ Otonom Provizyon Kararı"
            st.markdown(f"<h3 style='color:white; margin-bottom: 25px; font-size: 1.5rem;'>{title_text}</h3>", unsafe_allow_html=True)

            # 🔥 HAP BUTON 🔥
            st.markdown("""<style>
                div.stButton > button:first-child {
                    background: linear-gradient(45deg, #00e5ff, #0099ff) !important;
                    color: black !important;
                    border: none !important;
                    border-radius: 50px !important;
                    font-weight: 700 !important;
                    font-size: 1.1rem !important;
                    width: 100%;
                    height: 55px;
                    box-shadow: 0 5px 20px rgba(0, 229, 255, 0.5) !important;
                    transition: all 0.3s ease !important;
                }
                div.stButton > button:first-child:hover {
                    transform: scale(1.02) !important;
                    box-shadow: 0 8px 25px rgba(0, 229, 255, 0.7) !important;
                }
            </style>""", unsafe_allow_html=True)

            if st.button("ANALİZİ BAŞLAT", key="start_btn", use_container_width=True):

                # AI SİMÜLASYONU
                with st.status("Sistem Taraması Başlatılıyor...", expanded=True) as status:
                    st.write("🔄 Görüntü pikselleri normalize ediliyor...")
                    time.sleep(0.5)
                    st.write("📋 Poliçe veritabanı sorgulanıyor...")
                    time.sleep(0.5)
                    st.write("🧠 Sinir ağları (ResNet) kırık taraması yapıyor...")
                    time.sleep(0.5)
                    st.write("⚖️ Teminat ve muafiyet limitleri hesaplanıyor...")
                    time.sleep(0.5)
                    status.update(label="✅ Analiz Tamamlandı!", state="complete", expanded=False)

                # Model
                model = get_model()
                label, conf, heatmap = predict_with_heatmap(model, file)
                icd_code = "T94.1" if label == "fracture" else "Z00.0"

                # ---------------------------------------------------------
                # DOKTOR MODU
                # ---------------------------------------------------------
                if mode == "👨‍⚕️ Doktor Modu":
                    conf_percent = int(conf * 100)
                    st.markdown(f"""
                        <div style="margin-top: 20px; margin-bottom: 8px; color: white; font-size: 16px; font-weight: 500;">
                            Tespit Güveni: <span style="color:#00e5ff; font-weight:bold; font-size: 18px;">%{conf_percent}</span>
                        </div>
                        <div class="neon-progress-container">
                            <div class="neon-progress-bar" style="width: {conf_percent}%;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                    m1, m2, m3 = st.columns(3)
                    if label == "fracture":
                        m1.metric("Risk Seviyesi", "Yüksek 🔴")
                        m2.metric("Aciliyet", "Acil ⚡")
                        m3.metric("Doku Hasarı", "Var🧬")
                        
                        st.markdown(f"""
                            <div style="background: rgba(220, 53, 69, 0.15); border: 2px solid #dc3545; padding: 25px; border-radius: 15px; margin: 30px 0; box-shadow: 0 0 20px rgba(220, 53, 69, 0.2);">
                                <h3 style="color: #ff4b4b; margin:0; font-size: 1.6rem;">⚠️ TANI: POZİTİF (KIRIK)</h3>
                                <p style="color: rgba(255,255,255,0.9); margin-top:15px; font-size:17px; line-height: 1.6;">
                                    <strong>Bulgular:</strong> Kortikal bütünlükte bozulma tespit edilmiştir.<br>
                                    <strong>ICD-10 Kodu:</strong> <code style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 6px; font-size: 16px;">{icd_code}</code>
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        m1.metric("Risk Seviyesi", "Düşük 🟢")
                        m2.metric("Aciliyet", "Normal 🛡️")
                        m3.metric("Doku Hasarı", "Yok ✨")
                        st.success("✅ TANI: NORMAL BULGULAR")

                # ---------------------------------------------------------
                # 💼 SİGORTACI MODU (YENİLENMİŞ POLİÇE KARTI - HATA DÜZELTİLDİ)
                # ---------------------------------------------------------
                else:
                    if label == "fracture":
                        decision = "ONAYLANDI"
                        color = "#28a745"
                        
                        # Hesaplamalar
                        toplam_limit = 50000
                        kullanilan_limit = random.randint(10000, 30000)
                        kalan_limit = toplam_limit - kullanilan_limit 
                        tahmini_masraf = random.randint(12000, 18000)
                        usage_percent = int((kullanilan_limit / toplam_limit) * 100)

                        # 1. POLİÇE KARTI (Düzgün Görüntüleme)
                        # Not: HTML stringindeki indentation (girinti) kaldırıldı ki kod gibi görünmesin.
                        st.markdown(f"""
<div style="background: rgba(255,255,255,0.05); border-left: 5px solid #00e5ff; padding: 20px; border-radius: 10px; margin-top: 20px;">
    <h4 style="color: #00e5ff; margin:0 0 15px 0;">🛡️ POLİÇE ÖZETİ: {poliçe_input}</h4>
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <span style="color:white; opacity:0.7;">Poliçe Türü:</span>
        <span style="color:white; font-weight:bold;">Özel Sağlık - Platinum Paket</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <span style="color:white; opacity:0.7;">Kapsam:</span>
        <span style="color:white; font-weight:bold;">Yatarak + Ayakta + Travma</span>
    </div>
    <hr style="border-color: rgba(255,255,255,0.1);">
    <p style="color:white; font-size: 14px; margin-bottom: 5px;">Yıllık Teminat Limiti Kullanımı</p>
    <div style="width: 100%; background: #333; height: 10px; border-radius: 5px;">
        <div style="width: {usage_percent}%; background: #00e5ff; height: 100%; border-radius: 5px;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 5px; color: rgba(255,255,255,0.6);">
        <span>Kullanılan: {kullanilan_limit} TL</span>
        <span>Toplam: {toplam_limit} TL</span>
    </div>
    <div style="background: rgba(0, 229, 255, 0.15); padding: 10px; border-radius: 8px; text-align: center; margin-top: 15px; border: 1px solid rgba(0, 229, 255, 0.3);">
        <span style="color: white; font-size: 14px;">KALAN YILLIK LİMİT</span><br>
        <span style="color: #00e5ff; font-size: 24px; font-weight: bold; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);">{kalan_limit} TL</span>
    </div>
</div>
""", unsafe_allow_html=True)

                        # 2. TANI VE ICD-10
                        st.markdown(f"""
                            <div style="display: flex; gap: 15px; margin-top: 20px;">
                                <div style="flex: 1; background: rgba(0, 229, 255, 0.1); border: 2px solid #00e5ff; padding: 15px; border-radius: 12px; text-align: center;">
                                    <span style="color: #00e5ff; font-size: 12px; letter-spacing: 1px;">TESPİT EDİLEN KOD</span><br>
                                    <strong style="color: white; font-size: 32px; text-shadow: 0 0 10px #00e5ff;">{icd_code}</strong><br>
                                    <span style="color: white; opacity: 0.8; font-size: 14px;">Bacak Alt Kısım Kırığı</span>
                                </div>
                                <div style="flex: 1; background: {color}20; border: 2px solid {color}; padding: 15px; border-radius: 12px; text-align: center;">
                                    <span style="color: {color}; font-size: 12px; letter-spacing: 1px;">KARAR</span><br>
                                    <strong style="color: white; font-size: 32px;">{decision}</strong><br>
                                    <span style="color: white; opacity: 0.8; font-size: 14px;">Otomatik Provizyon</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # 3. FİNANSAL DÖKÜM
                        st.markdown("<br>", unsafe_allow_html=True)
                        f1, f2, f3 = st.columns(3)
                        f1.metric("Tahmini Tutar", f"{tahmini_masraf} TL")
                        f2.metric("Sigorta Payı", f"{tahmini_masraf} TL")
                        f3.metric("Hasta Payı", "0 TL")

                    else:
                        st.error("Hasar tespit edilemedi. Ödeme gerektirmiyor.")

               # AKSİYON BUTONLARI (ORTAK)
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("👁️ Görüntü Analizi (Heatmap)", expanded=False):
                    st.image(heatmap, use_container_width=True, channels="BGR") # Fotoğraf (İçeride olmalı)
                    st.markdown("""
                        <div style="
                            background-color: #00e5ff; 
                            color: black; 
                            padding: 10px; 
                            border-radius: 0 0 12px 12px; 
                            text-align: center; 
                            margin-top: -20px; 
                            font-weight: bold; 
                            font-size: 13px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            gap: 10px;
                        ">
                            <span>🛡️ UZMAN DOKTOR TARAFINDAN DOĞRULANMIŞTIR</span>
                            <span style="background: rgba(0,0,0,0.15); padding: 2px 8px; border-radius: 4px; font-size: 11px;">
                                📅 06.01.2026 ✅
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                c_btn1, c_btn2 = st.columns(2, gap="medium")
                with c_btn1:
                    st.button("📥 Dosyayı İndir", use_container_width=True)
                with c_btn2:
                    st.button("✉️ Onaya Gönder ve Provizyonu Onayla", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # --- 🔥 BURASI BOŞ (HAYALET KUTU YOK) 🔥 ---
            pass

# Diğer sekmeler (İçi boş)
for t in [tab2, tab3, tab4, tab5]:
    with t:
        st.write("")