import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import time
from functools import wraps
from io import BytesIO
import statistics
import math
import re
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================.
st.set_page_config(
    page_title="NYZTrade Stock Valuation + Screener Professional dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MOBILE-OPTIMIZED CSS STYLING
# ============================================================================.
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        margin: 0.5rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header h3 {
        font-size: 1.1rem;
        margin-bottom: 0.3rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    .main-header p {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.8;
    }
    
    .auth-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
        padding: 0 0.5rem;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem 0.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stat-card h3 {
        font-size: 1.5rem;
        margin: 0 0 0.25rem 0;
        font-weight: 600;
    }
    
    .stat-card p {
        font-size: 0.8rem;
        margin: 0;
        opacity: 0.9;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.1));
        border: 2px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #059669;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid rgba(124, 58, 237, 0.3);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.15);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: bold;
        color: #a78bfa;
        margin: 0.3rem 0;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #c4b5fd;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.3;
    }
    
    .company-header {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(167, 139, 250, 0.3);
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.15);
    }
    
    .company-title {
        font-size: 1.8rem;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
        font-weight: 700;
        line-height: 1.3;
    }
    
    .company-info {
        color: #a78bfa;
        font-size: 0.9rem;
        margin: 0.15rem 0;
        line-height: 1.4;
    }
    
    .fair-value-card {
        background: linear-gradient(135deg, #059669, #10b981);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        margin: 1rem 0;
    }
    
    .fair-value-title {
        font-size: 1rem;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    .fair-value-amount {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 1rem 0;
        line-height: 1.2;
    }
    
    .fair-value-details {
        font-size: 0.9rem;
        opacity: 0.8;
        line-height: 1.4;
    }
    
    .section-header {
        font-size: 1.3rem;
        color: #a78bfa;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(167, 139, 250, 0.3);
        font-weight: 600;
    }
    
    .recommendation-card {
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
    
    .rec-strong-buy {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
    }
    
    .rec-buy {
        background: linear-gradient(135deg, #0891b2, #06b6d4);
        color: white;
    }
    
    .rec-hold {
        background: linear-gradient(135deg, #ca8a04, #eab308);
        color: white;
    }
    
    .rec-avoid {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
    }
    
    .valuation-box {
        background: rgba(30, 27, 75, 0.6);
        border: 1px solid rgba(167, 139, 250, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    
    .valuation-method {
        color: #a78bfa;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .valuation-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.4rem 0;
        padding: 0.4rem;
        border-radius: 6px;
        background: rgba(167, 139, 250, 0.05);
        font-size: 0.9rem;
    }
    
    .valuation-label {
        color: #c4b5fd;
        font-weight: 500;
    }
    
    .valuation-value {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    .welcome-section {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(167, 139, 250, 0.1));
        border-radius: 15px;
        padding: 2rem 1rem;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    .welcome-title {
        font-size: 2rem;
        color: #a78bfa;
        margin-bottom: 1rem;
        font-weight: 700;
        line-height: 1.3;
    }
    
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #c4b5fd;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }
    
    .feature-list {
        text-align: left;
        max-width: 600px;
        margin: 0 auto;
        color: #e2e8f0;
    }
    
    .feature-list li {
        margin: 0.4rem 0;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* 52-week range styling */
    .range-container {
        background: rgba(30, 27, 75, 0.6);
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid rgba(167, 139, 250, 0.3);
    }
    
    .range-labels {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #a78bfa;
    }
    
    .range-bar {
        width: 100%;
        height: 18px;
        background: linear-gradient(90deg, #dc2626 0%, #eab308 50%, #059669 100%);
        border-radius: 9px;
        position: relative;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .range-indicator {
        position: absolute;
        top: -3px;
        width: 4px;
        height: 24px;
        background: #e2e8f0;
        border-radius: 2px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
    }
    
    .range-info {
        text-align: center;
        margin-top: 1rem;
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        color: #c4b5fd;
        text-align: center;
        padding: 1.5rem 1rem;
        border-radius: 12px;
        margin-top: 2rem;
        border: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    .disclaimer {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 1rem;
        font-style: italic;
        line-height: 1.4;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0.5rem;
            margin: 0.25rem 0 0.75rem 0;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .main-header h3 {
            font-size: 1rem;
        }
        
        .main-header p {
            font-size: 0.8rem;
        }
        
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            padding: 0 0.25rem;
        }
        
        .stat-card {
            padding: 0.75rem 0.5rem;
        }
        
        .stat-card h3 {
            font-size: 1.2rem;
        }
        
        .company-title {
            font-size: 1.4rem;
        }
        
        .fair-value-amount {
            font-size: 1.8rem;
        }
        
        .welcome-title {
            font-size: 1.6rem;
        }
        
        .metric-card {
            padding: 0.75rem;
            min-height: 85px;
        }
        
        .metric-value {
            font-size: 1.2rem;
        }
        
        .metric-label {
            font-size: 0.7rem;
        }
        
        .valuation-row {
            font-size: 0.8rem;
            padding: 0.3rem;
        }
        
        .section-header {
            font-size: 1.1rem;
        }
    }
    
    @media (max-width: 480px) {
        .stats-container {
            grid-template-columns: 1fr;
        }
        
        .main-header h1 {
            font-size: 1.3rem;
        }
        
        .company-title {
            font-size: 1.2rem;
        }
        
        .fair-value-amount {
            font-size: 1.6rem;
        }
        
        .metric-value {
            font-size: 1rem;
        }
    }
    
    /* Ensure proper contrast and visibility */
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    /* Fix potential black screen issues */
    .stApp > div {
        background: transparent !important;
    }
    
    .main > div {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PASSWORD AUTHENTICATION
# ============================================================================
def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "nytddemo", "premium": "zuktasempire", "niyas": "buffett123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div class="auth-container">
            <h1>🎯 NYZTrade Comprehensive Platform</h1>
            <h3>Professional Stock Analysis & Screening</h3>
            <p>Advanced Valuation • Industry Screening • Portfolio Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("👤 Username", key="username", placeholder="Enter username")
            st.text_input("🔒 Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True, type="primary")
            
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================================
# COMPREHENSIVE INDIAN STOCKS DATABASE
# ============================================================================
"""
Indian Stocks Database
Generated from stocks_universe_categorized_enhanced.csv
Total Categories: 117
Total Stocks: 8984
"""

"""
Indian Stocks Database
Generated from stocks_universe_categorized_enhanced.csv
Total Categories: 117
Total Stocks: 8984
"""

INDIAN_STOCKS = {
    "Advertising Agencies": {
        "AMMLTD.BO": "Appu Marketing & Manufacturing",
        "GOVMC.BO": "GOOD VALUE MARKETING CO.LTD.",
        "NEERAJ.BO": "NEERAJ PAPER MARKETING LIMITED",
        "PRESSMN.BO": "PRESSMAN ADVERTISING LIMITED",
        "PRESSMN.NS": "Pressman Advertising Limited",
        "SPECMKT.BO": "SPECULAR MARKETING & FINANCING",
        "SURYAMARK.BO": "SURYA MARKETING LTD"
    },

    "Aerospace/Defense - Major Diversified": {
        "ABGSHIP.NS": "ABG Shipyard Limited",
        "BEL.NS": "Bharat Electronics Limited",
        "BHARATIDIL.NS": "Bharati Defence And Infrastructure Limited",
        "RDEL.NS": "Reliance Defence and Engineering Limited",
        "COCHINSHIP.BO": "COCHIN SHIPYARD LTD."
    },

    "Agricultural Chemicals": {
        "AGRITECH.NS": "Agri-Tech (India) Ltd",
        "AGRODUTCH-BE.NS": "AGRO DUTCH INDUSTRIES LTD",
        "AGRODUTCH.BO": "AGRO DUTCH INDUSTRIES LTD.",
        "ARIES.NS": "ARIES AGRO LIMITED",
        "ARIES.BO": "Aries Agro Limited",
        "ARIES.NS": "Aries Agro Limited",
        "ASHAI.BO": "Ashiana Agro Industries Ltd.",
        "ASIANFR.BO": "ASIAN FERTILIZERS LTD.",
        "BAMBINO.BO": "Bambino Agro Industries Ltd.",
        "BAYERCROP.NS": "Bayer CropScience Limited",
        "BELAGRO.BO": "Bell Agromachina Ltd.",
        "BHARATRAS.NS": "Bharat Rasayan Limited",
        "BHASKAGR.BO": "BHASKAR AGROCHEMICALS LTD.",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "CRYPTAG.BO": "CRYPTOGEN AGRO INDUSTRIES LTD.",
        "DEEPAKFERT.NS": "DEEPAK FERTILIZERS AND PETROCHE",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "DHANUKA.NS": "Dhanuka Agritech Limited",
        "DHARNAG.BO": "DHARNENDRA AGRO FOOD INDUSTRIE",
        "EXCELCROP.NS": "Excel Crop Care Limited",
        "FACT.NS": "The Fertilisers And Chemicals Travancore Limited",
        "GNFC.NS": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
        "GOKULAGRO.BO": "Gokul Agro Resources Ltd",
        "GREENFIRE.NS": "Proseed India Limited",
        "GSFC.NS": "Gujarat State Fertilizers & Chemicals Limited",
        "HATSUN.NS": "HATSUN AGRO PRODUC INR1",
        "HATSUN.BO": "Hatsun Agro Product Limited",
        "HERUKAG.BO": "HERUK AGRO FOODS LTD.",
        "IFBAGRO.BO": "IFB AGRO INDUSTRIES LTD.",
        "INSECTICID.NS": "Insecticides (India) Limited",
        "JAYAGROGN.NS": "JAYANT AGRO ORGANICS LIMITED",
        "JAYAGROGN.BO": "JAYANT AGRO-ORGANICS LTD.",
        "JVLAGRO.BO": "JVL Agro Industries Ltd",
        "KGNAGRO.BO": "KGN AGRO INTERNATIONALS LTD.",
        "MADRASFERT.NS": "MADRAS FERTILIZERS INR10(DEMAT)",
        "MADRASFERT.BO": "Madras Fertilizer Limited",
        "MADRASFERT.NS": "Madras Fertilizers Limited",
        "MANGCHEFER.NS": "Mangalore Chemicals & Fertilizers Limited",
        "MAYAGRP.BO": "MAYA AGRO PRODUCTS LTD.",
        "MEGH.NS": "Meghmani Organics Limited",
        "MONESHIA.BO": "MONESHI AGRO INDUSTRIES LTD.",
        "MONSANTO.NS": "Monsanto India Limited",
        "MPAGI.BO": "M. P. Agro Industries Ltd",
        "NAPL.BO": "Naturite Agro Products Limited",
        "NATHBIOGEN.NS": "Nath Bio-Genes (India) Limited",
        "NEAGI.BO": "Neelamalai Agro Industries Ltd.",
        "NEPCAGRO.BO": "NEPC AGRO FOODS LTD.",
        "NFL.BO": "National Fertilizers Ltd.",
        "NFL.NS": "National Fertilizers Limited",
        "NIJJER.BO": "NIJJER AGRO FOODS LTD.",
        "OCEAGRO.BO": "Ocean Agro (India) Limited",
        "OSWALAGRO.BO": "OSWAL AGRO MILLS LTD.",
        "PARKERAC.BO": "Parker Agrochem Exports Ltd.",
        "PICCADIL.BO": "Piccadily Agro Industries Limited",
        "PIIND.NS": "PI Industries Limited",
        "PIONAGR.BO": "Pioneer Agro Extracts Ltd",
        "PRIMAGR.BO": "Prima Agro Limited",
        "RAASHIF.BO": "RAASHI FERTILIZERS LTD.",
        "RAFL.BO": "Raghuvansh Agrofarms Limited",
        "RAJAGRO.BO": "Raj Agro Mills Ltd.",
        "RALLIS.NS": "Rallis India Limited",
        "RATNAMAGRO.BO": "RATNAMANI AGRO INDUSTRIES LTD",
        "RCF.NS": "Rashtriya Chemicals And Fertilizers Limited",
        "REIAGROLTD-BE.NS": "REI AGRO LTD INR1",
        "REIAGROLTD.NS": "REI AGRO LTD INR1",
        "REIAGROLTD.BO": "REI AGRO LTD.",
        "REIAGROLTD6.BO": "REIAGROLTD6.BO",
        "RKB.BO": "RKB AGRO INDUSTRIES LIMITED",
        "SANJAG.BO": "SANJIVANI AGRO INDUSTRIES LTD.",
        "SATGAGR.BO": "SATGURU AGRO INDUSTRIES LTD.",
        "SEASTAG.BO": "SOUTH EAST AGRO INDUSTRIES LTD",
        "SH-ANJY.BO": "SHRI ANJANEY AGRO FOODS LTD.",
        "SHARDACROP.NS": "Sharda Cropchem Limited",
        "SHIVAAGRO.BO": "SHIVA GLOBAL AGRO INDUSTRIES L",
        "SPIC.NS": "Southern Petrochemical Industries Corporation Limited",
        "SPTRSHI.BO": "Saptarishi Agro Industries Limited",
        "SUNILAGR.BO": "Sunil Agro Foods Ltd",
        "SYPAGFD.BO": "SYP AGRO FOODS LTD.",
        "TEEAI.BO": "Teesta Agro Industries Ltd.",
        "UMREAGR.BO": "CIAN AGRO IND & INFRA LTD",
        "UNQAGRO.BO": "UNIQUE AGRO PROCESSORS (INDIA)",
        "UPL.NS": "UPL Limited",
        "USHERAGRO.BO": "USHER AGRO LTD.",
        "VITANAGRO.BO": "VITAN AGRO INDUSTRIES LTD",
        "VRUNAGR.BO": "VARUNA AGROPROTEINS LTD.",
        "ZUARI.BO": "ZUARI AGRO CHEMICALS LTD.",
        "ZUARI.NS": "Zuari Agro Chemicals Limited",
        "ZUARIGLOB.NS": "Zuari Global Limited"
    },

    "Air Delivery & Freight Services": {
        "ALLCARGO.NS": "Allcargo Logistics Limited",
        "ARSHIYA.NS": "Arshiya Limited",
        "BLUEDART.NS": "Blue Dart Express Limited",
        "CONCOR.NS": "Container Corporation of India Limited",
        "GATI.NS": "Gati Limited",
        "GDL.NS": "Gateway Distriparks Limited",
        "NAVKARCORP.NS": "Navkar Corporation Limited",
        "PATINTLOG.NS": "Patel Integrated Logistics Limited",
        "SICAL.NS": "Sical Logistics Limited",
        "SNOWMAN.NS": "Snowman Logistics Limited",
        "TCI.NS": "Transport Corporation of India Limited"
    },

    # ========================================================================
    # >>> ADD THE REST OF YOUR CATEGORY LISTS BELOW, IN THE SAME FORMAT <<<
    #
    #     "Category Name": {
    #         "TICKER.NS": "Company Name",
    #         "TICKER2.NS": "Company Name 2"      <- last entry: no comma
    #     },
    # ========================================================================

}

# ============================================================================
# COMPREHENSIVE INDUSTRY-SPECIFIC BENCHMARKS SYSTEM
# ============================================================================

# Industry-specific benchmarks based on Indian market analysis
INDUSTRY_BENCHMARKS = {
    # Financial Services - Industry Specific
    "Credit Services": {'pe': 16.0, 'pb': 2.8, 'roe': 18.0, 'ev_ebitda': 10.0, 'debt_equity': 4.5},
    "Financial Services": {'pe': 15.0, 'pb': 2.2, 'roe': 16.0, 'ev_ebitda': 9.0, 'debt_equity': 3.8},
    "Insurance - Life": {'pe': 20.0, 'pb': 2.0, 'roe': 14.0, 'ev_ebitda': 12.0, 'debt_equity': 0.2},
    "Insurance - Property & Casualty": {'pe': 18.0, 'pb': 1.8, 'roe': 15.0, 'ev_ebitda': 11.0, 'debt_equity': 0.3},
    "Money Center Banks": {'pe': 12.0, 'pb': 1.2, 'roe': 15.0, 'ev_ebitda': 8.0, 'debt_equity': 0.1},
    
    # Technology - Industry Specific
    "Information Technology Services": {'pe': 24.0, 'pb': 4.2, 'roe': 22.0, 'ev_ebitda': 16.0, 'debt_equity': 0.1},
    "Wireless Communications": {'pe': 18.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 12.0, 'debt_equity': 1.2},
    
    # Healthcare & Pharma - Industry Specific
    "Drug Manufacturers - Major": {'pe': 26.0, 'pb': 3.2, 'roe': 18.0, 'ev_ebitda': 15.0, 'debt_equity': 0.3},
    "Drug Manufacturers - Other": {'pe': 28.0, 'pb': 3.5, 'roe': 16.0, 'ev_ebitda': 16.0, 'debt_equity': 0.2},
    "Medical Services": {'pe': 32.0, 'pb': 3.8, 'roe': 17.0, 'ev_ebitda': 18.0, 'debt_equity': 0.8},
    
    # Auto & Manufacturing - Industry Specific  
    "Auto Manufacturers - Major": {'pe': 18.0, 'pb': 2.2, 'roe': 14.0, 'ev_ebitda': 10.0, 'debt_equity': 0.8},
    "Auto Parts": {'pe': 22.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 12.0, 'debt_equity': 0.6},
    "Diversified Electronics": {'pe': 24.0, 'pb': 3.0, 'roe': 17.0, 'ev_ebitda': 13.0, 'debt_equity': 0.4},
    "Diversified Machinery": {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 11.0, 'debt_equity': 0.7},
    
    # Materials & Chemicals - Industry Specific
    "Steel & Iron": {'pe': 12.0, 'pb': 1.0, 'roe': 12.0, 'ev_ebitda': 6.0, 'debt_equity': 1.5},
    "Cement & Aggregates": {'pe': 16.0, 'pb': 1.8, 'roe': 13.0, 'ev_ebitda': 8.0, 'debt_equity': 1.0},
    "Chemicals - Major Diversified": {'pe': 22.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 12.0, 'debt_equity': 0.5},
    "Agricultural Chemicals": {'pe': 20.0, 'pb': 2.2, 'roe': 16.0, 'ev_ebitda': 11.0, 'debt_equity': 0.6},
    
    # Energy & Utilities - Industry Specific
    "Oil & Gas Operations": {'pe': 8.0, 'pb': 0.8, 'roe': 12.0, 'ev_ebitda': 5.0, 'debt_equity': 0.6},
    "Oil & Gas Refining & Marketing": {'pe': 10.0, 'pb': 1.0, 'roe': 10.0, 'ev_ebitda': 6.0, 'debt_equity': 0.8},
    "Electric Utilities": {'pe': 14.0, 'pb': 1.2, 'roe': 11.0, 'ev_ebitda': 8.0, 'debt_equity': 1.8},
    "Gas Utilities": {'pe': 16.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 9.0, 'debt_equity': 1.5},
    "Renewable Energy": {'pe': 25.0, 'pb': 2.0, 'roe': 10.0, 'ev_ebitda': 12.0, 'debt_equity': 2.2},
    
    # Consumer - Industry Specific
    "Food - Major Diversified": {'pe': 35.0, 'pb': 4.5, 'roe': 18.0, 'ev_ebitda': 18.0, 'debt_equity': 0.3},
    "Jewelry Stores": {'pe': 25.0, 'pb': 2.8, 'roe': 16.0, 'ev_ebitda': 15.0, 'debt_equity': 0.4},
    "Retail - Apparel & Accessories": {'pe': 28.0, 'pb': 3.2, 'roe': 17.0, 'ev_ebitda': 16.0, 'debt_equity': 0.6},
    
    # Others
    "Real Estate Development": {'pe': 15.0, 'pb': 1.2, 'roe': 8.0, 'ev_ebitda': 12.0, 'debt_equity': 2.5},
    "Textile Industrial": {'pe': 18.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 10.0, 'debt_equity': 0.9},
}

# Cap-size specific multipliers for benchmarks
CAP_SIZE_MULTIPLIERS = {
    'Large': {'pe': 1.0, 'pb': 1.0, 'ev_ebitda': 1.0},      # Base benchmarks
    'Mid': {'pe': 1.15, 'pb': 1.1, 'ev_ebitda': 1.1},       # 10-15% premium for growth
    'Small': {'pe': 1.25, 'pb': 1.2, 'ev_ebitda': 1.15}     # 15-25% premium for higher growth
}

# Sector mapping for fallback when industry not found
INDUSTRY_TO_SECTOR = {
    # Financial Services
    "Credit Services": "Financial Services", 
    "Financial Services": "Financial Services",
    "Insurance - Life": "Financial Services",
    "Insurance - Property & Casualty": "Financial Services",
    "Money Center Banks": "Financial Services",
    
    # Technology
    "Information Technology Services": "Technology",
    "Wireless Communications": "Technology",
    
    # Healthcare & Pharma
    "Drug Manufacturers - Major": "Healthcare & Pharma",
    "Drug Manufacturers - Other": "Healthcare & Pharma",
    "Medical Services": "Healthcare & Pharma",
    
    # Industrial & Manufacturing
    "Diversified Electronics": "Industrial & Manufacturing",
    "Diversified Machinery": "Industrial & Manufacturing",
    "Steel & Iron": "Industrial & Manufacturing",
    "Auto Manufacturers - Major": "Industrial & Manufacturing",
    "Auto Parts": "Industrial & Manufacturing",
    
    # Energy & Utilities
    "Electric Utilities": "Energy & Utilities",
    "Gas Utilities": "Energy & Utilities",
    "Oil & Gas Operations": "Energy & Utilities",
    "Oil & Gas Refining & Marketing": "Energy & Utilities",
    "Renewable Energy": "Energy & Utilities",
    
    # Consumer & Retail
    "Food - Major Diversified": "Consumer & Retail",
    "Jewelry Stores": "Consumer & Retail",
    "Retail - Apparel & Accessories": "Consumer & Retail",
    
    # Materials & Chemicals
    "Agricultural Chemicals": "Materials & Chemicals",
    "Cement & Aggregates": "Materials & Chemicals",
    "Chemicals - Major Diversified": "Materials & Chemicals",
    
    # Real Estate & Construction
    "Real Estate Development": "Real Estate & Construction",
    
    # Textiles
    "Textile Industrial": "Textiles"
}

# Fallback sector benchmarks
SECTOR_BENCHMARKS = {
    'Financial Services': {'pe': 15.0, 'pb': 2.0, 'roe': 16.0, 'ev_ebitda': 10.0},
    'Technology': {'pe': 24.0, 'pb': 4.0, 'roe': 22.0, 'ev_ebitda': 16.0},
    'Healthcare & Pharma': {'pe': 28.0, 'pb': 3.4, 'roe': 17.0, 'ev_ebitda': 16.0},
    'Industrial & Manufacturing': {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 11.0},
    'Energy & Utilities': {'pe': 12.0, 'pb': 1.2, 'roe': 11.0, 'ev_ebitda': 7.0},
    'Consumer & Retail': {'pe': 30.0, 'pb': 3.5, 'roe': 17.0, 'ev_ebitda': 16.0},
    'Materials & Chemicals': {'pe': 18.0, 'pb': 2.0, 'roe': 14.0, 'ev_ebitda': 10.0},
    'Real Estate & Construction': {'pe': 15.0, 'pb': 1.2, 'roe': 8.0, 'ev_ebitda': 12.0},
    'Textiles': {'pe': 18.0, 'pb': 1.5, 'roe': 12.0, 'ev_ebitda': 10.0},
    'Other': {'pe': 20.0, 'pb': 2.5, 'roe': 15.0, 'ev_ebitda': 12.0}
}

# ============================================================================
# TECHNICAL ANALYSIS FUNCTIONS
# ============================================================================
@st.cache_data(ttl=3600)
def fetch_price_history(ticker, period="3mo"):
    """Fetch historical price data for technical analysis"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None
        return hist
    except:
        return None

def calculate_supertrend(high, low, close, period=10, multiplier=3):
    """Calculate SuperTrend indicator"""
    try:
        # Calculate ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Calculate basic upper and lower bands
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Initialize SuperTrend
        supertrend = pd.Series(index=close.index, dtype=float)
        direction = pd.Series(index=close.index, dtype=int)
        
        # Calculate SuperTrend
        for i in range(1, len(close)):
            if pd.isna(upper_band.iloc[i]) or pd.isna(lower_band.iloc[i]):
                continue
                
            # Current upper and lower bands
            curr_upper = upper_band.iloc[i]
            curr_lower = lower_band.iloc[i]
            prev_close = close.iloc[i-1]
            curr_close = close.iloc[i]
            
            # Adjust bands
            if curr_upper < upper_band.iloc[i-1] or prev_close > upper_band.iloc[i-1]:
                upper_band.iloc[i] = curr_upper
            else:
                upper_band.iloc[i] = upper_band.iloc[i-1]
                
            if curr_lower > lower_band.iloc[i-1] or prev_close < lower_band.iloc[i-1]:
                lower_band.iloc[i] = curr_lower
            else:
                lower_band.iloc[i] = lower_band.iloc[i-1]
            
            # Determine trend direction
            if i == 1:
                direction.iloc[i] = 1 if curr_close <= lower_band.iloc[i] else -1
                supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
            else:
                prev_supertrend = supertrend.iloc[i-1]
                prev_direction = direction.iloc[i-1]
                
                if prev_direction == 1 and curr_close >= lower_band.iloc[i]:
                    direction.iloc[i] = -1
                    supertrend.iloc[i] = upper_band.iloc[i]
                elif prev_direction == -1 and curr_close <= upper_band.iloc[i]:
                    direction.iloc[i] = 1
                    supertrend.iloc[i] = lower_band.iloc[i]
                else:
                    direction.iloc[i] = prev_direction
                    supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
        
        # Return signal: 1 for bullish (price > supertrend), -1 for bearish
        signal = (close > supertrend).astype(int) * 2 - 1
        
        return {
            'supertrend': supertrend,
            'direction': direction,
            'signal': signal.iloc[-1] if len(signal) > 0 else 0,
            'upper_band': upper_band,
            'lower_band': lower_band
        }
    except Exception as e:
        return None

def is_near_52w_high(price, high_52w, threshold=0.95):
    """Check if current price is near 52-week high"""
    if not price or not high_52w or high_52w <= 0:
        return False
    return (price / high_52w) >= threshold

def get_technical_signals(ticker):
    """Get comprehensive technical signals for a stock"""
    hist = fetch_price_history(ticker, period="6mo")
    if hist is None or len(hist) < 50:
        return None
    
    try:
        # Calculate SuperTrend
        supertrend_data = calculate_supertrend(
            hist['High'], 
            hist['Low'], 
            hist['Close']
        )
        
        if not supertrend_data:
            return None
        
        # Get current price and 52-week high
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].rolling(window=252).max().iloc[-1]
        
        # Additional technical indicators
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # Volume trend
        avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
        recent_volume = hist['Volume'].iloc[-5:].mean()
        
        return {
            'supertrend_signal': supertrend_data['signal'],
            'supertrend_value': supertrend_data['supertrend'].iloc[-1] if not pd.isna(supertrend_data['supertrend'].iloc[-1]) else None,
            'near_52w_high': is_near_52w_high(current_price, high_52w),
            'price_vs_52w_high': (current_price / high_52w) if high_52w > 0 else 0,
            'above_sma20': current_price > sma_20 if not pd.isna(sma_20) else False,
            'above_sma50': current_price > sma_50 if not pd.isna(sma_50) else False,
            'volume_surge': recent_volume > avg_volume * 1.2 if avg_volume > 0 else False,
            'current_price': current_price
        }
    except Exception as e:
        return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_all_tickers():
    """Get list of all ticker symbols"""
    tickers = []
    for category_stocks in INDIAN_STOCKS.values():
        tickers.extend(category_stocks.keys())
    return tickers

def get_stocks_by_category(category):
    """Get stocks in a specific category"""
    return INDIAN_STOCKS.get(category, {})

def get_all_categories():
    """Get list of all categories"""
    return list(INDIAN_STOCKS.keys())

def search_stock(query):
    """Search for stocks by ticker or name"""
    results = {}
    query_upper = query.upper()
    
    for category, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_upper in ticker.upper() or query_upper in name.upper():
                if category not in results:
                    results[category] = {}
                results[category][ticker] = name
    
    return results

def get_stock_info(ticker):
    """Get stock information by ticker"""
    for category, stocks in INDIAN_STOCKS.items():
        if ticker in stocks:
            return {
                "ticker": ticker,
                "name": stocks[ticker],
                "category": category
            }
    return None

def get_sector_for_industry(industry):
    """Get broad sector for a given industry"""
    return INDUSTRY_TO_SECTOR.get(industry, "Other")

# Statistics
TOTAL_STOCKS = sum(len(stocks) for stocks in INDIAN_STOCKS.values())
TOTAL_CATEGORIES = len(INDIAN_STOCKS)

# ============================================================================
# STOCK DATA FETCHING AND CACHING
# ============================================================================
def retry_with_backoff(retries=3, backoff_in_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=3600)
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def fetch_stock_data(ticker):
    """Fetch stock data with caching and retry mechanism"""
    try:
        time.sleep(0.5)  # Rate limiting
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        return info, None
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate" in error_msg.lower():
            return None, "Rate limit reached"
        return None, str(e)[:100]

def get_stock_fundamentals(ticker):
    """Get key fundamental metrics for a stock with enhanced sector analysis"""
    info, error = fetch_stock_data(ticker)
    
    if error or not info:
        return None
    
    try:
        # Extract key metrics
        market_cap = info.get('marketCap', 0)
        fundamentals = {
            'ticker': ticker,
            'name': info.get('longName', info.get('shortName', 'Unknown')),
            'price': info.get('currentPrice', info.get('regularMarketPrice')),
            'market_cap': market_cap,
            'trailing_pe': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            'profit_margin': info.get('profitMargins'),
            'debt_to_equity': info.get('debtToEquity'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'volume': info.get('volume') or info.get('regularMarketVolume'),
            'avg_volume': info.get('averageVolume') or info.get('averageDailyVolume10Day'),
            'trailing_eps': info.get('trailingEps'),
            'forward_pe': info.get('forwardPE'),
            'enterprise_value': info.get('enterpriseValue'),
            'ebitda': info.get('ebitda'),
            'book_value': info.get('bookValue'),
            'revenue': info.get('totalRevenue'),
            'sector': info.get('sector', 'Other'),
            'industry': info.get('industry', 'Other'),
            # Growth / profitability fields (available for future use and for
            # the Individual Analysis screen; the breakout screener does not filter on them)
            'earnings_growth': info.get('earningsGrowth') or info.get('earningsQuarterlyGrowth'),
            'revenue_growth': info.get('revenueGrowth'),
            'operating_margin': info.get('operatingMargins'),
            'return_on_assets': info.get('returnOnAssets'),
            'current_ratio': info.get('currentRatio'),
            'free_cashflow': info.get('freeCashflow')
        }
        
        # Calculate additional metrics
        if fundamentals['price'] and fundamentals['52w_high']:
            fundamentals['pct_from_high'] = ((fundamentals['price'] - fundamentals['52w_high']) / fundamentals['52w_high']) * 100
        
        if fundamentals['price'] and fundamentals['52w_low']:
            fundamentals['pct_from_low'] = ((fundamentals['price'] - fundamentals['52w_low']) / fundamentals['52w_low']) * 100
        
        # Determine market cap category for Indian market (in INR)
        if market_cap:
            if market_cap >= 200000000000:  # ≥₹20,000 Cr
                fundamentals['cap_type'] = 'Large'
            elif market_cap >= 50000000000:  # ₹5,000-20,000 Cr
                fundamentals['cap_type'] = 'Mid'
            else:  # <₹5,000 Cr
                fundamentals['cap_type'] = 'Small'
        else:
            fundamentals['cap_type'] = 'Unknown'
        
        return fundamentals
    
    except Exception as e:
        return None

def get_industry_benchmarks(industry, cap_type='Large'):
    """Get industry-specific benchmarks with cap-size adjustments"""
    # Get industry-specific benchmarks first
    if industry in INDUSTRY_BENCHMARKS:
        base_benchmarks = INDUSTRY_BENCHMARKS[industry].copy()
    else:
        # Fallback to sector benchmarks
        sector = get_sector_for_industry(industry)
        base_benchmarks = SECTOR_BENCHMARKS.get(sector, SECTOR_BENCHMARKS['Other']).copy()
    
    # Apply cap-size multipliers
    if cap_type in CAP_SIZE_MULTIPLIERS:
        multipliers = CAP_SIZE_MULTIPLIERS[cap_type]
        base_benchmarks['pe'] *= multipliers['pe']
        base_benchmarks['pb'] *= multipliers['pb'] 
        base_benchmarks['ev_ebitda'] *= multipliers['ev_ebitda']
    
    # ---- Peer-average P/E override -----------------------------------------
    # When enabled, the industry P/E becomes the mean trailing P/E of the
    # stocks actually in this industry, with missing P/Es excluded rather than
    # counted as zero. Applied AFTER the cap multipliers and deliberately not
    # scaled by them: a measured peer average already embodies the size mix of
    # the industry, so multiplying again would double-count it.
    try:
        if st.session_state.get('use_peer_pe'):
            peer = compute_peer_industry_pe(
                industry,
                max_sample=int(st.session_state.get('peer_pe_sample', 60)),
                pe_cap=float(st.session_state.get('peer_pe_cap', 200.0))
            )
            min_n = int(st.session_state.get('peer_pe_min_n', 3))
            if peer and peer.get('n', 0) >= min_n and peer.get('mean'):
                base_benchmarks['pe'] = peer['mean']
                base_benchmarks['pe_source'] = 'peer'
                base_benchmarks['peer_n'] = peer['n']
    except Exception:
        pass
    
    return base_benchmarks

def calculate_fair_value(fundamentals, industry, cap_type='Large'):
    """Calculate fair value using enhanced industry-specific benchmarks"""
    if not fundamentals or not fundamentals.get('price'):
        return None
    
    try:
        # Get industry-specific benchmarks with cap-size adjustments
        benchmarks = get_industry_benchmarks(industry, cap_type)
        fair_values = []
        
        # PE-based fair value
        if fundamentals.get('trailing_pe') and fundamentals.get('trailing_eps'):
            if 0 < fundamentals['trailing_pe'] < 100:  # Sanity check
                # Use blended approach: 70% industry benchmark, 30% historical
                target_pe = (0.7 * benchmarks['pe']) + (0.3 * fundamentals['trailing_pe'])
                pe_fair_value = fundamentals['trailing_eps'] * target_pe
                if pe_fair_value > 0:
                    fair_values.append(pe_fair_value)
        
        # PB-based fair value (for asset-heavy industries)
        if fundamentals.get('book_value') and benchmarks.get('pb'):
            if fundamentals['book_value'] > 0:
                pb_fair_value = fundamentals['book_value'] * benchmarks['pb']
                if pb_fair_value > 0:
                    fair_values.append(pb_fair_value)
        
        # For high-growth industries, give more weight to forward-looking metrics
        if industry in ['Information Technology Services', 'Drug Manufacturers - Major', 'Renewable Energy']:
            if fundamentals.get('forward_pe') and fundamentals.get('trailing_eps'):
                if 0 < fundamentals['forward_pe'] < 50:
                    forward_fair_value = fundamentals['trailing_eps'] * fundamentals['forward_pe'] * 1.1
                    if forward_fair_value > 0:
                        fair_values.append(forward_fair_value)
        
        # Return weighted average if we have multiple estimates
        if len(fair_values) >= 2:
            # Weight PE more heavily for most industries
            if len(fair_values) == 2:
                return (fair_values[0] * 0.7 + fair_values[1] * 0.3)
            else:
                return np.mean(fair_values)
        elif fair_values:
            return fair_values[0]
        else:
            return None
            
    except:
        return None

def calculate_valuations(info, industry=None):
    """Advanced valuation calculations using industry-specific benchmarks"""
    try:
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        book_value = info.get('bookValue', 0)
        revenue = info.get('totalRevenue', 0)
        
        # Determine market cap category
        if market_cap >= 200000000000:  # ≥₹20,000 Cr
            cap_type = 'Large'
        elif market_cap >= 50000000000:  # ₹5,000-20,000 Cr
            cap_type = 'Mid'
        else:  # <₹5,000 Cr
            cap_type = 'Small'
        
        # Get industry-specific benchmarks
        if industry:
            benchmarks = get_industry_benchmarks(industry, cap_type)
        else:
            # Fallback to yfinance sector mapping
            sector = info.get('sector', 'Other')
            sector_mapping = {
                'Technology': 'Information Technology Services',
                'Financial Services': 'Money Center Banks', 
                'Healthcare': 'Drug Manufacturers - Major',
                'Industrials': 'Diversified Machinery',
                'Energy': 'Oil & Gas Operations',
                'Consumer Cyclical': 'Auto Manufacturers - Major',
                'Consumer Defensive': 'Food - Major Diversified',
                'Basic Materials': 'Steel & Iron',
                'Communication Services': 'Wireless Communications',
                'Real Estate': 'Real Estate Development',
                'Utilities': 'Electric Utilities'
            }
            mapped_industry = sector_mapping.get(sector, 'Other')
            benchmarks = get_industry_benchmarks(mapped_industry, cap_type)
        
        industry_pe = benchmarks['pe']
        industry_ev_ebitda = benchmarks['ev_ebitda']
        
        # Enhanced PE-based valuation
        historical_pe = trailing_pe if trailing_pe and 0 < trailing_pe < 100 else industry_pe
        # Blend industry benchmark with historical PE (weighted by cap size)
        pe_weight = 0.8 if cap_type == 'Large' else 0.7 if cap_type == 'Mid' else 0.6
        blended_pe = (industry_pe * pe_weight) + (historical_pe * (1 - pe_weight))
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # Enhanced EV/EBITDA-based valuation
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        
        if current_ev_ebitda and 0 < current_ev_ebitda < 50:
            # Blend current and industry EV/EBITDA
            ev_weight = 0.7 if cap_type == 'Large' else 0.6 if cap_type == 'Mid' else 0.5
            target_ev_ebitda = (industry_ev_ebitda * ev_weight) + (current_ev_ebitda * (1 - ev_weight))
        else:
            target_ev_ebitda = industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Additional ratios
        pb_ratio = price / book_value if book_value and book_value > 0 else None
        ps_ratio = market_cap / revenue if revenue and revenue > 0 else None
        
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,
            'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,
            'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev,
            'pb_ratio': pb_ratio, 'ps_ratio': ps_ratio,
            'book_value': book_value, 'revenue': revenue,
            'net_debt': (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'roe': info.get('returnOnEquity', 0),
            'profit_margin': info.get('profitMargins', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
            'cap_type': cap_type,
            'benchmarks_used': benchmarks
        }
    except:
        return None

# ============================================================================
# SCREENING LOGIC
# ============================================================================
def run_industry_screener(industry, strategy_type="undervalued", max_results=50):
    """Run comprehensive screening for a specific industry using enhanced benchmarks"""
    
    stocks = get_stocks_by_category(industry)
    if not stocks:
        return pd.DataFrame()
    
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_stocks = len(stocks)
    
    for i, (ticker, name) in enumerate(stocks.items()):
        # Update progress
        progress = (i + 1) / total_stocks
        progress_bar.progress(progress)
        status_text.text(f"Processing {ticker} ({i + 1}/{total_stocks})")
        
        # Get fundamentals
        fundamentals = get_stock_fundamentals(ticker)
        if not fundamentals or not fundamentals['price']:
            continue
        
        # Calculate fair value using industry-specific benchmarks
        fair_value = calculate_fair_value(fundamentals, industry, fundamentals.get('cap_type', 'Large'))
        if not fair_value or fair_value <= 0:
            continue
        
        # Calculate upside
        upside = ((fair_value - fundamentals['price']) / fundamentals['price']) * 100
        
        # Remove outliers: Skip stocks with upside > 500% (likely data errors)
        if upside > 350:
            continue
        
        # Get industry benchmarks for additional filtering
        benchmarks = get_industry_benchmarks(industry, fundamentals.get('cap_type', 'Large'))
        
        # Apply strategy filters with enhanced criteria
        passes_filter = False
        
        if strategy_type == "undervalued":
            # Basic undervalued filter
            if upside >= 15:  # At least 15% upside
                passes_filter = True
        
        elif strategy_type == "undervalued_near_high":
            # Undervalued stocks trading near 52-week highs (strong momentum + value)
            if upside >= 15:  # Must be undervalued
                pct_from_high = fundamentals.get('pct_from_high', -100)
                # Near 52-week high: within 5% of high
                if pct_from_high >= -5:
                    passes_filter = True
        
        elif strategy_type == "undervalued_supertrend":
            # Undervalued + Real SuperTrend bullish signal
            if upside >= 15:  # Must be undervalued
                # Get technical signals
                with st.spinner(f"Analyzing technical signals for {ticker}..."):
                    technical = get_technical_signals(ticker)
                
                if technical:
                    # SuperTrend bullish (1) and additional confirmations
                    if (technical['supertrend_signal'] == 1 and
                        technical['above_sma20'] and 
                        technical.get('price_vs_52w_high', 0) > 0.7):  # Not in deep correction
                        passes_filter = True
        
        elif strategy_type == "undervalued_rsi_macd":
            # Undervalued + momentum indicators (proxy using price action)
            if (upside >= 15 and
                fundamentals.get('pct_from_high', -100) >= -30 and
                fundamentals.get('volume', 0) > 0):  # Has volume
                passes_filter = True
        
        elif strategy_type == "momentum":
            # Momentum: stocks near 52W high with reasonable valuation
            if (fundamentals.get('pct_from_high', -100) >= -10 and
                fundamentals.get('trailing_pe', 999) <= benchmarks['pe'] * 1.5):
                passes_filter = True
        
        elif strategy_type == "quality":
            # Quality: good fundamentals with reasonable valuation
            roe_threshold = benchmarks.get('roe', 15) / 100
            if (fundamentals.get('roe', 0) > roe_threshold and
                fundamentals.get('trailing_pe', 999) <= benchmarks['pe'] * 1.2 and
                upside >= 5 and
                fundamentals.get('debt_to_equity', 999) <= benchmarks.get('debt_equity', 1.0)):
                passes_filter = True
        
        if not passes_filter:
            continue
        
        # Add to results
        result = {
            'Ticker': ticker,
            'Name': name,
            'Industry': industry,
            'Price': fundamentals['price'],
            'Fair Value': fair_value,
            'Upside %': upside,
            'PE Ratio': fundamentals['trailing_pe'],
            'PB Ratio': fundamentals['pb_ratio'],
            'ROE %': fundamentals['roe'] * 100 if fundamentals['roe'] else None,
            'Market Cap': fundamentals['market_cap'],
            'Cap Type': fundamentals['cap_type'],
            'From 52W High %': fundamentals['pct_from_high'],
            'From 52W Low %': fundamentals['pct_from_low'],
            'Beta': fundamentals['beta'],
            'Dividend Yield %': fundamentals['dividend_yield'] * 100 if fundamentals['dividend_yield'] else None,
            'Volume': fundamentals.get('volume'),
            'Avg Volume': fundamentals.get('avg_volume'),
            'Rel Vol': (fundamentals.get('volume') / fundamentals.get('avg_volume'))
                       if (fundamentals.get('volume') and fundamentals.get('avg_volume')) else None,
            'Industry PE Benchmark': benchmarks['pe'],
            'Industry EV/EBITDA Benchmark': benchmarks['ev_ebitda'],
            'Valuation': build_valuation_link(ticker)
        }
        results.append(result)
        
        if len(results) >= max_results:
            break
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

def search_stocks_by_name(query, max_results=50):
    """Search stocks by company name across all industries"""
    results = []
    query_lower = query.lower()
    
    for industry, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query_lower in name.lower() or query_lower in ticker.lower():
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'industry': industry
                })
                if len(results) >= max_results:
                    break
        if len(results) >= max_results:
            break
    
    return results

# ============================================================================
# EARNINGS + VALUE SCREENER
# ----------------------------------------------------------------------------
# DESIGN NOTES
#
# Exactly three criteria, and no technical/momentum model at all:
#
#   1. Price is near its 52-week high
#   2. Price is below the fair value estimate
#   3. Earnings fall inside a chosen calendar window
#
# The stages run cheapest-first. Stage 1 works from batched daily bars and
# typically removes most of a universe for the cost of a few requests. Only
# the survivors reach the per-ticker calls in stages 2 and 3, both of which
# are cached (fair value 1h, earnings dates 1h).
#
# The two earnings windows are OPPOSITE trades and the UI says so. "Reported
# in the last N days" is post-earnings drift: the event is behind you and the
# surprise is known. "Due in the next N days" means holding through a binary
# event, where a gap passes straight through a stop.
# ============================================================================

def _ns(symbols):
    """Helper to append NSE suffix to a list of raw symbols"""
    return [s if s.endswith((".NS", ".BO")) else f"{s}.NS" for s in symbols]


# Preset liquid universes for fast intraday scanning (yfinance rate-limit friendly)
BREAKOUT_PRESET_UNIVERSES = {
    "NIFTY 50 (Most Liquid)": _ns([
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR", "ITC", "SBIN",
        "BHARTIARTL", "KOTAKBANK", "LT", "BAJFINANCE", "AXISBANK", "ASIANPAINT", "MARUTI",
        "HCLTECH", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "WIPRO", "ONGC", "NTPC",
        "POWERGRID", "M&M", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "ADANIENT", "ADANIPORTS",
        "COALINDIA", "GRASIM", "HINDALCO", "DRREDDY", "CIPLA", "APOLLOHOSP", "BAJAJFINSV",
        "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "BRITANNIA", "TATACONSUM", "INDUSINDBK",
        "SBILIFE", "HDFCLIFE", "TECHM", "LTIM", "SHRIRAMFIN", "BPCL", "TRENT"
    ]),
    "NIFTY NEXT 50 / Midcap Liquid": _ns([
        "DMART", "PIDILITIND", "GODREJCP", "DABUR", "HAVELLS", "SIEMENS", "ABB", "BOSCHLTD",
        "AMBUJACEM", "ACC", "VEDL", "DLF", "ICICIPRULI", "ICICIGI", "CHOLAFIN", "TVSMOTOR",
        "IOC", "GAIL", "PFC", "RECLTD", "HAL", "BEL", "IRCTC", "INDIGO", "NAUKRI",
        "MOTHERSON", "MARICO", "COLPAL", "BERGEPAINT", "TORNTPHARM", "LUPIN", "AUROPHARMA",
        "ZYDUSLIFE", "ALKEM", "MPHASIS", "PERSISTENT", "COFORGE", "POLYCAB", "ASTRAL",
        "SRF", "PIIND", "UPL", "TATAPOWER", "JINDALSTEL", "SAIL", "NMDC", "CANBK", "PNB",
        "BANKBARODA", "IDFCFIRSTB", "AUBANK", "FEDERALBNK", "MUTHOOTFIN", "LICHSGFIN"
    ]),
    "High Beta / F&O Movers": _ns([
        "ADANIENT", "ADANIPORTS", "TATAMOTORS", "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL",
        "SAIL", "NMDC", "JINDALSTEL", "IDFCFIRSTB", "YESBANK", "PNB", "CANBK", "BANKBARODA",
        "RBLBANK", "BANDHANBNK", "IEX", "BSE", "ANGELONE", "PAYTM", "POLICYBZR", "NYKAA",
        "IRFC", "RVNL", "IRCON", "NBCC", "HUDCO", "SJVN", "NHPC", "PFC", "RECLTD",
        "TATAPOWER", "SUZLON", "IDEA", "ZEEL", "DELHIVERY", "MAZDOCK", "COCHINSHIP", "BDL"
    ]),
    "Banking & Financials": _ns([
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK", "BANKBARODA",
        "PNB", "CANBK", "FEDERALBNK", "IDFCFIRSTB", "AUBANK", "BAJFINANCE", "BAJAJFINSV",
        "CHOLAFIN", "SHRIRAMFIN", "MUTHOOTFIN", "LICHSGFIN", "PFC", "RECLTD", "SBILIFE",
        "HDFCLIFE", "ICICIPRULI", "ICICIGI", "IIFL", "MANAPPURAM", "PEL", "M&MFIN"
    ]),
    "IT & Tech": _ns([
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "MPHASIS", "PERSISTENT",
        "COFORGE", "LTTS", "OFSS", "KPITTECH", "TATAELXSI", "CYIENT", "SONATSOFTW",
        "BIRLASOFT", "ZENSARTECH", "NEWGEN", "HAPPSTMNDS", "INTELLECT"
    ]),
}


# ---------------------------------------------------------------------------
# Indicator helpers
# ---------------------------------------------------------------------------
def format_volume(v):
    """Format volume in Indian convention (K / L / Cr)"""
    try:
        if v is None or pd.isna(v) or v <= 0:
            return "N/A"
        v = float(v)
        if v >= 1e7:
            return f"{v/1e7:.2f} Cr"
        if v >= 1e5:
            return f"{v/1e5:.2f} L"
        if v >= 1e3:
            return f"{v/1e3:.1f} K"
        return f"{v:,.0f}"
    except Exception:
        return "N/A"


# ---------------------------------------------------------------------------
# Batch data fetching
# ---------------------------------------------------------------------------
def _batch_download(tickers_tuple, interval, period):
    """Shared batch downloader returning {ticker: DataFrame}"""
    tickers = list(tickers_tuple)
    out = {}
    if not tickers:
        return out
    try:
        data = yf.download(
            tickers=" ".join(tickers),
            period=period,
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False,
            prepost=False
        )
    except Exception:
        return out

    if data is None or len(data) == 0:
        return out

    try:
        if isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                try:
                    sub = data[t].dropna(how="all")
                    if not sub.empty and len(sub) > 5:
                        out[t] = sub
                except Exception:
                    continue
        else:
            if len(tickers) == 1:
                sub = data.dropna(how="all")
                if not sub.empty:
                    out[tickers[0]] = sub
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------
# EARNINGS CALENDAR + VALUE + 52-WEEK HIGH ENGINE
# ---------------------------------------------------------------------------
# Three criteria only:
#
#   1. Price is approaching its 52-week high
#   2. Price is below fair value (undervalued)
#   3. Earnings fall inside a chosen window - either due in the next N days,
#      or already reported in the last N days
#
# No breakout structure, no momentum indicators, no timeframe scanning.
# ---------------------------------------------------------------------------

EARNINGS_MODES = {
    "Reported in last N days (post-earnings drift)": "reported",
    "Due in next N days (pre-earnings run-up)": "upcoming",
    "Either side of earnings": "either",
    "No earnings filter": "off",
}


@st.cache_data(ttl=900, show_spinner=False)
def fetch_daily_history_batch(tickers_tuple, period="1y"):
    """Daily OHLCV for the 52-week high calculation. Cached 15 minutes."""
    return _batch_download(tickers_tuple, "1d", period)


# ---------------------------------------------------------------------------
# PEER-AVERAGE INDUSTRY P/E
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def compute_peer_industry_pe(industry, max_sample=60, pe_cap=200.0):
    """
    Mean trailing P/E of the stocks actually in this industry.

    Stocks with no P/E are excluded, not treated as zero. A missing P/E on
    Yahoo almost always means negative or nil earnings, and averaging those
    in as zeros would drag every fair value down.

    Also excluded: non-positive P/E (loss-making, where the ratio carries no
    valuation meaning) and anything above `pe_cap`, since one 900x outlier
    moves the mean of a 20-stock industry by 45 points on its own.
    """
    result = {'mean': None, 'median': None, 'n': 0, 'excluded_missing': 0,
              'excluded_negative': 0, 'excluded_outlier': 0, 'values': [],
              'sample_size': 0}
    try:
        stocks = get_stocks_by_category(industry)
        if not stocks:
            return result

        tickers = list(stocks.keys())[:max_sample]
        result['sample_size'] = len(tickers)
        values = []

        for ticker in tickers:
            try:
                f = get_stock_fundamentals(ticker)
            except Exception:
                f = None
            if not f:
                result['excluded_missing'] += 1
                continue
            pe = f.get('trailing_pe')
            if pe is None or (isinstance(pe, float) and pd.isna(pe)):
                result['excluded_missing'] += 1
                continue
            pe = float(pe)
            if pe <= 0:
                result['excluded_negative'] += 1
                continue
            if pe > pe_cap:
                result['excluded_outlier'] += 1
                continue
            values.append(pe)

        if values:
            result['values'] = sorted(values)
            result['n'] = len(values)
            result['mean'] = float(np.mean(values))
            result['median'] = float(np.median(values))
    except Exception:
        pass
    return result


# ---------------------------------------------------------------------------
# EARNINGS DATES - MULTI-SOURCE FALLBACK CHAIN
# ---------------------------------------------------------------------------
# Yahoo has no earnings dates for large parts of the NSE mid and small cap
# universe. Each source below is tried in turn and the winner is recorded in
# the 'source' field so you can see how a date was obtained.
# ---------------------------------------------------------------------------

# SEBI LODR Regulation 33: quarterly results must be filed within 45 days of
# the quarter end (60 days for the final quarter of the financial year).
SEBI_FILING_LAG_DAYS = 45
SEBI_Q4_FILING_LAG_DAYS = 60


def _earnings_from_info(ticker):
    """Source 3: the earnings timestamps buried in the already-cached info dict."""
    try:
        info, err = fetch_stock_data(ticker)
        if err or not info:
            return None, None
        nxt = last = None
        for key in ('earningsTimestamp', 'earningsTimestampStart', 'earningsTimestampEnd'):
            ts = info.get(key)
            if not ts:
                continue
            try:
                d = pd.Timestamp(int(ts), unit='s')
            except Exception:
                continue
            now = pd.Timestamp.now()
            if d > now:
                nxt = d if nxt is None or d < nxt else nxt
            else:
                last = d if last is None or d > last else last
        return nxt, last
    except Exception:
        return None, None


def _earnings_from_quarter_end(ticker):
    """
    Source 4: infer the announcement from the most recent reported quarter.

    Yahoo exposes the quarter END date even when it has no announcement date.
    Adding the statutory filing lag gives an approximation - clearly flagged as
    estimated, never presented as a confirmed date.
    """
    try:
        info, err = fetch_stock_data(ticker)
        q_end = None
        if not err and info:
            ts = info.get('mostRecentQuarter')
            if ts:
                try:
                    q_end = pd.Timestamp(int(ts), unit='s')
                except Exception:
                    q_end = None

        if q_end is None:
            tk = yf.Ticker(ticker)
            for attr in ('quarterly_income_stmt', 'quarterly_financials'):
                try:
                    qdf = getattr(tk, attr)
                    if qdf is not None and not qdf.empty:
                        cols = [pd.Timestamp(c) for c in qdf.columns]
                        q_end = max(cols)
                        break
                except Exception:
                    continue

        if q_end is None:
            return None, None, None

        # Q4 (financial year ending March in India) gets the longer window
        lag = SEBI_Q4_FILING_LAG_DAYS if q_end.month == 3 else SEBI_FILING_LAG_DAYS
        deadline = q_end + pd.Timedelta(days=lag)
        now = pd.Timestamp.now()

        # The filing deadline for the most recent quarter end may not have
        # arrived yet. In that case it is the NEXT expected announcement, and
        # the last one belongs to the quarter before it - otherwise a stock
        # reports a "last earnings" date that has not happened.
        if deadline > now:
            est_next = deadline
            prev_q_end = q_end - pd.Timedelta(days=91)
            prev_lag = SEBI_Q4_FILING_LAG_DAYS if prev_q_end.month == 3 else SEBI_FILING_LAG_DAYS
            est_last = prev_q_end + pd.Timedelta(days=prev_lag)
            if est_last > now:
                est_last = None
        else:
            est_last = deadline
            next_q_end = q_end + pd.Timedelta(days=91)
            next_lag = SEBI_Q4_FILING_LAG_DAYS if next_q_end.month == 3 else SEBI_FILING_LAG_DAYS
            est_next = next_q_end + pd.Timedelta(days=next_lag)

        return est_next, est_last, q_end
    except Exception:
        return None, None, None


@st.cache_data(ttl=21600, show_spinner=False)
def _earnings_from_nse(symbol):
    """
    Source 5: NSE India board-meeting calendar. OFF by default.

    NSE requires a cookie handshake and blocks most datacentre IP ranges, so
    this frequently fails from Streamlit Cloud and other hosted environments.
    It is opt-in for that reason, and every failure is silent.
    """
    try:
        import requests
    except Exception:
        return None, None

    base = "https://www.nseindia.com"
    headers = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{base}/get-quotes/equity?symbol={symbol}",
    }
    try:
        sess = requests.Session()
        sess.headers.update(headers)
        sess.get(base, timeout=6)                      # cookie handshake
        sess.get(f"{base}/get-quotes/equity?symbol={symbol}", timeout=6)

        for url in (f"{base}/api/top-corp-info?symbol={symbol}&market=equities",
                    f"{base}/api/quote-equity?symbol={symbol}&section=corp_info"):
            try:
                r = sess.get(url, timeout=8)
                if r.status_code != 200:
                    continue
                payload = r.json()
            except Exception:
                continue

            meetings = []
            def walk(node):
                if isinstance(node, dict):
                    if any(k in node for k in ('meetingdate', 'bm_date', 'meetingDate')):
                        meetings.append(node)
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(payload)

            dates = []
            for m in meetings:
                purpose = " ".join(str(v) for v in m.values()).lower()
                if 'result' not in purpose and 'financial' not in purpose:
                    continue
                raw = m.get('meetingdate') or m.get('bm_date') or m.get('meetingDate')
                if not raw:
                    continue
                for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d-%m-%Y", "%d %b %Y"):
                    try:
                        dates.append(pd.Timestamp(datetime.strptime(str(raw).strip(), fmt)))
                        break
                    except Exception:
                        continue

            if dates:
                now = pd.Timestamp.now()
                future = [d for d in dates if d > now]
                past = [d for d in dates if d <= now]
                return (min(future) if future else None), (max(past) if past else None)
    except Exception:
        pass
    return None, None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_earnings_calendar(ticker, allow_nse=False, allow_estimate=True):
    """
    Next and most recent earnings dates, trying every available source.

    Source order, best first:
      1. Yahoo earnings_dates    - confirmed announcement dates
      2. Yahoo calendar          - confirmed next date
      3. Yahoo info timestamps   - free, already cached with the info dict
      4. NSE board meetings      - opt-in, often blocked from cloud hosts
      5. Quarter-end + SEBI lag  - ESTIMATE, flagged as such
    """
    out = {'next_date': None, 'days_to_next': None, 'last_date': None,
           'days_since_last': None, 'surprise_pct': None,
           'source': 'None', 'estimated': False}

    # ---- 1. Yahoo earnings_dates ----
    try:
        tk = yf.Ticker(ticker)
        try:
            df = tk.get_earnings_dates(limit=16)
        except Exception:
            df = None

        if df is not None and not df.empty:
            idx = pd.to_datetime(df.index)
            tz = getattr(idx, 'tz', None)
            now = pd.Timestamp.now(tz=tz) if tz is not None else pd.Timestamp.now()

            surprise_col = next((c for c in df.columns if 'surprise' in str(c).lower()), None)
            reported_col = next((c for c in df.columns if 'reported' in str(c).lower()), None)

            future = [d for d in idx if d > now]
            past = [d for d in idx if d <= now]

            if future:
                nxt = min(future)
                out['next_date'] = nxt
                out['days_to_next'] = int((nxt - now).days)
            if past:
                last = max(past)
                if reported_col is not None and reported_col in df.columns:
                    reported = [d for d in past if pd.notna(df.loc[d, reported_col])]
                    if reported:
                        last = max(reported)
                out['last_date'] = last
                out['days_since_last'] = int((now - last).days)
                if surprise_col is not None and surprise_col in df.columns:
                    val = df.loc[last, surprise_col]
                    if pd.notna(val):
                        out['surprise_pct'] = float(val)
            if out['next_date'] is not None or out['last_date'] is not None:
                out['source'] = 'Yahoo earnings'
    except Exception:
        pass

    # ---- 2. Yahoo calendar (next date only) ----
    if out['next_date'] is None:
        try:
            cal = yf.Ticker(ticker).calendar
            dates = None
            if isinstance(cal, dict):
                dates = cal.get('Earnings Date')
            elif cal is not None and hasattr(cal, 'index') and 'Earnings Date' in cal.index:
                dates = cal.loc['Earnings Date'].tolist()
            if dates:
                if not isinstance(dates, (list, tuple)):
                    dates = [dates]
                nxt = pd.Timestamp(min(dates))
                now = pd.Timestamp.now()
                if nxt > now:
                    out['next_date'] = nxt
                    out['days_to_next'] = int((nxt - now).days)
                    if out['source'] == 'None':
                        out['source'] = 'Yahoo calendar'
        except Exception:
            pass

    # ---- 3. Yahoo info timestamps ----
    if out['next_date'] is None or out['last_date'] is None:
        nxt, last = _earnings_from_info(ticker)
        now = pd.Timestamp.now()
        if out['next_date'] is None and nxt is not None:
            out['next_date'] = nxt
            out['days_to_next'] = int((nxt - now).days)
            if out['source'] == 'None':
                out['source'] = 'Yahoo info'
        if out['last_date'] is None and last is not None:
            out['last_date'] = last
            out['days_since_last'] = int((now - last).days)
            if out['source'] == 'None':
                out['source'] = 'Yahoo info'

    # ---- 4. NSE board meetings (opt-in) ----
    if allow_nse and (out['next_date'] is None or out['last_date'] is None):
        sym = ticker.replace('.NS', '').replace('.BO', '')
        nxt, last = _earnings_from_nse(sym)
        now = pd.Timestamp.now()
        if out['next_date'] is None and nxt is not None:
            out['next_date'] = nxt
            out['days_to_next'] = int((nxt - now).days)
            out['source'] = 'NSE'
        if out['last_date'] is None and last is not None:
            out['last_date'] = last
            out['days_since_last'] = int((now - last).days)
            if out['source'] in ('None',):
                out['source'] = 'NSE'

    # ---- 5. Quarter end + statutory filing lag (ESTIMATE) ----
    if allow_estimate and (out['next_date'] is None or out['last_date'] is None):
        est_next, est_last, q_end = _earnings_from_quarter_end(ticker)
        now = pd.Timestamp.now()
        if out['last_date'] is None and est_last is not None:
            out['last_date'] = est_last
            out['days_since_last'] = int((now - est_last).days)
            out['estimated'] = True
            out['source'] = f"≈ Q-end {q_end.strftime('%b-%Y')}" if q_end is not None else "≈ Estimated"
        if out['next_date'] is None and est_next is not None and est_next > now:
            out['next_date'] = est_next
            out['days_to_next'] = int((est_next - now).days)
            out['estimated'] = True
            if out['source'] == 'None':
                out['source'] = "≈ Estimated"

    return out


# ---------------------------------------------------------------------------
# MANUAL FAIR VALUE CALCULATOR
# ---------------------------------------------------------------------------
def render_manual_fair_value(results_key, key_prefix="mfv"):
    """
    Override the model's fair value for any row in the results table.

    The model blends a P/E and a P/B estimate off industry benchmarks. When
    those inputs are stale or distorted - a trailing EPS from a bad quarter,
    a book value that has since been written down - this lets you substitute
    your own numbers and push the result straight back into the table.
    """
    df = st.session_state.get(results_key)
    if df is None or getattr(df, 'empty', True) or 'Ticker' not in df.columns:
        return

    with st.expander("🧮 Manual Fair Value Calculator"):
        options = [f"{r['Ticker']} — {r.get('Name', '')}" for _, r in df.iterrows()]
        picked = st.selectbox("Stock", options, key=f"{key_prefix}_pick")
        ticker = picked.split(" — ")[0].strip()

        row = df[df['Ticker'] == ticker]
        if row.empty:
            return
        row = row.iloc[0]

        fundamentals = None
        try:
            fundamentals = get_stock_fundamentals(ticker)
        except Exception:
            pass

        ltp = float(row['LTP']) if pd.notna(row.get('LTP')) else 0.0
        eps_default = float(fundamentals.get('trailing_eps') or 0.0) if fundamentals else 0.0
        bv_default = float(fundamentals.get('book_value') or 0.0) if fundamentals else 0.0
        pe_default = float(fundamentals.get('trailing_pe') or 0.0) if fundamentals else 0.0

        industry = None
        try:
            si = get_stock_info(ticker)
            industry = si['category'] if si else (fundamentals.get('industry') if fundamentals else None)
        except Exception:
            pass
        bench = {}
        try:
            bench = get_industry_benchmarks(industry or 'Other',
                                            (fundamentals or {}).get('cap_type', 'Large'))
        except Exception:
            bench = {}

        st.caption(f"**{ticker}** · LTP ₹{ltp:,.2f} · Industry: {industry or 'Unknown'} · "
                   f"Current P/E {pe_default:,.2f} · Model fair value "
                   f"{'₹{:,.2f}'.format(row['Fair Value']) if pd.notna(row.get('Fair Value')) else 'N/A'}")

        c1, c2, c3 = st.columns(3)
        with c1:
            eps = st.number_input("EPS (₹)", value=float(round(eps_default, 2)),
                                  step=0.5, format="%.2f", key=f"{key_prefix}_eps")
            target_pe = st.number_input("Target P/E", value=float(round(bench.get('pe', 18.0), 2)),
                                        min_value=0.0, step=0.5, format="%.2f",
                                        key=f"{key_prefix}_pe")
        with c2:
            bv = st.number_input("Book Value / share (₹)", value=float(round(bv_default, 2)),
                                 step=1.0, format="%.2f", key=f"{key_prefix}_bv")
            target_pb = st.number_input("Target P/B", value=float(round(bench.get('pb', 2.5), 2)),
                                        min_value=0.0, step=0.1, format="%.2f",
                                        key=f"{key_prefix}_pb")
        with c3:
            pe_weight = st.slider("Weight on P/E method", 0, 100, 70, 5,
                                  key=f"{key_prefix}_w") / 100.0
            margin = st.slider("Margin of safety %", 0, 50, 0, 5,
                               key=f"{key_prefix}_mos",
                               help="Discounts the computed fair value before "
                                    "the upside is calculated.")

        pe_fv = eps * target_pe if eps and target_pe else None
        pb_fv = bv * target_pb if bv and target_pb else None

        if pe_fv is not None and pb_fv is not None:
            fv = pe_weight * pe_fv + (1 - pe_weight) * pb_fv
        else:
            fv = pe_fv if pe_fv is not None else pb_fv

        if fv is not None and fv > 0:
            fv = fv * (1 - margin / 100.0)
            upside = ((fv - ltp) / ltp * 100) if ltp else None

            r1, r2, r3 = st.columns(3)
            r1.metric("P/E fair value", f"₹{pe_fv:,.2f}" if pe_fv else "N/A")
            r2.metric("P/B fair value", f"₹{pb_fv:,.2f}" if pb_fv else "N/A")
            r3.metric("Blended fair value", f"₹{fv:,.2f}",
                      delta=f"{upside:+.1f}% vs LTP" if upside is not None else None)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ Apply to results table", key=f"{key_prefix}_apply",
                             use_container_width=True, type="primary"):
                    d = st.session_state[results_key].copy()
                    mask = d['Ticker'] == ticker
                    d.loc[mask, 'Fair Value'] = fv
                    d.loc[mask, 'Upside %'] = upside
                    d.loc[mask, 'Value Tag'] = get_valuation_tag(upside)
                    if 'FV Source' in d.columns:
                        d.loc[mask, 'FV Source'] = '🧮 Manual'
                    st.session_state[results_key] = d
                    st.rerun()
            with b2:
                if st.button("↩️ Revert this row to model", key=f"{key_prefix}_revert",
                             use_container_width=True):
                    d = st.session_state[results_key].copy()
                    mask = d['Ticker'] == ticker
                    try:
                        f2 = get_stock_fundamentals(ticker)
                        fv2 = calculate_fair_value(f2, industry or 'Other',
                                                   f2.get('cap_type', 'Large'))
                        up2 = ((fv2 - f2['price']) / f2['price'] * 100) if fv2 else None
                        d.loc[mask, 'Fair Value'] = fv2
                        d.loc[mask, 'Upside %'] = up2
                        d.loc[mask, 'Value Tag'] = get_valuation_tag(up2)
                        if 'FV Source' in d.columns:
                            d.loc[mask, 'FV Source'] = 'Model'
                        st.session_state[results_key] = d
                        st.rerun()
                    except Exception:
                        st.warning("Could not recompute the model value for this stock.")
        else:
            st.info("Enter an EPS with a target P/E, or a book value with a target P/B.")


def compute_52w_features(df):
    """Price position against the 52-week high, plus volume context."""
    try:
        if df is None or len(df) < 60:
            return None
        d = df[['High', 'Low', 'Close', 'Volume']].dropna(subset=['Close'])
        if len(d) < 60:
            return None

        window = d.iloc[-252:] if len(d) >= 252 else d
        high_52w = float(window['High'].max())
        low_52w = float(window['Low'].min())
        price = float(d['Close'].iloc[-1])
        if high_52w <= 0 or price <= 0:
            return None

        volume = d['Volume'].fillna(0)
        last_vol = float(volume.iloc[-1])
        avg_vol = float(volume.rolling(20).mean().iloc[-1]) if len(volume) >= 20 else last_vol
        prev_close = float(d['Close'].iloc[-2]) if len(d) > 1 else price

        # Negative = below the high. -2.0 means 2% under the 52-week high.
        pct_from_high = (price - high_52w) / high_52w * 100

        return {
            'price': price,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'pct_from_high': pct_from_high,
            'pct_from_low': (price - low_52w) / low_52w * 100 if low_52w > 0 else None,
            'last_volume': last_vol,
            'avg_volume': avg_vol,
            'rel_volume': (last_vol / avg_vol) if avg_vol > 0 else 0.0,
            'chg_pct': (price - prev_close) / prev_close * 100 if prev_close else 0.0,
            'last_bar': d.index[-1],
        }
    except Exception:
        return None


def earnings_window_passes(cal, mode, upcoming_days, reported_days):
    """Apply the chosen earnings-window rule. Returns (passes, status_label)."""
    d_next = cal.get('days_to_next')
    d_last = cal.get('days_since_last')

    upcoming = d_next is not None and 0 <= d_next <= upcoming_days
    reported = d_last is not None and 0 <= d_last <= reported_days

    if mode == "off":
        # No window applies here, so report the real dates rather than
        # pretending a stock 45 days from earnings has no date at all.
        if d_next is not None and d_last is not None:
            return True, (f"🔜 In {d_next}d" if d_next <= d_last else f"✅ {d_last}d ago")
        if d_next is not None:
            return True, f"🔜 In {d_next}d"
        if d_last is not None:
            return True, f"✅ {d_last}d ago"
        return True, "— No date"

    if mode == "upcoming":
        return upcoming, (f"🔜 In {d_next}d" if upcoming else "")

    if mode == "reported":
        return reported, (f"✅ {d_last}d ago" if reported else "")

    # either
    if upcoming and reported:
        return True, f"🔁 {d_last}d ago → {d_next}d"
    if upcoming:
        return True, f"🔜 In {d_next}d"
    if reported:
        return True, f"✅ {d_last}d ago"
    return False, ""


def run_earnings_value_screener(universe, near_high_pct=5.0, min_upside=15.0,
                                earnings_mode="reported", upcoming_days=30,
                                reported_days=30, min_price=20.0,
                                min_avg_volume=50000, max_results=40,
                                max_valuation_calls=150, chunk_size=25,
                                final_rank="Upside %", allow_nse=False,
                                allow_estimate=True):
    """
    Three-stage funnel, ordered cheapest first.

      1. Daily bars, batched  - 52-week high proximity, price, liquidity
      2. Fair value           - per ticker, cached, only on stage-1 survivors
      3. Earnings calendar    - per ticker, cached, only on stage-2 survivors

    Stages 2 and 3 are per-ticker calls, so the ordering matters: stage 1
    typically removes 90% of a universe for the cost of a handful of requests.
    """
    tickers = list(universe.keys())
    total = len(tickers)
    funnel = {'scanned': 0, 'with_data': 0, 'near_high': 0,
              'undervalued': 0, 'earnings_ok': 0, 'final': 0}

    if total == 0:
        return pd.DataFrame(), funnel

    # ---------------- STAGE 1: 52-week high proximity ----------------
    stage1 = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    processed = 0

    for start in range(0, total, chunk_size):
        chunk = tickers[start:start + chunk_size]
        status_text.text(f"📈 Stage 1/3 — 52-week high scan... "
                         f"{processed}/{total} | near high: {len(stage1)}")
        data_map = fetch_daily_history_batch(tuple(chunk), "1y")

        for ticker in chunk:
            processed += 1
            funnel['scanned'] += 1
            try:
                progress_bar.progress(min(processed / total * 0.5, 0.5))
            except Exception:
                pass

            df = data_map.get(ticker)
            if df is None or df.empty:
                continue
            funnel['with_data'] += 1

            feat = compute_52w_features(df)
            if not feat:
                continue
            if feat['price'] < min_price or feat['avg_volume'] < min_avg_volume:
                continue
            # pct_from_high is negative below the high; -near_high_pct is the floor
            if feat['pct_from_high'] < -abs(near_high_pct):
                continue

            funnel['near_high'] += 1
            stage1.append({'ticker': ticker, 'feat': feat})

    # Closest to the high first, then cap the per-ticker work that follows
    stage1.sort(key=lambda c: c['feat']['pct_from_high'], reverse=True)
    stage1 = stage1[:max_valuation_calls]

    # ---------------- STAGE 2: valuation ----------------
    rows = []
    for n, c in enumerate(stage1):
        ticker, feat = c['ticker'], c['feat']
        try:
            progress_bar.progress(min(0.5 + (n + 1) / max(len(stage1), 1) * 0.3, 0.8))
            status_text.text(f"💰 Stage 2/3 — valuing... {n + 1}/{len(stage1)} — {ticker}")
        except Exception:
            pass

        fair_value = upside = pe_ratio = cap_type = market_cap = None
        try:
            fundamentals = get_stock_fundamentals(ticker)
            if fundamentals and fundamentals.get('price'):
                stock_info = get_stock_info(ticker)
                industry = stock_info['category'] if stock_info else fundamentals.get('industry', 'Other')
                cap_type = fundamentals.get('cap_type', 'Large')
                pe_ratio = fundamentals.get('trailing_pe')
                market_cap = fundamentals.get('market_cap')
                fv = calculate_fair_value(fundamentals, industry, cap_type)
                if fv and fv > 0:
                    ref = fundamentals['price']
                    up = ((fv - ref) / ref) * 100
                    if -95 <= up <= 350:
                        fair_value, upside = fv, up
        except Exception:
            pass

        if upside is None or upside < min_upside:
            continue
        funnel['undervalued'] += 1

        rows.append({
            'ticker': ticker, 'feat': feat, 'fair_value': fair_value,
            'upside': upside, 'pe_ratio': pe_ratio, 'cap_type': cap_type,
            'market_cap': market_cap
        })

    # ---------------- STAGE 3: earnings calendar ----------------
    final_rows = []
    for n, r in enumerate(rows):
        ticker, feat = r['ticker'], r['feat']
        try:
            progress_bar.progress(min(0.8 + (n + 1) / max(len(rows), 1) * 0.2, 1.0))
            status_text.text(f"📅 Stage 3/3 — earnings dates... {n + 1}/{len(rows)} — {ticker}")
        except Exception:
            pass

        cal = fetch_earnings_calendar(ticker, allow_nse=allow_nse,
                                      allow_estimate=allow_estimate)
        passes, status = earnings_window_passes(cal, earnings_mode,
                                                upcoming_days, reported_days)
        if not passes:
            continue
        funnel['earnings_ok'] += 1

        surprise = cal.get('surprise_pct')
        if surprise is None:
            surprise_tag = "—"
        elif surprise > 0:
            surprise_tag = f"🟢 Beat {surprise:+.1f}%"
        elif surprise < 0:
            surprise_tag = f"🔴 Miss {surprise:+.1f}%"
        else:
            surprise_tag = "⚪ In line"

        final_rows.append({
            'Ticker': ticker,
            'Name': universe.get(ticker, ticker),
            'LTP': feat['price'],
            'Chg %': feat['chg_pct'],
            '52W High': feat['high_52w'],
            'From High %': feat['pct_from_high'],
            'Fair Value': r['fair_value'],
            'Upside %': r['upside'],
            'Value Tag': get_valuation_tag(r['upside']),
            'FV Source': 'Model',
            'Earnings': status,
            'Date Source': cal.get('source', 'None'),
            'Estimated': bool(cal.get('estimated')),
            'Next Earnings': cal['next_date'].strftime('%d-%b-%Y') if cal.get('next_date') is not None else 'N/A',
            'Days To': cal.get('days_to_next'),
            'Last Earnings': cal['last_date'].strftime('%d-%b-%Y') if cal.get('last_date') is not None else 'N/A',
            'Days Since': cal.get('days_since_last'),
            'Last Surprise': surprise_tag,
            'Surprise %': surprise,
            'Volume': feat['last_volume'],
            'Avg Volume': feat['avg_volume'],
            'Rel Vol': feat['rel_volume'],
            'From Low %': feat['pct_from_low'],
            'PE Ratio': r['pe_ratio'],
            'Cap Type': r['cap_type'],
            'Market Cap': r['market_cap'],
            'As Of': feat['last_bar'].strftime('%d-%b-%Y') if hasattr(feat['last_bar'], 'strftime') else str(feat['last_bar']),
            'Valuation': build_valuation_link(ticker),
        })

    try:
        progress_bar.empty()
        status_text.empty()
    except Exception:
        pass

    if not final_rows:
        return pd.DataFrame(), funnel

    df_out = pd.DataFrame(final_rows)

    if final_rank == "Closest to 52W High":
        df_out = df_out.sort_values('From High %', ascending=False)
    elif final_rank == "Earnings Soonest":
        df_out = df_out.sort_values('Days To', ascending=True, na_position='last')
    elif final_rank == "Best Surprise":
        df_out = df_out.sort_values('Surprise %', ascending=False, na_position='last')
    else:
        df_out = df_out.sort_values('Upside %', ascending=False)

    df_out = df_out.head(max_results).reset_index(drop=True)
    funnel['final'] = len(df_out)
    return df_out, funnel


# ---------------------------------------------------------------------------
# Valuation enrichment (fair value + upside %)
# ---------------------------------------------------------------------------
def get_valuation_tag(upside):
    """Human readable valuation status from the upside percentage"""
    if upside is None or pd.isna(upside):
        return "❔ No Data"
    if upside > 25:
        return "🚀 Deep Value"
    if upside > 15:
        return "✅ Undervalued"
    if upside > 0:
        return "📥 Fairly Valued"
    if upside > -10:
        return "⏸️ Slightly Rich"
    return "⚠️ Overvalued"


def enrich_with_valuation(rows, show_progress=True):
    """
    Attach fair value and upside to breakout candidates.

    DISPLAY ONLY. Nothing here can remove a stock from the results - the
    screener is purely technical, and these columns exist so you can see what
    you are buying, not to veto a valid setup. Runs after the technical and
    trend gates, so the per-ticker calls only touch survivors, and
    fetch_stock_data() is cached for an hour.
    """
    if not rows:
        return rows

    total = len(rows)
    progress_bar = st.progress(0) if show_progress else None
    status_text = st.empty() if show_progress else None

    for n, row in enumerate(rows):
        ticker = row['Ticker']
        if show_progress:
            try:
                progress_bar.progress(min((n + 1) / total, 1.0))
                status_text.text(f"💰 Fetching fair value... {n + 1}/{total} — {ticker}")
            except Exception:
                pass

        fair_value = upside = pe_ratio = market_cap = cap_type = None

        try:
            fundamentals = get_stock_fundamentals(ticker)
            if fundamentals and fundamentals.get('price'):
                stock_info = get_stock_info(ticker)
                industry = stock_info['category'] if stock_info else fundamentals.get('industry', 'Other')
                cap_type = fundamentals.get('cap_type', 'Large')
                pe_ratio = fundamentals.get('trailing_pe')
                market_cap = fundamentals.get('market_cap')

                fv = calculate_fair_value(fundamentals, industry, cap_type)
                if fv and fv > 0:
                    ref = fundamentals['price']
                    up = ((fv - ref) / ref) * 100
                    if -95 <= up <= 350:
                        fair_value, upside = fv, up
        except Exception:
            pass

        row['Fair Value'] = fair_value
        row['Upside %'] = upside
        row['Value Tag'] = get_valuation_tag(upside)
        row['PE Ratio'] = pe_ratio
        row['Market Cap'] = market_cap
        row['Cap Type'] = cap_type

    if show_progress:
        try:
            progress_bar.empty()
            status_text.empty()
        except Exception:
            pass

    return rows


# ---------------------------------------------------------------------------
# MAIN SCREENER PIPELINE
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Deep-link helpers: jump from screener result row -> valuation screen
# ---------------------------------------------------------------------------
def build_valuation_link(ticker):
    """Build a deep link that opens the Individual Analysis (valuation) screen"""
    try:
        base = st.session_state.get("app_base_url", "").strip().rstrip("/")
    except Exception:
        base = ""
    query = f"?mode=valuation&ticker={quote(str(ticker))}"
    return f"{base}{query}" if base else query


def _get_query_param(name):
    """Read a URL query parameter across Streamlit versions"""
    val = None
    try:
        val = st.query_params.get(name)
    except Exception:
        try:
            val = st.experimental_get_query_params().get(name)
        except Exception:
            val = None
    if isinstance(val, list):
        val = val[0] if val else None
    return val


def render_valuation_jump(results_df, key_prefix):
    """Fallback in-app navigation to the valuation screen for any screened ticker"""
    if results_df is None or results_df.empty or 'Ticker' not in results_df.columns:
        return
    st.markdown("##### 🔗 Open Valuation Screen")
    c1, c2 = st.columns([3, 1])
    with c1:
        options = [f"{r['Ticker']} — {r.get('Name', '')}" for _, r in results_df.iterrows()]
        picked = st.selectbox(
            "Select a screened stock to run full valuation",
            options,
            key=f"{key_prefix}_val_pick",
            label_visibility="collapsed"
        )
    with c2:
        if st.button("📊 Open Valuation", key=f"{key_prefix}_val_btn",
                     use_container_width=True, type="primary"):
            chosen = picked.split(" — ")[0].strip()
            st.session_state["_pending_mode"] = "📈 Individual Analysis"
            st.session_state["input_method_radio"] = "✏️ Direct Ticker"
            st.session_state["deeplink_ticker"] = chosen
            st.session_state["auto_analyze"] = True
            st.rerun()


def valuation_column_config(extra=None):
    """Column config that renders the Valuation column as a clickable link"""
    cfg = {}
    try:
        cfg["Valuation"] = st.column_config.LinkColumn(
            "Valuation",
            display_text="📊 Analyze",
            help="Open this stock in the Individual Analysis / valuation screen"
        )
    except Exception:
        cfg = {}
    if extra and cfg:
        cfg.update(extra)
    return cfg


# ============================================================================
# NEWS SENTIMENT INDUSTRY SCREENER
# ============================================================================

# --- Multi-word financial phrases (checked FIRST, highest signal) ------------
# Unigram scoring cannot capture these: "beats" alone is ambiguous, but
# "beats estimates" is unambiguous. Phrases override individual word scores.
FIN_PHRASES = {
    # ---- Strongly positive -------------------------------------------------
    "beats estimates": 3.0, "beat estimates": 3.0, "beats expectations": 3.0,
    "beat expectations": 3.0, "tops estimates": 3.0, "topped estimates": 3.0,
    "better than expected": 2.8, "ahead of estimates": 2.6, "earnings beat": 3.0,
    "raises guidance": 3.2, "raised guidance": 3.2, "hikes guidance": 3.2,
    "raises outlook": 3.0, "raised outlook": 3.0, "upgrades outlook": 2.8,
    "record profit": 3.2, "record revenue": 3.0, "record high": 2.6,
    "all time high": 2.8, "all-time high": 2.8, "life high": 2.6,
    "52 week high": 2.2, "multi year high": 2.2,
    "order win": 2.8, "order wins": 2.8, "bags order": 2.8, "wins order": 2.8,
    "wins contract": 2.8, "bags contract": 2.8, "secures contract": 2.6,
    "new order": 2.0, "order book": 1.4, "order inflow": 1.8,
    "dividend hike": 2.4, "special dividend": 2.2, "bonus issue": 2.0,
    "buyback": 2.2, "share buyback": 2.4, "stock split": 1.2,
    "profit rises": 2.6, "profit jumps": 3.0, "profit surges": 3.2,
    "profit doubles": 3.4, "revenue jumps": 2.8, "revenue surges": 3.0,
    "margin expansion": 2.6, "margins expand": 2.6, "margin improvement": 2.4,
    "debt reduction": 2.4, "debt free": 2.6, "deleveraging": 2.0,
    "turns profitable": 3.0, "returns to profit": 3.0, "back in black": 2.8,
    "capacity expansion": 2.0, "new plant": 1.6, "greenfield": 1.4,
    "strategic partnership": 2.0, "joint venture": 1.6, "acquisition": 1.4,
    "stake buy": 1.8, "open offer": 1.6, "fund raise": 1.0,
    "target price raised": 2.8, "price target raised": 2.8,
    "rating upgrade": 3.0, "upgraded to buy": 3.2, "initiates coverage": 1.2,
    "outperform rating": 2.4, "overweight rating": 2.2, "accumulate rating": 1.8,
    "strong demand": 2.4, "demand revival": 2.4, "demand recovery": 2.4,
    "volume growth": 2.0, "market share gain": 2.4, "gains market share": 2.4,
    "cost savings": 1.8, "operational efficiency": 1.8,
    "government approval": 2.2, "regulatory approval": 2.4, "clearance received": 2.2,
    "usfda approval": 3.0, "drug approval": 2.8, "patent granted": 2.4,
    "successful trial": 2.6, "positive results": 2.4,
    "gst cut": 2.0, "tax benefit": 1.8, "subsidy": 1.4, "incentive scheme": 1.8,
    "pli scheme": 2.0, "policy support": 1.8, "rate cut": 1.6,

    # ---- Strongly negative -------------------------------------------------
    "misses estimates": -3.0, "missed estimates": -3.0, "miss estimates": -3.0,
    "misses expectations": -3.0, "below estimates": -2.8, "earnings miss": -3.0,
    "worse than expected": -2.8, "short of estimates": -2.6,
    "cuts guidance": -3.4, "cut guidance": -3.4, "lowers guidance": -3.4,
    "slashes guidance": -3.6, "cuts outlook": -3.2, "lowers outlook": -3.2,
    "withdraws guidance": -3.4, "profit warning": -3.6, "guidance cut": -3.4,
    "profit falls": -2.6, "profit drops": -2.6, "profit declines": -2.6,
    "profit slumps": -3.0, "profit plunges": -3.2, "profit halves": -3.2,
    "revenue falls": -2.6, "revenue declines": -2.6, "sales decline": -2.4,
    "margin pressure": -2.6, "margin contraction": -2.6, "margins shrink": -2.6,
    "posts loss": -3.0, "reports loss": -3.0, "net loss": -2.8,
    "widens loss": -3.2, "loss widens": -3.2, "slips into loss": -3.2,
    "record low": -2.6, "52 week low": -2.2, "all time low": -2.8,
    "multi year low": -2.2, "lifetime low": -2.6,
    "rating downgrade": -3.0, "downgraded to sell": -3.2, "cut to sell": -3.2,
    "target price cut": -2.8, "price target cut": -2.8, "underperform rating": -2.4,
    "underweight rating": -2.2, "reduce rating": -1.8,
    "order cancellation": -3.0, "contract cancelled": -3.0, "loses contract": -2.8,
    "order book decline": -2.4,
    "debt default": -3.8, "loan default": -3.8, "defaults on": -3.6,
    "insolvency": -3.6, "bankruptcy": -3.8, "nclt": -2.4, "ibc proceedings": -3.0,
    "credit rating downgrade": -3.2, "rating cut": -2.8, "debt burden": -2.4,
    "liquidity crisis": -3.4, "cash crunch": -3.0, "going concern": -3.2,
    "sebi probe": -3.2, "sebi investigation": -3.2, "ed raid": -3.6,
    "income tax raid": -3.4, "cbi probe": -3.4, "tax notice": -2.4,
    "show cause notice": -2.6, "regulatory action": -2.6, "penalty imposed": -2.6,
    "fraud allegation": -3.8, "accounting fraud": -4.0, "auditor resigns": -3.6,
    "resignation of cfo": -2.8, "cfo resigns": -2.8, "ceo resigns": -2.4,
    "promoter pledge": -2.4, "pledged shares": -2.0, "stake sale": -1.4,
    "block deal": -0.8, "promoter selling": -2.2, "insider selling": -2.0,
    "usfda warning": -3.4, "import alert": -3.4, "form 483": -2.8,
    "product recall": -3.0, "plant shutdown": -2.8, "production halt": -2.8,
    "strike": -2.2, "labour unrest": -2.4, "lockout": -2.6,
    "demand slowdown": -2.6, "demand weakness": -2.6, "slowdown": -2.0,
    "cost pressure": -2.0, "input cost": -1.6, "raw material cost": -1.6,
    "market share loss": -2.4, "loses market share": -2.4,
    "delisting": -2.4, "trading halt": -2.4, "circuit breaker": -1.6,
    "lower circuit": -2.6, "upper circuit": 2.6,
}

# --- Single-word financial lexicon ------------------------------------------
FIN_WORDS = {
    # positive
    "surge": 2.6, "surges": 2.6, "surged": 2.6, "soar": 2.8, "soars": 2.8,
    "soared": 2.8, "rally": 2.2, "rallies": 2.2, "rallied": 2.2, "jump": 2.2,
    "jumps": 2.2, "jumped": 2.2, "spike": 1.8, "spikes": 1.8, "climb": 1.6,
    "climbs": 1.6, "rise": 1.4, "rises": 1.4, "rose": 1.4, "gain": 1.6,
    "gains": 1.6, "gained": 1.6, "advance": 1.2, "advances": 1.2, "up": 0.8,
    "higher": 1.2, "outperform": 2.4, "outperforms": 2.4, "beat": 2.2,
    "beats": 2.2, "upgrade": 2.6, "upgrades": 2.6, "upgraded": 2.6,
    "bullish": 2.6, "buy": 1.8, "accumulate": 1.6, "overweight": 1.8,
    "strong": 1.8, "robust": 2.0, "solid": 1.6, "healthy": 1.6, "resilient": 1.6,
    "growth": 1.6, "expansion": 1.6, "profit": 1.4, "profitable": 2.0,
    "record": 1.8, "high": 0.8, "boost": 2.0, "boosts": 2.0, "boosted": 2.0,
    "improve": 1.6, "improves": 1.6, "improved": 1.6, "improvement": 1.6,
    "recovery": 1.8, "rebound": 2.0, "rebounds": 2.0, "revival": 1.8,
    "optimistic": 2.0, "confident": 1.6, "positive": 1.8, "favourable": 1.6,
    "favorable": 1.6, "attractive": 1.6, "opportunity": 1.2, "momentum": 1.2,
    "breakout": 1.8, "multibagger": 2.4, "rerating": 2.0, "re-rating": 2.0,
    "dividend": 1.2, "bonus": 1.4, "win": 1.8, "wins": 1.8, "won": 1.6,
    "secures": 1.6, "bags": 1.8, "approval": 1.8, "approved": 1.8,
    "launch": 1.0, "launches": 1.0, "partnership": 1.4, "expand": 1.4,
    "expands": 1.4, "efficiency": 1.2, "outlook": 0.4, "guidance": 0.3,

    # negative
    "plunge": -2.8, "plunges": -2.8, "plunged": -2.8, "crash": -3.0,
    "crashes": -3.0, "crashed": -3.0, "slump": -2.6, "slumps": -2.6,
    "slumped": -2.6, "tumble": -2.4, "tumbles": -2.4, "tumbled": -2.4,
    "sink": -2.2, "sinks": -2.2, "dive": -2.2, "dives": -2.2, "skid": -2.0,
    "slide": -1.8, "slides": -1.8, "drop": -1.8, "drops": -1.8, "dropped": -1.8,
    "fall": -1.8, "falls": -1.8, "fell": -1.8, "decline": -1.8, "declines": -1.8,
    "declined": -1.8, "down": -0.8, "lower": -1.2, "weak": -2.0, "weakness": -2.0,
    "weaker": -2.0, "soft": -1.4, "sluggish": -2.0, "tepid": -1.6, "muted": -1.4,
    "underperform": -2.4, "downgrade": -2.6, "downgrades": -2.6,
    "downgraded": -2.6, "bearish": -2.6, "sell": -1.8, "underweight": -1.8,
    "reduce": -1.4, "miss": -2.2, "misses": -2.2, "missed": -2.2,
    "loss": -2.4, "losses": -2.4, "lossmaking": -3.0, "deficit": -2.0,
    "debt": -1.2, "default": -3.2, "bankruptcy": -3.8, "insolvent": -3.6,
    "fraud": -3.8, "scam": -3.8, "probe": -2.4, "investigation": -2.2,
    "raid": -3.0, "penalty": -2.4, "fine": -2.0, "lawsuit": -2.4, "sues": -2.2,
    "litigation": -2.0, "violation": -2.6, "breach": -2.4, "irregularities": -3.0,
    "concern": -1.6, "concerns": -1.6, "worry": -1.8, "worries": -1.8,
    "fear": -2.0, "fears": -2.0, "risk": -1.2, "risks": -1.2, "uncertainty": -1.8,
    "volatile": -1.2, "volatility": -1.0, "pressure": -1.6, "headwind": -2.0,
    "headwinds": -2.0, "challenge": -1.4, "challenges": -1.4, "struggle": -2.2,
    "struggles": -2.2, "struggling": -2.4, "crisis": -3.0, "distress": -3.0,
    "slowdown": -2.0, "recession": -2.8, "contraction": -2.2, "shrink": -2.0,
    "cut": -1.6, "cuts": -1.6, "slash": -2.4, "slashes": -2.4, "halt": -2.2,
    "halts": -2.2, "suspend": -2.2, "suspends": -2.2, "shutdown": -2.6,
    "delay": -1.6, "delays": -1.6, "delayed": -1.6, "postpone": -1.4,
    "resign": -2.0, "resigns": -2.0, "resignation": -2.0, "exit": -1.2,
    "layoff": -2.2, "layoffs": -2.2, "retrench": -2.2, "downsizing": -2.0,
    "recall": -2.4, "warning": -2.4, "warns": -2.4, "caution": -1.6,
    "cautious": -1.4, "overvalued": -2.0, "bubble": -2.2, "selloff": -2.4,
    "sell-off": -2.4, "correction": -1.6, "pessimistic": -2.2, "negative": -1.8,
}

# Words that flip the polarity of what follows
NEGATORS = {
    "not", "no", "never", "none", "cannot", "cant", "can't", "wont", "won't",
    "dont", "don't", "doesnt", "doesn't", "didnt", "didn't", "isnt", "isn't",
    "arent", "aren't", "wasnt", "wasn't", "without", "lacks", "lacking",
    "fails", "failed", "fail", "unable", "denies", "denied", "rejects",
    "rejected", "rules out", "ruled out", "less", "fewer",
}

# Words that scale the intensity of what follows
INTENSIFIERS = {
    "very": 1.4, "extremely": 1.7, "highly": 1.4, "significantly": 1.5,
    "substantially": 1.5, "sharply": 1.6, "steeply": 1.6, "massively": 1.7,
    "hugely": 1.6, "strongly": 1.4, "considerably": 1.4, "dramatically": 1.6,
    "record": 1.4, "multi": 1.2, "sequentially": 1.1, "yoy": 1.1,
    "slightly": 0.5, "marginally": 0.5, "modestly": 0.6, "somewhat": 0.6,
    "mildly": 0.5, "partially": 0.7, "slight": 0.5, "minor": 0.5,
}

# Headlines matching these are noise for sentiment purposes
NOISE_PATTERNS = (
    "stocks to watch", "market wrap", "closing bell", "opening bell",
    "top gainers", "top losers", "nifty today", "sensex today",
    "stock market live", "share price live", "muhurat", "trading calendar",
    "buy sell hold", "technical view", "f&o ban", "fno ban",
)

# --- Optional VADER blend ---------------------------------------------------
# VADER adds general-language tone on top of the financial lexicon. It is a
# small pure-Python package with no model download. If it is not installed the
# engine still works — the financial lexicon does the heavy lifting.
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _VADER = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except Exception:
    _VADER = None
    VADER_AVAILABLE = False

_TOKEN_RE = re.compile(r"[a-z0-9&'\-]+")
_MAX_PHRASE_LEN = max(len(p.split()) for p in FIN_PHRASES)


def _normalise(text):
    if not text:
        return ""
    t = str(text).lower()
    t = t.replace("’", "'").replace("‘", "'")
    t = re.sub(r"[%₹$]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def is_noise_headline(text):
    t = _normalise(text)
    return any(p in t for p in NOISE_PATTERNS)


def _apply_modifiers(tokens, start, end, value, consumed=None):
    """
    Apply negation and intensity modifiers to a scored span [start, end).

    Shared by the phrase pass and the unigram pass so that "revenue declines
    sharply" and "declines sharply" are treated the same way — without this,
    a multi-word phrase would swallow its own modifiers.
    """
    n = len(tokens)
    mult = 1.0
    negated = False

    # Backward window: negators and pre-modifiers
    for back in range(1, 4):
        j = start - back
        if j < 0:
            break
        prev = tokens[j]
        if prev in NEGATORS:
            negated = True
        elif prev in INTENSIFIERS:
            mult *= INTENSIFIERS[prev]

    # Forward window: post-modifiers ("rises sharply", "declines slightly")
    for fwd in range(0, 2):
        k = end + fwd
        if k >= n:
            break
        if consumed is not None and k in consumed:
            break
        if tokens[k] in INTENSIFIERS:
            mult *= INTENSIFIERS[tokens[k]]
            break

    value *= mult
    if negated:
        value = -value * 0.75
    return value


def score_text(text):
    """
    Score a single piece of text on a roughly -1..+1 scale.

    Phrase matches take priority over unigrams and consume their tokens, so
    "cuts guidance" scores as one strong negative signal rather than the sum
    of two weak ones.
    """
    t = _normalise(text)
    if not t:
        return 0.0, []

    hits = []
    consumed = set()
    tokens = _TOKEN_RE.findall(t)
    n = len(tokens)
    if n == 0:
        return 0.0, []

    # --- Pass 1: multi-word phrases, longest first ---------------------------
    for size in range(min(_MAX_PHRASE_LEN, n), 1, -1):
        for i in range(n - size + 1):
            if any(j in consumed for j in range(i, i + size)):
                continue
            gram = " ".join(tokens[i:i + size])
            if gram in FIN_PHRASES:
                # Backward lookback catches "fails to beat estimates" and
                # "does not expect profit warning", where the negator is
                # separated from the phrase by a linking verb or particle.
                val = _apply_modifiers(tokens, i, i + size, FIN_PHRASES[gram])
                hits.append((gram, val))
                consumed.update(range(i, i + size))

    # --- Pass 2: single words on the remaining tokens ------------------------
    for i, tok in enumerate(tokens):
        if i in consumed or tok not in FIN_WORDS:
            continue
        val = _apply_modifiers(tokens, i, i + 1, FIN_WORDS[tok], consumed)
        hits.append((tok, val))

    if not hits:
        base = 0.0
    else:
        total = sum(v for _, v in hits)
        # Normalise with a saturating curve so long headlines don't dominate
        base = total / math.sqrt(total * total + 9.0)

    # --- Blend VADER for general-language tone --------------------------------
    if VADER_AVAILABLE:
        try:
            v = _VADER.polarity_scores(t)["compound"]
        except Exception:
            v = 0.0
        # Financial lexicon dominates; VADER only nudges
        if hits:
            base = 0.85 * base + 0.15 * v
        else:
            base = 0.35 * v

    return max(-1.0, min(1.0, base)), hits


def recency_weight(age_hours, half_life_hours=48.0):
    """Exponential decay so a 2-day-old headline counts half as much."""
    if age_hours is None or age_hours < 0:
        return 0.5
    return 0.5 ** (age_hours / half_life_hours)


def sentiment_label(score):
    if score is None:
        return "❔ No News"
    if score >= 0.35:
        return "🟢 Very Bullish"
    if score >= 0.12:
        return "🟢 Bullish"
    if score > -0.12:
        return "⚪ Neutral"
    if score > -0.35:
        return "🔴 Bearish"
    return "🔴 Very Bearish"


# ---------------------------------------------------------------------------
# News fetching — defensive across yfinance schema versions
# ---------------------------------------------------------------------------
def _parse_news_item(item):
    """
    Normalise one news item into {title, summary, publisher, link, published}.

    yfinance has used at least two shapes:
      - legacy (<=0.2.54): flat dict with 'title', 'publisher',
        'providerPublishTime' (epoch seconds), 'link'
      - current (>=0.2.55): nested under 'content' with 'title', 'summary',
        'pubDate' (ISO string), 'provider': {'displayName'},
        'canonicalUrl': {'url'}
    Both are handled, plus Google News RSS entries, so a yfinance upgrade
    cannot silently break the screener.
    """
    if not isinstance(item, dict):
        return None

    content = item.get('content') if isinstance(item.get('content'), dict) else item

    title = content.get('title') or item.get('title')
    if not title:
        return None

    summary = content.get('summary') or content.get('description') or item.get('summary') or ''

    # Publisher
    publisher = ''
    prov = content.get('provider')
    if isinstance(prov, dict):
        publisher = prov.get('displayName') or prov.get('name') or ''
    if not publisher:
        publisher = item.get('publisher') or content.get('publisher') or ''

    # Link
    link = ''
    canon = content.get('canonicalUrl') or content.get('clickThroughUrl')
    if isinstance(canon, dict):
        link = canon.get('url', '')
    if not link:
        link = item.get('link') or content.get('link') or ''

    # Published timestamp -> tz-naive datetime
    published = None
    epoch = item.get('providerPublishTime') or content.get('providerPublishTime')
    if epoch:
        try:
            published = datetime.fromtimestamp(float(epoch))
        except Exception:
            published = None
    if published is None:
        raw = content.get('pubDate') or content.get('displayTime') or item.get('pubDate')
        if raw:
            try:
                ts = pd.to_datetime(raw, errors='coerce', utc=True)
                if pd.notna(ts):
                    published = ts.tz_convert(None).to_pydatetime()
            except Exception:
                published = None

    return {
        'title': str(title).strip(),
        'summary': str(summary).strip()[:400],
        'publisher': str(publisher).strip(),
        'link': str(link).strip(),
        'published': published,
    }


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock_news(ticker, max_items=10):
    """Fetch recent news for one ticker. Cached 30 min. Never raises."""
    items = []
    try:
        tk = yf.Ticker(ticker)
        raw = None
        try:
            raw = tk.get_news(count=max_items)
        except TypeError:
            raw = tk.news          # very old yfinance: plain property
        except Exception:
            raw = None
        if not raw:
            try:
                raw = tk.news
            except Exception:
                raw = None
        if raw:
            for it in raw[:max_items]:
                parsed = _parse_news_item(it)
                if parsed and parsed['title']:
                    items.append(parsed)
    except Exception:
        pass
    return items


def score_articles(articles, lookback_days=7, half_life_hours=48.0, drop_noise=True):
    """
    Turn a list of articles into an aggregate sentiment for one stock.

    Headlines are weighted more heavily than summaries (headlines carry the
    editorial judgement), and older news decays exponentially.
    """
    now = datetime.now()
    scored = []

    for a in articles:
        title = a.get('title', '')
        if drop_noise and is_noise_headline(title):
            continue

        age_hours = None
        if a.get('published'):
            try:
                age_hours = (now - a['published']).total_seconds() / 3600.0
                if age_hours > lookback_days * 24:
                    continue
                if age_hours < -12:      # clock skew / bad timestamps
                    continue
            except Exception:
                age_hours = None

        s_title, hits = score_text(title)
        s_summary, _ = score_text(a.get('summary', ''))
        combined = 0.75 * s_title + 0.25 * s_summary if a.get('summary') else s_title

        w = recency_weight(age_hours, half_life_hours)
        scored.append({
            'title': title,
            'publisher': a.get('publisher', ''),
            'link': a.get('link', ''),
            'published': a.get('published'),
            'age_hours': age_hours,
            'score': combined,
            'weight': w,
            'drivers': ", ".join(k for k, _ in sorted(hits, key=lambda x: -abs(x[1]))[:3]),
        })

    if not scored:
        return None

    tw = sum(x['weight'] for x in scored)
    agg = sum(x['score'] * x['weight'] for x in scored) / tw if tw > 0 else 0.0
    pos = sum(1 for x in scored if x['score'] > 0.12)
    neg = sum(1 for x in scored if x['score'] < -0.12)

    # Freshness (0-1): the weighted average alone is age-blind for a single
    # article — a lone 5-day-old headline would score the same as a lone
    # 1-hour-old one. This carries the age information forward so the
    # industry rollup can discount stale coverage.
    freshness = tw / len(scored) if scored else 0.0

    # Disagreement between articles: high when the news flow is genuinely
    # mixed, which makes the average less trustworthy.
    if len(scored) > 1:
        mean_s = sum(x['score'] for x in scored) / len(scored)
        variance = sum((x['score'] - mean_s) ** 2 for x in scored) / len(scored)
        dispersion = math.sqrt(variance)
    else:
        dispersion = 0.0

    # Hours since the most recent article
    ages = [x['age_hours'] for x in scored if x['age_hours'] is not None]
    newest = min(ages) if ages else None

    return {
        'sentiment': agg,
        'article_count': len(scored),
        'positive_count': pos,
        'negative_count': neg,
        'freshness': freshness,
        'dispersion': dispersion,
        'newest_hours': newest,
        'articles': sorted(scored, key=lambda x: -abs(x['score']))[:5],
    }


# ---------------------------------------------------------------------------
# Price momentum — batch fetched, used to confirm sentiment
# ---------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_momentum_batch(tickers_tuple, period="3mo"):
    """Batch daily OHLCV -> momentum stats per ticker. Cached 30 min."""
    tickers = list(tickers_tuple)
    out = {}
    if not tickers:
        return out
    try:
        data = yf.download(tickers=" ".join(tickers), period=period, interval="1d",
                           group_by="ticker", auto_adjust=False, threads=True,
                           progress=False)
    except Exception:
        return out
    if data is None or len(data) == 0:
        return out

    def _stats(df):
        try:
            df = df.dropna(subset=['Close'])
            if len(df) < 25:
                return None
            c = df['Close']
            v = df['Volume'].fillna(0)
            last = float(c.iloc[-1])
            r5 = (last / float(c.iloc[-6]) - 1) * 100 if len(c) > 6 else 0.0
            r20 = (last / float(c.iloc[-21]) - 1) * 100 if len(c) > 21 else 0.0
            sma20 = float(c.rolling(20).mean().iloc[-1])
            sma50 = float(c.rolling(50).mean().iloc[-1]) if len(c) >= 50 else sma20
            vol20 = float(v.rolling(20).mean().iloc[-1]) if len(v) >= 20 else float(v.mean())
            vol5 = float(v.iloc[-5:].mean())
            hi52 = float(c.max())
            return {
                'price': last,
                'ret_5d': r5,
                'ret_20d': r20,
                'above_sma20': last > sma20,
                'above_sma50': last > sma50,
                'vol_ratio': (vol5 / vol20) if vol20 > 0 else 1.0,
                'from_high_pct': (last / hi52 - 1) * 100 if hi52 else 0.0,
            }
        except Exception:
            return None

    try:
        if isinstance(data.columns, pd.MultiIndex):
            for t in tickers:
                try:
                    s = _stats(data[t])
                    if s:
                        out[t] = s
                except Exception:
                    continue
        elif len(tickers) == 1:
            s = _stats(data)
            if s:
                out[tickers[0]] = s
    except Exception:
        pass
    return out


# ---------------------------------------------------------------------------
# Industry-level sentiment screener
# ---------------------------------------------------------------------------
def compute_swing_score(sentiment, breadth, ret_5d, ret_20d, above_sma20,
                        vol_ratio, article_count, freshness=1.0):
    """
    Blend news sentiment with price confirmation into a 0-100 swing score.

    Sentiment alone is a weak and noisy signal — it is most useful when price
    action agrees with it. Roughly half the weight is sentiment/breadth and
    half is momentum/participation, so a sentiment spike with no price
    response scores only moderately.
    """
    # Sentiment component (0-35)
    s_comp = (max(-1.0, min(1.0, sentiment)) + 1) / 2 * 35

    # Breadth: share of stocks with positive news (0-15)
    b_comp = max(0.0, min(1.0, breadth)) * 15

    # Momentum (0-30)
    m5 = max(-1.0, min(1.0, ret_5d / 8.0))
    m20 = max(-1.0, min(1.0, ret_20d / 20.0))
    m_comp = ((m5 * 0.6 + m20 * 0.4) + 1) / 2 * 30

    # Trend participation (0-10)
    t_comp = max(0.0, min(1.0, above_sma20)) * 10

    # Volume confirmation (0-10)
    v_comp = max(0.0, min(1.0, (vol_ratio - 0.8) / 0.7)) * 10

    score = s_comp + b_comp + m_comp + t_comp + v_comp

    # Penalise thin news coverage — 1 article is not a trend
    if article_count < 3:
        score *= 0.85
    if article_count < 2:
        score *= 0.85

    # Pull the sentiment contribution toward neutral when the news is stale.
    # freshness ~1.0 means coverage is hours old; ~0.25 means several days.
    if freshness < 1.0:
        neutral = 50.0
        score = neutral + (score - neutral) * (0.55 + 0.45 * max(0.0, min(1.0, freshness)))

    return max(0.0, min(100.0, score))


def trend_label(score, sentiment):
    if score >= 72 and sentiment > 0.1:
        return "🔥 Hot — Strong Uptrend"
    if score >= 62:
        return "📈 Trending Up"
    if score >= 52:
        return "🟢 Improving"
    if score >= 42:
        return "⚪ Neutral"
    if score >= 32:
        return "🔻 Weakening"
    return "❄️ Cold — Avoid"


def run_sentiment_industry_screener(selected_industries, stocks_per_industry=6,
                                    lookback_days=7, max_articles=8,
                                    half_life_hours=48.0, max_workers=6):
    """
    Score each industry by aggregating news sentiment across a sample of its
    stocks, confirmed against price momentum.

    Returns (industry_df, stock_df).
    """
    # ---- Build the sample -------------------------------------------------
    sample = {}          # industry -> [tickers]
    all_tickers = []
    for ind in selected_industries:
        stocks = get_stocks_by_category(ind)
        if not stocks:
            continue
        picks = list(stocks.keys())[:stocks_per_industry]
        if picks:
            sample[ind] = picks
            all_tickers.extend(picks)

    if not all_tickers:
        return pd.DataFrame(), pd.DataFrame()

    progress_bar = st.progress(0)
    status_text = st.empty()

    # ---- Momentum in batches (fast) ---------------------------------------
    status_text.text("📈 Fetching price momentum...")
    momentum = {}
    for i in range(0, len(all_tickers), 40):
        momentum.update(fetch_momentum_batch(tuple(all_tickers[i:i + 40])))

    # ---- News in parallel (the slow part) ----------------------------------
    news_map = {}
    done = 0
    total = len(all_tickers)

    def _work(tk):
        return tk, fetch_stock_news(tk, max_articles)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(_work, t): t for t in all_tickers}
            for fut in as_completed(futures):
                done += 1
                try:
                    progress_bar.progress(min(done / total, 1.0))
                    status_text.text(f"📰 Reading news... {done}/{total}")
                except Exception:
                    pass
                try:
                    tk, arts = fut.result()
                    news_map[tk] = arts
                except Exception:
                    continue
    except Exception:
        # Fall back to serial if threads are unavailable
        for tk in all_tickers:
            news_map[tk] = fetch_stock_news(tk, max_articles)

    # ---- Score each stock --------------------------------------------------
    stock_rows = []
    for ind, tickers in sample.items():
        for tk in tickers:
            agg = score_articles(news_map.get(tk, []), lookback_days, half_life_hours)
            mom = momentum.get(tk, {})
            name = get_stocks_by_category(ind).get(tk, tk)

            stock_rows.append({
                'Industry': ind,
                'Ticker': tk,
                'Name': name,
                'Sentiment': agg['sentiment'] if agg else None,
                'Mood': sentiment_label(agg['sentiment'] if agg else None),
                'Articles': agg['article_count'] if agg else 0,
                'Positive': agg['positive_count'] if agg else 0,
                'Negative': agg['negative_count'] if agg else 0,
                'Freshness': agg['freshness'] if agg else None,
                'Newest (h)': agg['newest_hours'] if agg else None,
                'Price': mom.get('price'),
                'Ret 5D %': mom.get('ret_5d'),
                'Ret 20D %': mom.get('ret_20d'),
                'Vol Ratio': mom.get('vol_ratio'),
                'Above SMA20': mom.get('above_sma20'),
                '_articles': agg['articles'] if agg else [],
                'Valuation': build_valuation_link(tk),
            })

    stock_df = pd.DataFrame(stock_rows)

    # ---- Roll up to industry level ----------------------------------------
    ind_rows = []
    for ind in sample:
        sub = stock_df[stock_df['Industry'] == ind]
        if sub.empty:
            continue

        with_news = sub[sub['Sentiment'].notna()]
        total_articles = int(sub['Articles'].sum())

        if not with_news.empty:
            # Weight by volume of news AND how fresh it is, so a stock with
            # one week-old story cannot outvote one with today's coverage.
            w = with_news['Articles'].clip(lower=1) * with_news['Freshness'].fillna(0.5)
            w = w.clip(lower=0.01)
            avg_sent = float((with_news['Sentiment'] * w).sum() / w.sum())
            breadth = float((with_news['Sentiment'] > 0.12).sum() / len(with_news))
            avg_fresh = float(with_news['Freshness'].fillna(0.5).mean())
        else:
            avg_sent = 0.0
            breadth = 0.0
            avg_fresh = 0.0

        r5 = float(sub['Ret 5D %'].dropna().mean()) if sub['Ret 5D %'].notna().any() else 0.0
        r20 = float(sub['Ret 20D %'].dropna().mean()) if sub['Ret 20D %'].notna().any() else 0.0
        vr = float(sub['Vol Ratio'].dropna().mean()) if sub['Vol Ratio'].notna().any() else 1.0
        above = float(sub['Above SMA20'].dropna().mean()) if sub['Above SMA20'].notna().any() else 0.0

        score = compute_swing_score(avg_sent, breadth, r5, r20, above, vr,
                                    total_articles, avg_fresh)

        ind_rows.append({
            'Industry': ind,
            'Swing Score': score,
            'Trend': trend_label(score, avg_sent),
            'Sentiment': avg_sent,
            'Mood': sentiment_label(avg_sent if total_articles else None),
            'Breadth %': breadth * 100,
            'Articles': total_articles,
            'Freshness': avg_fresh,
            'Stocks': len(sub),
            'Avg 5D %': r5,
            'Avg 20D %': r20,
            'Above SMA20 %': above * 100,
            'Vol Ratio': vr,
        })

    try:
        progress_bar.empty()
        status_text.empty()
    except Exception:
        pass

    ind_df = pd.DataFrame(ind_rows)
    if not ind_df.empty:
        ind_df = ind_df.sort_values('Swing Score', ascending=False).reset_index(drop=True)
    return ind_df, stock_df


# ============================================================================
# MANUAL VALUATION ENGINE — pure functions, no Streamlit
# ============================================================================
# Unit convention (matters, and is the usual source of silent errors):
#   - Revenue / EBITDA / FCF / Net debt : ₹ Crore
#   - Share count                       : Crore shares
#   - EPS / BVPS / DPS / Price          : ₹ per share
# With those units, (₹ Cr) / (Cr shares) = ₹/share, so the crore cancels and
# no 1e7 conversion factor is ever needed.
# ============================================================================



def _pos(x):
    """True when x is a usable positive number."""
    try:
        return x is not None and not (isinstance(x, float) and math.isnan(x)) and float(x) > 0
    except Exception:
        return False


def _num(x, default=0.0):
    try:
        if x is None:
            return default
        v = float(x)
        return default if math.isnan(v) or math.isinf(v) else v
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Derived inputs
# ---------------------------------------------------------------------------
def eps_from_revenue(revenue_cr, net_margin_pct, shares_cr):
    """
    Revenue model -> EPS.

    EPS = (Revenue x net margin) / share count. This is the route to use when
    you trust a revenue forecast and a margin assumption more than a broker's
    headline EPS number, which is exactly the 'reported vs estimated' case.
    """
    if not (_pos(revenue_cr) and _pos(shares_cr)):
        return None
    margin = _num(net_margin_pct) / 100.0
    profit_cr = revenue_cr * margin
    return profit_cr / shares_cr


def bvps_from_equity(equity_cr, shares_cr):
    if not (_pos(equity_cr) and _pos(shares_cr)):
        return None
    return equity_cr / shares_cr


def net_debt(total_debt_cr, cash_cr):
    """Net debt can legitimately be negative (net cash)."""
    return _num(total_debt_cr) - _num(cash_cr)


# ---------------------------------------------------------------------------
# Individual valuation methods. Each returns ₹/share or None.
# ---------------------------------------------------------------------------
def fv_pe(eps, target_pe):
    """Classic earnings multiple. Negative EPS makes this meaningless."""
    if not (_pos(eps) and _pos(target_pe)):
        return None
    return eps * target_pe

def fv_forward_pe(fwd_eps, forward_pe):
    if not (_pos(fwd_eps) and _pos(forward_pe)):
        return None
    return fwd_eps * forward_pe

def fv_pb(bvps, target_pb):
    if not (_pos(bvps) and _pos(target_pb)):
        return None
    return bvps * target_pb

def fv_ps(revenue_cr, shares_cr, target_ps):
    if not (_pos(revenue_cr) and _pos(shares_cr) and _pos(target_ps)):
        return None
    return (revenue_cr / shares_cr) * target_ps

def fv_ev_ebitda(ebitda_cr, target_multiple, net_debt_cr, shares_cr):
    """
    EV/EBITDA -> equity value per share.

    Enterprise value is what the whole business is worth; equity holders get
    EV minus net debt. Skipping the net-debt step is the most common mistake
    in EV-based valuation and badly overvalues leveraged companies.
    """
    if not (_pos(ebitda_cr) and _pos(target_multiple) and _pos(shares_cr)):
        return None
    ev = ebitda_cr * target_multiple
    equity = ev - _num(net_debt_cr)
    if equity <= 0:
        return None          # debt exceeds enterprise value
    return equity / shares_cr

def fv_peg(eps, growth_pct, target_peg=1.0):
    """
    PEG-implied multiple: target PE = PEG x growth rate.

    Only meaningful for positive growth; a declining business cannot be
    valued this way.
    """
    if not (_pos(eps) and _pos(growth_pct) and _pos(target_peg)):
        return None
    implied_pe = target_peg * growth_pct
    return eps * implied_pe

def fv_graham(eps, bvps):
    """
    Graham Number = sqrt(22.5 x EPS x BVPS).

    22.5 comes from Graham's ceilings of 15x earnings and 1.5x book. It is a
    deliberately conservative floor, not a target price.
    """
    if not (_pos(eps) and _pos(bvps)):
        return None
    return math.sqrt(22.5 * eps * bvps)

def fv_earnings_power(eps, required_return_pct):
    """Capitalised earnings: EPS / r. A no-growth perpetuity value."""
    if not (_pos(eps) and _pos(required_return_pct)):
        return None
    return eps / (required_return_pct / 100.0)

def fv_ddm(dps, required_return_pct, growth_pct):
    """
    Gordon growth dividend discount: V = D1 / (r - g).

    Requires r > g, otherwise the formula diverges and returns nonsense.
    """
    if not (_pos(dps) and _pos(required_return_pct)):
        return None
    r = required_return_pct / 100.0
    g = _num(growth_pct) / 100.0
    if r - g <= 0.005:        # need a real spread, not a near-zero divisor
        return None
    d1 = dps * (1 + g)
    return d1 / (r - g)

def fv_dcf(fcf_cr, shares_cr, growth_pct, years, terminal_growth_pct,
           discount_rate_pct, net_debt_cr=0.0, fade_to_terminal=True):
    """
    Two-stage FCF DCF.

    Stage 1 grows FCF for `years`. With fade_to_terminal the growth rate
    declines linearly toward the terminal rate across the forecast, which is
    more defensible than a cliff-edge drop from 25% to 3% in a single year.
    Stage 2 is a Gordon terminal value, discounted back.
    """
    if not (_pos(fcf_cr) and _pos(shares_cr) and _pos(discount_rate_pct)):
        return None
    years = int(_num(years, 5))
    if years < 1 or years > 30:
        return None

    r = discount_rate_pct / 100.0
    g0 = _num(growth_pct) / 100.0
    gt = _num(terminal_growth_pct) / 100.0

    if r - gt <= 0.005:
        return None           # terminal growth must stay below the discount rate

    pv_sum = 0.0
    fcf = fcf_cr
    for t in range(1, years + 1):
        if fade_to_terminal and years > 1:
            g = g0 + (gt - g0) * ((t - 1) / (years - 1))
        else:
            g = g0
        fcf = fcf * (1 + g)
        pv_sum += fcf / ((1 + r) ** t)

    terminal = (fcf * (1 + gt)) / (r - gt)
    pv_terminal = terminal / ((1 + r) ** years)

    ev = pv_sum + pv_terminal
    equity = ev - _num(net_debt_cr)
    if equity <= 0:
        return None
    return equity / shares_cr


# ---------------------------------------------------------------------------
# Blending
# ---------------------------------------------------------------------------
def blend_valuations(results, weights, margin_of_safety_pct=0.0):
    """
    Weighted blend across methods.

    Weights are renormalised over the methods that actually produced a value,
    so switching a method off (or it returning None for bad inputs) silently
    redistributes its weight rather than dragging the blend toward zero.
    """
    usable = {k: v for k, v in results.items()
              if _pos(v) and _pos(weights.get(k, 0))}
    if not usable:
        return None, {}

    total_w = sum(weights[k] for k in usable)
    if total_w <= 0:
        return None, {}

    effective = {k: weights[k] / total_w for k in usable}
    blended = sum(usable[k] * effective[k] for k in usable)

    if margin_of_safety_pct:
        blended *= (1 - _num(margin_of_safety_pct) / 100.0)

    return blended, effective


def valuation_stats(results):
    """Min / median / max / spread across the methods that produced a value."""
    vals = sorted(v for v in results.values() if _pos(v))
    if not vals:
        return None
    n = len(vals)
    median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
    return {
        'count': n,
        'min': vals[0],
        'max': vals[-1],
        'median': median,
        'mean': sum(vals) / n,
        'spread_pct': ((vals[-1] - vals[0]) / vals[0] * 100) if vals[0] else None,
    }


# ---------------------------------------------------------------------------
# Reverse valuation: what does today's price already assume?
# ---------------------------------------------------------------------------
def implied_pe(price, eps):
    if not (_pos(price) and _pos(eps)):
        return None
    return price / eps

def implied_growth_for_pe(price, eps, target_peg=1.0):
    """Growth rate the market is paying for, read through a PEG lens."""
    pe = implied_pe(price, eps)
    if pe is None or not _pos(target_peg):
        return None
    return pe / target_peg

def implied_eps_for_price(price, target_pe):
    """EPS the company must deliver to justify today's price at a given P/E."""
    if not (_pos(price) and _pos(target_pe)):
        return None
    return price / target_pe


# ---------------------------------------------------------------------------
# Scenario + sensitivity
# ---------------------------------------------------------------------------
def build_scenarios(eps, target_pe, bear_eps_cut_pct=20.0, bull_eps_lift_pct=20.0,
                    bear_pe_cut_pct=25.0, bull_pe_lift_pct=25.0):
    """Bear / Base / Bull on the two levers that matter most: EPS and the multiple."""
    if not (_pos(eps) and _pos(target_pe)):
        return None
    return {
        'Bear': {
            'eps': eps * (1 - bear_eps_cut_pct / 100.0),
            'pe': target_pe * (1 - bear_pe_cut_pct / 100.0),
        },
        'Base': {'eps': eps, 'pe': target_pe},
        'Bull': {
            'eps': eps * (1 + bull_eps_lift_pct / 100.0),
            'pe': target_pe * (1 + bull_pe_lift_pct / 100.0),
        },
    }


def sensitivity_grid(eps, eps_deltas_pct, pe_values):
    """
    Fair-value matrix across EPS scenarios (rows) and target P/E (columns).

    Shows how much of a valuation depends on the multiple rather than the
    earnings — usually more than people expect.
    """
    if not _pos(eps):
        return None
    grid = []
    for d in eps_deltas_pct:
        e = eps * (1 + d / 100.0)
        grid.append({
            'eps_delta': d,
            'eps': e,
            'values': [e * pe if _pos(pe) else None for pe in pe_values],
        })
    return grid




def create_football_field_chart(method_values, current_price, blended=None):
    """
    Football-field chart: each valuation method as a horizontal bar against
    the live price. The point is to show the RANGE of defensible values, not
    a single false-precision number.
    """
    rows = [(k, v) for k, v in method_values.items() if v and v > 0]
    if not rows:
        return None

    rows.sort(key=lambda x: x[1])
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    colors_list = ['#16a34a' if v > current_price else '#dc2626' for v in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=values, orientation='h',
        marker=dict(color=colors_list),
        text=[f"₹{v:,.0f}" for v in values],
        textposition='outside',
        hovertemplate="%{y}<br>Fair value ₹%{x:,.2f}<extra></extra>",
        name="Fair value"
    ))

    fig.add_vline(x=current_price, line_width=2, line_dash="dash",
                  line_color="#2563eb",
                  annotation_text=f"LTP ₹{current_price:,.2f}",
                  annotation_position="top")

    if blended and blended > 0:
        fig.add_vline(x=blended, line_width=2, line_dash="dot",
                      line_color="#f59e0b",
                      annotation_text=f"Blended ₹{blended:,.0f}",
                      annotation_position="bottom")

    fig.update_layout(
        title="Valuation Range by Method",
        xaxis_title="Fair value per share (₹)",
        height=max(320, 45 * len(rows) + 140),
        margin=dict(l=10, r=60, t=60, b=40),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


# ---------------------------------------------------------------------------
# SHARED VALUATION PRESENTATION
# ---------------------------------------------------------------------------
# Used by BOTH the system (model) valuation and the manual valuation so the
# two render identically and can be compared at a glance.
# ---------------------------------------------------------------------------
def recommendation_for_upside(upside):
    """Map an upside % to the same card class / label / icon used everywhere."""
    if upside is None:
        return "rec-hold", "Insufficient Data", "❔"
    if upside > 25:
        return "rec-strong-buy", "Significantly Undervalued", "🚀"
    if upside > 15:
        return "rec-buy", "Undervalued", "✅"
    if upside > 0:
        return "rec-buy", "Fairly Valued", "📥"
    if upside > -10:
        return "rec-hold", "Slightly Overvalued", "⏸️"
    return "rec-avoid", "Overvalued", "⚠️"


def render_company_header(company, ticker, sector, industry):
    st.markdown(f'''
    <div class="company-header">
        <div class="company-title">{company}</div>
        <div class="company-info">
            🏷️ {ticker} • 🏢 {sector} • 🏭 {industry}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_fair_value_card(fair_value, price, upside, title="📊 Calculated Fair Value"):
    arrow = "📈" if (upside or 0) > 0 else "📉"
    up_txt = f"{upside:+.2f}% Potential" if upside is not None else "Upside unavailable"
    st.markdown(f'''
    <div class="fair-value-card">
        <div class="fair-value-title">{title}</div>
        <div class="fair-value-amount">₹{fair_value:,.2f}</div>
        <div class="fair-value-details">
            Current Price: ₹{price:,.2f}<br>
            {arrow} {up_txt}
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_recommendation_card(upside):
    cls, text, icon = recommendation_for_upside(upside)
    ret = f"{upside:+.2f}%" if upside is not None else "N/A"
    st.markdown(f'''
    <div class="recommendation-card {cls}">
        <h3>{icon} {text}</h3>
        <p>Expected Return: {ret}</p>
    </div>
    ''', unsafe_allow_html=True)


def render_metric_cards(items):
    """items = [(icon, value, label), ...] rendered as the standard metric cards."""
    if not items:
        return
    cols = st.columns(len(items))
    for col, (icon, value, label) in zip(cols, items):
        with col:
            st.markdown(f'''
            <div class="metric-card">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            ''', unsafe_allow_html=True)


def render_valuation_box(method_title, rows):
    """rows = [(label, value_string), ...] in the standard valuation-box style."""
    inner = "".join(
        f'''<div class="valuation-row">
            <span class="valuation-label">{lbl}</span>
            <span class="valuation-value">{val}</span>
        </div>''' for lbl, val in rows
    )
    st.markdown(f'''
    <div class="valuation-box">
        <div class="valuation-method">{method_title}</div>
        {inner}
    </div>
    ''', unsafe_allow_html=True)


def create_manual_comparison_chart(price, method_values, blended):
    """
    Price vs fair value bars for the manual valuation, styled to match the
    system valuation's comparison chart.
    """
    rows = [(k, v) for k, v in method_values.items() if v and v > 0]
    if not rows:
        return None
    rows.sort(key=lambda x: x[1])

    labels = ["Current Price"] + [r[0] for r in rows] + ["Blended"]
    values = [price] + [r[1] for r in rows] + [blended]
    colors_list = (["#2563eb"]
                   + ['#16a34a' if v > price else '#dc2626' for _, v in rows]
                   + ["#f59e0b"])

    fig = go.Figure(go.Bar(
        x=labels, y=values, marker=dict(color=colors_list),
        text=[f"₹{v:,.0f}" for v in values], textposition='outside',
        hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        title="Price vs Fair Value by Method",
        yaxis_title="₹ per share",
        height=420, showlegend=False,
        margin=dict(l=10, r=10, t=60, b=90),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=-35),
    )
    return fig


def compute_system_valuation(ticker):
    """
    Run the app's own model on a ticker: the same path the screeners use.
    Returns (vals, fundamentals, info, error_string).
    """
    try:
        info, err = fetch_stock_data(ticker)
    except Exception as e:
        return None, None, None, str(e)[:120]
    if err or not info:
        return None, None, None, (err or "No data returned")

    try:
        si = get_stock_info(ticker)
        industry = si['category'] if si else None
        vals = calculate_valuations(info, industry)
        fund = get_stock_fundamentals(ticker)
        return vals, fund, info, None
    except Exception as e:
        return None, None, info, str(e)[:120]


# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================
def create_gauge_chart(upside_pe, upside_ev):
    """Create professional dual gauge chart for valuations"""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        horizontal_spacing=0.15
    )
    
    # PE Multiple Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe if upside_pe else 0,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Multiple", 'font': {'size': 14, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 28, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA", 'font': {'size': 14, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': '#e2e8f0'}
    )
    return fig

def create_valuation_comparison_chart(vals):
    """Create professional bar chart comparing current vs fair values"""
    categories = []
    current_vals = []
    fair_vals = []
    
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_pe'])
    
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_ev'])
    
    if not categories:
        return None
    
    fig = go.Figure()
    
    # Current Price bars
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current_vals,
        marker=dict(
            color='#6366f1',
            line=dict(color='#818cf8', width=2),
        ),
        text=[f'₹{v:,.2f}' for v in current_vals],
        textposition='outside',
        textfont=dict(size=12, color='#e2e8f0', family='Inter')
    ))
    
    # Fair Value bars
    colors = ['#34d399' if fv > cv else '#f87171' for fv, cv in zip(fair_vals, current_vals)]
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair_vals,
        marker=dict(
            color=colors,
            line=dict(color=['#6ee7b7' if c == '#34d399' else '#fca5a5' for c in colors], width=2),
        ),
        text=[f'₹{v:,.2f}' for v in fair_vals],
        textposition='outside',
        textfont=dict(size=12, color='#e2e8f0', family='Inter')
    ))
    
    fig.update_layout(
        barmode='group',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=11, color='#e2e8f0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#e2e8f0')
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#4c1d95',
            tickfont=dict(size=11, color='#e2e8f0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(167, 139, 250, 0.2)',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=10, color='#a78bfa')
        ),
        margin=dict(l=40, r=30, t=40, b=30)
    )
    
    return fig

def create_52week_range_display(vals):
    """Create 52-week price range display using HTML/CSS"""
    low = vals.get('52w_low', 0)
    high = vals.get('52w_high', 0)
    current = vals.get('price', 0)
    
    if not all([low, high, current]) or high <= low:
        return None
    
    # Calculate position percentage
    position = ((current - low) / (high - low)) * 100
    position = max(0, min(100, position))  # Clamp between 0-100
    
    html = f'''
    <div class="range-container">
        <div class="range-labels">
            <span>52W Low: ₹{low:,.2f}</span>
            <span>52W High: ₹{high:,.2f}</span>
        </div>
        <div class="range-bar">
            <div class="range-indicator" style="left: {position}%;"></div>
        </div>
        <div class="range-info">
            Current Price: ₹{current:,.2f} ({position:.1f}% of range)
        </div>
    </div>
    '''
    return html

# ============================================================================
# PDF REPORT GENERATION
# ============================================================================
def create_pdf_report(company, ticker, sector, vals):
    """Generate professional PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=24, 
        textColor=colors.HexColor('#7c3aed'), 
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph("NYZTrade Comprehensive Analysis", title_style))
    story.append(Paragraph("Professional Stock Valuation Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Company Info
    story.append(Paragraph(f"{company}", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Calculate averages
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Fair Value Summary
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value', f"₹ {avg_fair:,.2f}"],
        ['Current Price', f"₹ {vals['price']:,.2f}"],
        ['Potential Upside', f"{avg_up:+.2f}%"]
    ]
    fair_table = Table(fair_data, colWidths=[3*inch, 2.5*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 25))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        spaceBefore=20
    )
    story.append(Paragraph(
        "DISCLAIMER: This report is for educational purposes only and does not constitute financial advice. "
        "Always consult a qualified financial advisor before making investment decisions.",
        disclaimer_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main():
    # ------------------------------------------------------------------
    # NAVIGATION / DEEP-LINK HANDLING (screener result -> valuation screen)
    # ------------------------------------------------------------------
    MODE_OPTIONS = [
        "🎯 Industry Screener",
        "📅 Earnings + Value Screener",
        "📰 News Sentiment Screener",
        "🧮 Manual Valuation",
        "📈 Individual Analysis",
        "📊 Industry Explorer"
    ]

    # Apply any pending navigation requested on the previous run
    if st.session_state.get("_pending_mode"):
        st.session_state["mode_select"] = st.session_state.pop("_pending_mode")

    # Handle ?mode=valuation&ticker=XXX deep links coming from the result tables
    _qp_ticker = _get_query_param("ticker")
    if _qp_ticker and st.session_state.get("_last_qp_ticker") != _qp_ticker:
        st.session_state["_last_qp_ticker"] = _qp_ticker
        st.session_state["deeplink_ticker"] = str(_qp_ticker).upper()
        st.session_state["input_method_radio"] = "✏️ Direct Ticker"
        st.session_state["auto_analyze"] = True
        st.session_state["mode_select"] = "📈 Individual Analysis"

    if "mode_select" not in st.session_state:
        st.session_state["mode_select"] = MODE_OPTIONS[0]

    # Header
    st.markdown(f'''
    <div class="main-header">
        <h1>🎯 NYZTrade Comprehensive Platform</h1>
        <h3>Professional Stock Analysis & Industry Screening</h3>
        <p>Advanced Valuation • {TOTAL_CATEGORIES} Industries • {TOTAL_STOCKS:,} Stock Universe</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Stats row
    st.markdown(f'''
    <div class="stats-container">
        <div class="stat-card">
            <h3>{TOTAL_CATEGORIES}</h3>
            <p>Industries</p>
        </div>
        <div class="stat-card">
            <h3>{TOTAL_STOCKS:,}</h3>
            <p>Stocks</p>
        </div>
        <div class="stat-card">
            <h3>6</h3>
            <p>Strategies</p>
        </div>
        <div class="stat-card">
            <h3>Live</h3>
            <p>Data</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔐 Account")
        st.markdown(f"**User:** {st.session_state.get('authenticated_user', 'Guest').title()}")
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔧 Analysis Mode")
        
        # Mode selection
        mode = st.selectbox(
            "Choose Mode",
            MODE_OPTIONS,
            key="mode_select"
        )

        with st.expander("🔗 Link Settings"):
            st.text_input(
                "App Base URL (optional)",
                key="app_base_url",
                placeholder="https://your-app.streamlit.app",
                help="Set this if the 'Valuation' links in the result tables should open "
                     "as full URLs (e.g. in a new tab). Leave blank to use relative links."
            )
    
    # Mode-specific content
    if mode == "🎯 Industry Screener":
        
        st.markdown("### 🎯 Industry-Based Stock Screener")
        
        # Industry selection with stock counts
        industries = sorted(get_all_categories())
        industry_options = []
        for industry in industries:
            stock_count = len(get_stocks_by_category(industry))
            industry_options.append(f"{industry} ({stock_count} stocks)")
        
        selected_industry_with_count = st.sidebar.selectbox("Select Industry", industry_options)
        selected_industry = selected_industry_with_count.split(" (")[0]  # Extract industry name
        
        # Strategy selection  
        strategy_options = [
            ("undervalued", "🎯 Undervalued Stocks (15%+ upside)"),
            ("undervalued_near_high", "🚀 Undervalued Near 52W High"),
            ("undervalued_supertrend", "📈 Undervalued + SuperTrend Bullish")
           
        ]
        
        strategy_choice = st.sidebar.selectbox(
            "Screening Strategy",
            strategy_options,
            format_func=lambda x: x[1]
        )
        
        strategy_type = strategy_choice[0]
        strategy_name = strategy_choice[1]
        
        # Parameters
        max_results = st.sidebar.slider("Max Results", 10, 100, 30)
        
        # Run screener
        if st.sidebar.button("🚀 Run Screener", type="primary"):
            
            # Show industry info
            industry_stocks = get_stocks_by_category(selected_industry)
            sector = get_sector_for_industry(selected_industry)
            
            st.markdown(f'''
            <div class="highlight-box">
                <h3>📊 {strategy_name}</h3>
                <p><strong>Industry:</strong> {selected_industry}</p>
                <p><strong>Sector:</strong> {sector}</p>
                <p><strong>Universe:</strong> {len(industry_stocks):,} stocks</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Run screener
            with st.spinner(f"🔍 Screening {len(industry_stocks):,} stocks..."):
                results_df = run_industry_screener(selected_industry, strategy_type, max_results)
            
            # Persist results so they survive reruns (needed for the valuation deep-link)
            st.session_state['screener_results'] = results_df
            st.session_state['screener_meta'] = {
                'industry': selected_industry,
                'strategy_type': strategy_type,
                'strategy_name': strategy_name
            }
        
        # ------------------------------------------------------------------
        # Render persisted screener results
        # ------------------------------------------------------------------
        results_df = st.session_state.get('screener_results')
        meta = st.session_state.get('screener_meta', {})
        
        if results_df is not None:
            _industry = meta.get('industry', selected_industry)
            _strategy_type = meta.get('strategy_type', strategy_type)
            _strategy_name = meta.get('strategy_name', strategy_name)
            
            if results_df.empty:
                st.warning(f"❌ No stocks found matching {_strategy_name} criteria in {_industry}")
            else:
                # Display results
                st.markdown(f'''
                <div class="success-message">
                    ✅ Found <strong>{len(results_df)}</strong> opportunities in {_industry}<br>
                    🎯 Strategy: {_strategy_name}
                </div>
                ''', unsafe_allow_html=True)
                
                # Sort results by upside
                results_df = results_df.sort_values('Upside %', ascending=False)
                
                # Format display
                display_df = results_df.copy()
                
                # Format currency columns
                for col in ['Price', 'Fair Value']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                # Format percentage columns
                for col in ['Upside %', 'ROE %', 'From 52W High %', 'From 52W Low %', 'Dividend Yield %']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else 'N/A')
                
                # Format ratio columns
                for col in ['PE Ratio', 'PB Ratio', 'Beta']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
                
                # Format volume columns (latest traded volume + relative volume)
                for col in ['Volume', 'Avg Volume']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(format_volume)
                if 'Rel Vol' in display_df.columns:
                    display_df['Rel Vol'] = display_df['Rel Vol'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A'
                    )
                
                # Format market cap
                if 'Market Cap' in display_df.columns:
                    display_df['Market Cap'] = display_df['Market Cap'].apply(
                        lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A'
                    )
                
                # Select key columns for display (now includes latest Volume + Valuation link)
                display_columns = ['Ticker', 'Name', 'Price', 'Fair Value', 'Upside %', 'PE Ratio',
                                   'Volume', 'Avg Volume', 'Rel Vol', 'From 52W High %', 'Cap Type', 'Valuation']
                display_columns = [c for c in display_columns if c in display_df.columns]
                
                # Display table
                st.dataframe(
                    display_df[display_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(500, len(display_df) * 35 + 100),
                    column_config=valuation_column_config()
                )
                
                # In-app jump to the valuation screen for any screened stock
                render_valuation_jump(results_df, "industry_screener")
                
                # Download CSV
                csv = results_df.to_csv(index=False)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"NYZTrade_{_industry.replace(' ', '_')}_{_strategy_type}_{timestamp}.csv"
                
                st.download_button(
                    f"📥 Download Results ({len(results_df)} stocks)",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
    
    elif mode == "📅 Earnings + Value Screener":
        
        st.markdown("### 📅 Earnings + Value Screener")
        st.caption("Undervalued stocks trading near their 52-week high, filtered by where "
                   "they sit in the earnings calendar. No breakout or momentum criteria.")
        
        # ---------------- Universe ----------------
        st.sidebar.markdown("### 🌐 Universe")
        universe_mode = st.sidebar.selectbox(
            "Source", ["Preset Watchlist", "By Industry", "Custom Tickers"]
        )
        
        universe = {}
        universe_label = ""
        
        if universe_mode == "Preset Watchlist":
            preset = st.sidebar.selectbox("Watchlist", list(BREAKOUT_PRESET_UNIVERSES.keys()))
            universe = {t: t.replace('.NS', '').replace('.BO', '') for t in BREAKOUT_PRESET_UNIVERSES[preset]}
            universe_label = preset
        
        elif universe_mode == "By Industry":
            ev_industries = sorted(get_all_categories())
            ev_options = [f"{ind} ({len(get_stocks_by_category(ind))} stocks)" for ind in ev_industries]
            ev_selected = st.sidebar.selectbox("Industry", ev_options)
            ev_industry = ev_selected.split(" (")[0]
            universe = dict(get_stocks_by_category(ev_industry))
            universe_label = ev_industry
            scan_cap = st.sidebar.slider("Max stocks to scan", 20, 600, 200, step=20)
            if len(universe) > scan_cap:
                universe = dict(list(universe.items())[:scan_cap])
        
        else:
            custom_input = st.sidebar.text_area(
                "Tickers (comma or newline separated)",
                placeholder="RELIANCE.NS, TCS.NS, HDFCBANK.NS",
                height=120
            )
            raw = [x.strip().upper() for x in custom_input.replace("\n", ",").split(",") if x.strip()]
            raw = [x if x.endswith(('.NS', '.BO')) else f"{x}.NS" for x in raw]
            universe = {t: t.replace('.NS', '').replace('.BO', '') for t in raw}
            universe_label = "Custom List"
        
        # ---------------- The three criteria ----------------
        st.sidebar.markdown("### 📈 52-Week High Proximity")
        near_high_pct = st.sidebar.slider(
            "Within % of 52W high", 0.5, 25.0, 5.0, 0.5,
            help="How close to the 52-week high the stock must be trading. "
                 "5% means the price is no more than 5% below its 52-week high."
        )
        
        st.sidebar.markdown("### 💰 Valuation")
        
        st.sidebar.checkbox(
            "Industry P/E = peer average", value=True, key="use_peer_pe",
            help="Replaces the static benchmark table with the mean trailing P/E "
                 "of the stocks in that industry. Stocks with no P/E are excluded, "
                 "not counted as zero. Applies to every screen in the app."
        )
        if st.session_state.get("use_peer_pe"):
            with st.sidebar.expander("Peer P/E settings"):
                st.number_input("Max stocks sampled", 10, 300, 60, 10,
                                key="peer_pe_sample",
                                help="First run costs one cached call per stock.")
                st.number_input("Ignore P/E above", 20.0, 1000.0, 200.0, 10.0,
                                key="peer_pe_cap",
                                help="One 900x outlier moves a 20-stock mean by "
                                     "45 points. Set very high to disable.")
                st.number_input("Min stocks required", 1, 20, 3, 1,
                                key="peer_pe_min_n",
                                help="Below this, the static benchmark is kept.")
        
        min_upside = st.sidebar.slider(
            "Min Upside % vs Fair Value", 0, 100, 15, 5,
            help="Fair value uses the same model as the Industry Screener, so the "
                 "numbers reconcile between the two screens."
        )
        
        st.sidebar.markdown("### 📅 Earnings Window")
        earnings_choice = st.sidebar.selectbox(
            "Earnings filter", list(EARNINGS_MODES.keys()), index=0
        )
        earnings_mode = EARNINGS_MODES[earnings_choice]
        
        reported_days = 30
        upcoming_days = 30
        if earnings_mode in ("reported", "either"):
            reported_days = st.sidebar.slider("Reported within last N days", 1, 90, 30, 1)
        if earnings_mode in ("upcoming", "either"):
            upcoming_days = st.sidebar.slider("Due within next N days", 1, 90, 30, 1)
        
        with st.sidebar.expander("🔎 Earnings date sources"):
            st.caption("Yahoo has no earnings dates for much of the NSE mid and "
                       "small cap universe. These fallbacks fill the gaps.")
            allow_estimate = st.checkbox(
                "Estimate from quarter end", value=True,
                help="When no announcement date exists, infer one from the most "
                     "recent reported quarter plus the SEBI filing deadline "
                     "(45 days, 60 for Q4). Always flagged as an estimate."
            )
            allow_nse = st.checkbox(
                "Try NSE board meetings", value=False,
                help="Queries the NSE board-meeting calendar. NSE blocks most "
                     "datacentre IPs, so this usually fails on Streamlit Cloud "
                     "and other hosted environments. Slow when it does work."
            )
            if allow_nse:
                st.caption("⚠️ Adds a per-stock web request. Expect it to fail "
                           "silently when hosted.")
        
        if earnings_mode == "upcoming":
            st.sidebar.warning(
                "⚠️ Holding into an earnings date means holding gap risk. A gap "
                "through your stop is an uncontrolled loss, not a controlled one."
            )
        
        st.sidebar.markdown("### 🎚️ Basic Filters")
        min_price = st.sidebar.number_input("Min Price (₹)", min_value=1.0, value=20.0, step=5.0)
        min_avg_volume = st.sidebar.number_input("Min Avg Daily Volume", min_value=0,
                                                 value=50000, step=10000)
        max_results = st.sidebar.slider("Max Results", 10, 100, 40, key="ev_max_results")
        max_valuation_calls = st.sidebar.slider(
            "Max stocks to value", 25, 300, 150, 25,
            help="Caps the per-ticker work after the 52-week high filter. Lower is faster."
        )
        final_rank = st.sidebar.selectbox(
            "Rank results by",
            ["Upside %", "Closest to 52W High", "Earnings Soonest", "Best Surprise"]
        )
        
        with st.expander("📐 How this screen works, and what the two earnings windows mean"):
            st.markdown("""
Three filters, applied in this order so the expensive calls only touch survivors:

1. **Near the 52-week high** — from daily bars, batched. Breakouts into blue sky
   have better follow-through than breakouts in the middle of a range.
2. **Undervalued** — price below the fair value estimate, same model the Industry
   Screener uses.
3. **Earnings window** — where the stock sits in its reporting cycle.

**These two earnings windows are opposite trades, and it matters which you pick.**

*Reported in the last N days* is **post-earnings announcement drift** — a documented
tendency for price to keep moving in the direction of an earnings surprise for weeks
afterwards. The event risk is behind you and the surprise is known, which is why the
**Last Surprise** column matters most in this mode: drift follows the beats.

*Due in the next N days* is the **run-up** trade, and it carries the risk I would
normally tell you to screen out. You are holding through a binary event. A gap
against you passes straight through a stop. If you run this mode, size for the gap
rather than for the stop.

Combining "undervalued" with "near 52-week high" is deliberately contrarian — most
stocks near highs are not cheap. Expect few results, and treat a large `Upside %`
on a stock at its high with suspicion: check whether the fair value is being driven
by a single depressed input like a trailing EPS that has since recovered.
            """)
        
        if st.session_state.get("use_peer_pe") and universe_mode == "By Industry" and universe_label:
            _peer = compute_peer_industry_pe(
                universe_label,
                max_sample=int(st.session_state.get("peer_pe_sample", 60)),
                pe_cap=float(st.session_state.get("peer_pe_cap", 200.0))
            )
            if _peer and _peer.get('n', 0) > 0:
                _static = None
                try:
                    _static = INDUSTRY_BENCHMARKS.get(universe_label, {}).get('pe')
                except Exception:
                    pass
                pc1, pc2, pc3, pc4 = st.columns(4)
                pc1.metric("Peer P/E (mean)", f"{_peer['mean']:.2f}")
                pc2.metric("Peer P/E (median)", f"{_peer['median']:.2f}")
                pc3.metric("Stocks with P/E", f"{_peer['n']} / {_peer['sample_size']}")
                pc4.metric("Static table P/E", f"{_static:.2f}" if _static else "N/A")
                st.caption(
                    f"Excluded — no P/E: {_peer['excluded_missing']} · "
                    f"loss-making or negative: {_peer['excluded_negative']} · "
                    f"above cap: {_peer['excluded_outlier']}. "
                    f"The mean of the {_peer['n']} available P/Es is what the fair "
                    f"value model uses."
                )
                if _peer['median'] and abs(_peer['mean'] - _peer['median']) > 0.35 * _peer['median']:
                    st.warning(
                        f"⚠️ Mean ({_peer['mean']:.1f}) and median ({_peer['median']:.1f}) "
                        f"diverge sharply, so the average is being pulled by a few "
                        f"high-P/E names. Consider lowering the 'Ignore P/E above' cap."
                    )
        
        if st.sidebar.button("🔍 Run Screen", type="primary"):
            if not universe:
                st.warning("❌ No tickers in the selected universe.")
            else:
                st.markdown(f'''
                <div class="highlight-box">
                    <h3>📅 {earnings_choice}</h3>
                    <p><strong>Universe:</strong> {universe_label} ({len(universe):,} stocks)</p>
                    <p><strong>Within:</strong> {near_high_pct:.1f}% of 52W high &nbsp;•&nbsp;
                       <strong>Min Upside:</strong> {min_upside}%</p>
                </div>
                ''', unsafe_allow_html=True)
                
                with st.spinner(f"🔍 Screening {len(universe):,} stocks..."):
                    ev_df, ev_funnel = run_earnings_value_screener(
                        universe=universe,
                        near_high_pct=near_high_pct,
                        min_upside=min_upside,
                        earnings_mode=earnings_mode,
                        upcoming_days=upcoming_days,
                        reported_days=reported_days,
                        min_price=min_price,
                        min_avg_volume=min_avg_volume,
                        max_results=max_results,
                        max_valuation_calls=max_valuation_calls,
                        final_rank=final_rank,
                        allow_nse=allow_nse,
                        allow_estimate=allow_estimate
                    )
                
                st.session_state['ev_results'] = ev_df
                st.session_state['ev_funnel'] = ev_funnel
                st.session_state['ev_meta'] = {
                    'universe_label': universe_label,
                    'earnings_choice': earnings_choice,
                    'near_high_pct': near_high_pct,
                    'min_upside': min_upside
                }
        
        # ---------------- Render results ----------------
        ev_df = st.session_state.get('ev_results')
        ev_meta = st.session_state.get('ev_meta', {})
        ev_funnel = st.session_state.get('ev_funnel', {})
        
        if ev_df is not None:
            if ev_funnel:
                st.markdown("##### 🔻 Funnel")
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Scanned", ev_funnel.get('scanned', 0))
                c2.metric("Had Data", ev_funnel.get('with_data', 0))
                c3.metric("Near 52W High", ev_funnel.get('near_high', 0))
                c4.metric("Undervalued", ev_funnel.get('undervalued', 0))
                c5.metric("Earnings Match", ev_funnel.get('earnings_ok', 0))
            
            if ev_df.empty:
                st.warning(
                    "❌ Nothing passed all three filters. The binding constraint is usually "
                    "the combination of *undervalued* and *near the 52-week high* — those two "
                    "pull against each other. Widen the 52-week band, lower the minimum "
                    "upside, or check the funnel above to see which stage emptied out."
                )
            else:
                st.markdown(f'''
                <div class="success-message">
                    ✅ <strong>{len(ev_df)}</strong> undervalued stocks near their 52-week high<br>
                    📅 {ev_meta.get('earnings_choice', earnings_choice)}<br>
                    🌐 Universe: {ev_meta.get('universe_label', universe_label)}
                </div>
                ''', unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Results", len(ev_df))
                m2.metric("Avg Upside",
                          f"{ev_df['Upside %'].mean():+.1f}%"
                          if 'Upside %' in ev_df.columns and ev_df['Upside %'].notna().any() else "N/A")
                m3.metric("Avg From High",
                          f"{ev_df['From High %'].mean():.2f}%"
                          if 'From High %' in ev_df.columns and ev_df['From High %'].notna().any() else "N/A")
                if 'Surprise %' in ev_df.columns and ev_df['Surprise %'].notna().any():
                    m4.metric("Beats", int((ev_df['Surprise %'] > 0).sum()))
                else:
                    m4.metric("Beats", "N/A")
                
                ev_display = ev_df.copy()
                
                for col in ['LTP', '52W High', 'Fair Value']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                
                for col in ['Chg %', 'From High %', 'Upside %', 'From Low %']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"{x:+.2f}%" if pd.notna(x) else 'N/A')
                
                for col in ['Volume', 'Avg Volume']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(format_volume)
                if 'Rel Vol' in ev_display.columns:
                    ev_display['Rel Vol'] = ev_display['Rel Vol'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                if 'PE Ratio' in ev_display.columns:
                    ev_display['PE Ratio'] = ev_display['PE Ratio'].apply(
                        lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                if 'Market Cap' in ev_display.columns:
                    ev_display['Market Cap'] = ev_display['Market Cap'].apply(
                        lambda x: f"₹{x/10000000:,.0f}Cr" if pd.notna(x) else 'N/A')
                for col in ['Days To', 'Days Since']:
                    if col in ev_display.columns:
                        ev_display[col] = ev_display[col].apply(
                            lambda x: f"{int(x)}d" if pd.notna(x) else 'N/A')
                
                ev_columns = ['Ticker', 'Name', 'LTP', 'From High %', '52W High',
                              'Fair Value', 'Upside %', 'Value Tag', 'FV Source',
                              'Earnings', 'Date Source', 'Last Earnings', 'Days Since',
                              'Last Surprise', 'Next Earnings', 'Days To',
                              'Volume', 'Avg Volume', 'Rel Vol', 'Chg %',
                              'PE Ratio', 'Cap Type', 'As Of', 'Valuation']
                ev_columns = [c for c in ev_columns if c in ev_display.columns]
                
                st.dataframe(
                    ev_display[ev_columns],
                    use_container_width=True,
                    hide_index=True,
                    height=min(600, len(ev_display) * 35 + 100),
                    column_config=valuation_column_config()
                )
                
                render_valuation_jump(ev_df, "earnings_value")
                
                render_manual_fair_value('ev_results', key_prefix="ev_mfv")
                
                with st.expander("📅 Earnings detail"):
                    st.caption("A positive last surprise is what post-earnings drift follows. "
                               "An upcoming date inside your intended holding period is gap risk.")
                    e_cols = ['Ticker', 'Date Source', 'Estimated', 'Last Earnings',
                              'Days Since', 'Last Surprise', 'Next Earnings', 'Days To',
                              'Upside %', 'From High %']
                    e_cols = [c for c in e_cols if c in ev_df.columns]
                    st.dataframe(ev_df[e_cols], use_container_width=True, hide_index=True)
                
                ev_csv = ev_df.to_csv(index=False)
                ev_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    f"📥 Download Results ({len(ev_df)} stocks)",
                    data=ev_csv,
                    file_name=f"NYZTrade_EarningsValue_{ev_ts}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    

    elif mode == "📰 News Sentiment Screener":

        st.markdown("### 📰 News Sentiment Industry Screener")
        st.caption("Finds which industries the news flow is turning positive on, "
                   "then confirms it against price momentum to surface swing-trade candidates.")

        st.sidebar.markdown("### 📰 Sentiment Settings")

        all_inds = sorted(get_all_categories())

        scope = st.sidebar.radio(
            "🌐 Scope",
            ["Quick Scan (popular industries)", "Choose Industries", "All Industries (slow)"]
        )

        POPULAR = [
            "Banks - Regional", "Money Center Banks", "Credit Services",
            "Information Technology Services", "Software - Application",
            "Drug Manufacturers - Major", "Auto Manufacturers - Major",
            "Steel & Iron", "Cement", "Chemicals - Major Diversified",
            "Electric Utilities", "Oil & Gas Refining & Marketing",
            "Aerospace/Defense - Major Diversified", "Textile - Apparel Clothing",
            "Packaged Foods", "Real Estate Development",
        ]

        if scope == "Quick Scan (popular industries)":
            chosen = [i for i in POPULAR if i in all_inds]
            if not chosen:
                chosen = all_inds[:15]
            st.sidebar.caption(f"Scanning {len(chosen)} industries")
        elif scope == "Choose Industries":
            chosen = st.sidebar.multiselect(
                "Select Industries",
                all_inds,
                default=all_inds[:8],
                help="Each industry costs a few seconds — 5 to 20 is a comfortable range"
            )
        else:
            chosen = all_inds
            st.sidebar.warning(
                f"⚠️ {len(all_inds)} industries selected. This makes a lot of news "
                f"requests and can take several minutes — and may hit Yahoo rate limits."
            )

        stocks_per_industry = st.sidebar.slider(
            "Stocks sampled per industry", 2, 15, 5,
            help="More stocks = more reliable industry read, but a slower scan"
        )
        lookback_days = st.sidebar.slider("News lookback (days)", 1, 21, 7)
        max_articles = st.sidebar.slider("Max articles per stock", 3, 20, 8)
        half_life = st.sidebar.slider(
            "Recency half-life (hours)", 6, 168, 48, step=6,
            help="How fast old news loses weight. At 48h, a 2-day-old headline "
                 "counts half as much as one published now."
        )

        st.sidebar.markdown("---")
        min_articles = st.sidebar.slider(
            "Min articles to rank an industry", 0, 20, 3,
            help="Industries with less coverage than this are shown but flagged as thin"
        )
        max_workers = st.sidebar.slider(
            "Parallel requests", 1, 12, 6,
            help="Lower this if you start seeing empty news results (rate limiting)"
        )

        est = len(chosen) * stocks_per_industry
        st.info(f"📊 Scan plan: **{len(chosen)} industries** × {stocks_per_industry} stocks "
                f"= **~{est} news lookups**. Roughly {max(1, est // 15)}–{max(1, est // 6)} "
                f"seconds. Results cache for 30 minutes.")

        with st.expander("🧠 How the sentiment engine works"):
            st.markdown("""
**Financial lexicon, not generic sentiment.** General-purpose models misread market
language badly — *"cuts guidance"* is severely negative but contains no ordinarily
negative word, and *"aggressive expansion"* is positive despite *aggressive* scoring
negative in social-media lexicons. The engine uses a domain lexicon of ~500 finance
terms plus ~250 multi-word phrases scored for market impact.

**Phrases beat single words.** *"beats estimates"*, *"profit warning"*, *"USFDA warning"*,
*"promoter pledge"* are matched as units and consume their tokens, so they can't be
double-counted by the word-level pass.

**Negation and intensity are handled.** *"fails to beat estimates"* flips polarity;
*"declines sharply"* scores harder than *"declines slightly"*.

**Recency decay.** Each article is weighted by an exponential half-life, so stale news
fades. An industry whose only coverage is 5 days old gets pulled toward neutral rather
than ranked on it.

**Noise filtering.** Round-ups like *"Stocks to watch"* and *"Top gainers and losers"*
are dropped — they mention many companies and carry no company-specific signal.

---

**Swing Score (0–100)** deliberately does *not* rank on sentiment alone, because
sentiment alone is a weak and noisy predictor. Roughly half the weight is news and
half is price confirmation:

| Component | Weight | Rationale |
|---|---|---|
| News sentiment | 35 | Recency-weighted, article-count-weighted |
| Breadth | 15 | Share of sampled stocks with positive news — one stock's story isn't a sector trend |
| Price momentum | 30 | 5-day and 20-day returns; sentiment with no price response is just talk |
| Trend participation | 10 | Share of stocks above their 20-day SMA |
| Volume confirmation | 10 | Recent volume vs 20-day average |

Thin coverage (under 3 articles) and stale news both scale the score down.
            """)

        if st.sidebar.button("📰 Run Sentiment Scan", type="primary"):
            if not chosen:
                st.warning("❌ Select at least one industry.")
            else:
                with st.spinner(f"📰 Analysing news across {len(chosen)} industries..."):
                    ind_df, stock_df = run_sentiment_industry_screener(
                        selected_industries=chosen,
                        stocks_per_industry=stocks_per_industry,
                        lookback_days=lookback_days,
                        max_articles=max_articles,
                        half_life_hours=float(half_life),
                        max_workers=max_workers
                    )
                st.session_state['sent_ind_df'] = ind_df
                st.session_state['sent_stock_df'] = stock_df
                st.session_state['sent_min_articles'] = min_articles

        ind_df = st.session_state.get('sent_ind_df')
        stock_df = st.session_state.get('sent_stock_df')

        if ind_df is not None:
            if ind_df.empty:
                st.warning("❌ No results. The news source may be unreachable, or the "
                           "selected industries have no covered stocks.")
            else:
                min_art = st.session_state.get('sent_min_articles', 3)
                total_art = int(ind_df['Articles'].sum())

                if total_art == 0:
                    st.error(
                        "⚠️ **No news articles were retrieved at all.** The scan ran, but "
                        "every news request came back empty. This usually means Yahoo "
                        "Finance is rate-limiting or its news endpoint has changed. "
                        "The momentum columns below are still valid; the sentiment "
                        "columns are not. Try again in a few minutes, or lower "
                        "'Parallel requests'."
                    )

                hot = ind_df[ind_df['Swing Score'] >= 62]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Industries Scanned", len(ind_df))
                m2.metric("Articles Analysed", total_art)
                m3.metric("Trending Up", len(hot))
                m4.metric("Avg Sentiment", f"{ind_df['Sentiment'].mean():+.3f}")

                st.markdown("#### 🏆 Industry Rankings")

                disp = ind_df.copy()
                thin = disp['Articles'] < min_art
                disp['Industry'] = disp.apply(
                    lambda r: f"{r['Industry']} ⚠️" if r['Articles'] < min_art else r['Industry'],
                    axis=1
                )
                disp['Swing Score'] = disp['Swing Score'].apply(lambda x: f"{x:.1f}")
                disp['Sentiment'] = disp['Sentiment'].apply(lambda x: f"{x:+.3f}")
                for c in ['Breadth %', 'Above SMA20 %']:
                    disp[c] = disp[c].apply(lambda x: f"{x:.0f}%")
                for c in ['Avg 5D %', 'Avg 20D %']:
                    disp[c] = disp[c].apply(lambda x: f"{x:+.2f}%")
                disp['Vol Ratio'] = disp['Vol Ratio'].apply(lambda x: f"{x:.2f}x")
                disp['Freshness'] = disp['Freshness'].apply(
                    lambda x: f"{x*100:.0f}%" if pd.notna(x) else 'N/A')

                cols = ['Industry', 'Swing Score', 'Trend', 'Sentiment', 'Mood',
                        'Breadth %', 'Articles', 'Freshness', 'Avg 5D %', 'Avg 20D %',
                        'Above SMA20 %', 'Vol Ratio', 'Stocks']
                cols = [c for c in cols if c in disp.columns]

                st.dataframe(disp[cols], use_container_width=True, hide_index=True,
                             height=min(560, len(disp) * 35 + 100))

                if thin.any():
                    st.caption(f"⚠️ marks industries with fewer than {min_art} articles — "
                               "treat their sentiment as unreliable.")

                # ---- Drill-down ------------------------------------------------
                st.markdown("---")
                st.markdown("#### 🔎 Drill Into an Industry")

                pick = st.selectbox(
                    "Industry",
                    ind_df['Industry'].tolist(),
                    key="sent_drill_pick"
                )

                if stock_df is not None and not stock_df.empty:
                    sub = stock_df[stock_df['Industry'] == pick].copy()

                    if sub.empty:
                        st.info("No stocks recorded for this industry.")
                    else:
                        sd = sub.copy()
                        sd['Sentiment'] = sd['Sentiment'].apply(
                            lambda x: f"{x:+.3f}" if pd.notna(x) else 'No News')
                        sd['Price'] = sd['Price'].apply(
                            lambda x: f"₹{x:,.2f}" if pd.notna(x) else 'N/A')
                        for c in ['Ret 5D %', 'Ret 20D %']:
                            sd[c] = sd[c].apply(
                                lambda x: f"{x:+.2f}%" if pd.notna(x) else 'N/A')
                        sd['Vol Ratio'] = sd['Vol Ratio'].apply(
                            lambda x: f"{x:.2f}x" if pd.notna(x) else 'N/A')
                        sd['Newest (h)'] = sd['Newest (h)'].apply(
                            lambda x: f"{x:.0f}h ago" if pd.notna(x) else 'N/A')

                        scols = ['Ticker', 'Name', 'Sentiment', 'Mood', 'Articles',
                                 'Positive', 'Negative', 'Newest (h)', 'Price',
                                 'Ret 5D %', 'Ret 20D %', 'Vol Ratio', 'Valuation']
                        scols = [c for c in scols if c in sd.columns]

                        st.dataframe(sd[scols], use_container_width=True, hide_index=True,
                                     column_config=valuation_column_config())

                        render_valuation_jump(sub, "sentiment_screener")

                        # ---- Headlines --------------------------------------
                        st.markdown("##### 📄 Headlines Driving This Score")
                        shown = 0
                        for _, r in sub.iterrows():
                            arts = r.get('_articles') or []
                            if not arts:
                                continue
                            shown += 1
                            with st.expander(
                                f"{r['Ticker']} — {r['Name']}  "
                                f"({r['Articles']} articles, {r['Mood']})"
                            ):
                                for a in arts:
                                    s = a['score']
                                    icon = "🟢" if s > 0.12 else ("🔴" if s < -0.12 else "⚪")
                                    age = (f"{a['age_hours']:.0f}h ago"
                                           if a.get('age_hours') is not None else "undated")
                                    title = a['title']
                                    if a.get('link'):
                                        st.markdown(f"{icon} **[{title}]({a['link']})**")
                                    else:
                                        st.markdown(f"{icon} **{title}**")
                                    meta = f"`{s:+.3f}` · {age}"
                                    if a.get('publisher'):
                                        meta += f" · {a['publisher']}"
                                    if a.get('drivers'):
                                        meta += f" · triggers: _{a['drivers']}_"
                                    st.caption(meta)
                        if shown == 0:
                            st.info("No headlines were retrieved for the stocks in this industry.")

                # ---- Downloads --------------------------------------------------
                st.markdown("---")
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        f"📥 Industry Rankings ({len(ind_df)})",
                        data=ind_df.to_csv(index=False),
                        file_name=f"NYZTrade_Sentiment_Industries_{ts}.csv",
                        mime="text/csv", use_container_width=True
                    )
                with d2:
                    if stock_df is not None and not stock_df.empty:
                        st.download_button(
                            f"📥 Stock Detail ({len(stock_df)})",
                            data=stock_df.drop(columns=['_articles'], errors='ignore').to_csv(index=False),
                            file_name=f"NYZTrade_Sentiment_Stocks_{ts}.csv",
                            mime="text/csv", use_container_width=True
                        )


    elif mode == "🧮 Manual Valuation":

        st.markdown("### 🧮 Manual Valuation Dashboard")
        st.caption("Enter per-share figures, then value the stock seven ways off the "
                   "pre-fed industry multiples.")

        # ------------------------------------------------------------------
        # Widget defaults are seeded into session_state ONCE, and the widgets
        # below are created with key= only (no value=). This is deliberate:
        # when a widget has a key that already exists in session_state,
        # Streamlit uses the stored value and ignores value=. Seeding first
        # and letting prefill write straight to the widget keys is what makes
        # the prefill buttons actually move the fields.
        # ------------------------------------------------------------------
        _MV_DEFAULTS = {
            'mv_price_in': 0.0, 'mv_shares_in': 0.0, 'mv_eps_in': 0.0,
            'mv_fwd_eps_in': 0.0, 'mv_bvps_in': 0.0, 'mv_dps_in': 0.0,
        }
        for _k, _v in _MV_DEFAULTS.items():
            st.session_state.setdefault(_k, _v)

        # ------------------------------------------------------------------
        # STEP 1 — pick the stock
        # ------------------------------------------------------------------
        st.markdown("#### 1️⃣ Select Stock")

        pick_mode = st.radio(
            "How do you want to choose the stock?",
            ["🔍 Search the database", "✏️ Type a ticker", "🖊️ Fully manual (no ticker)"],
            horizontal=True, key="mv_pick_mode"
        )

        mv_ticker = ""
        db_hit = None

        if pick_mode == "🔍 Search the database":
            sc1, sc2 = st.columns([1, 2])
            with sc1:
                q = st.text_input("Search name or ticker", placeholder="e.g. reliance, tcs, bank",
                                  key="mv_db_query").strip()
            with sc2:
                if q and len(q) >= 2:
                    matches = search_stocks_by_name(q, max_results=200)
                    if matches:
                        labels = [f"{m['ticker']} — {m['name']}  ·  {m['industry']}"
                                  for m in matches]
                        chosen_lbl = st.selectbox(f"{len(matches)} match(es) in the database",
                                                  labels, key="mv_db_pick")
                        idx = labels.index(chosen_lbl)
                        db_hit = matches[idx]
                        mv_ticker = db_hit['ticker']
                    else:
                        st.info(f"No stock in the database matches “{q}”. "
                                "Use *Type a ticker* if it isn't listed.")
                else:
                    st.caption("Type at least 2 characters to search "
                               f"the {TOTAL_STOCKS:,}-stock database.")

        elif pick_mode == "✏️ Type a ticker":
            mv_ticker = st.text_input("Ticker", placeholder="e.g. RELIANCE.NS",
                                      key="mv_ticker_typed").strip().upper()
            if mv_ticker:
                db_hit = get_stock_info(mv_ticker)
                if db_hit:
                    st.success(f"✅ Found in database: **{db_hit['name']}** "
                               f"· {db_hit['category']}")
                else:
                    st.info("Not in the database — you can still value it, but the "
                            "industry has to be picked manually below.")

        # ---- Industry + cap (auto-matched from the database when possible) ----
        industries = ["— none / use sector default —"] + sorted(get_all_categories())

        if db_hit and db_hit.get('category' if 'category' in db_hit else 'industry'):
            matched = db_hit.get('category') or db_hit.get('industry')
            if matched in industries and st.session_state.get('mv_last_match') != matched:
                st.session_state['mv_industry'] = matched
                st.session_state['mv_last_match'] = matched

        ic1, ic2 = st.columns([3, 1])
        with ic1:
            mv_industry = st.selectbox("Industry (drives the benchmark multiples)",
                                       industries, key="mv_industry")
        with ic2:
            mv_cap = st.selectbox("Cap", ["Large", "Mid", "Small"], key="mv_cap")

        # ---- Prefill ---------------------------------------------------------
        if pick_mode != "🖊️ Fully manual (no ticker)":
            p1, p2 = st.columns([1, 3])
            with p1:
                do_prefill = st.button("⬇️ Prefill financials",
                                       use_container_width=True,
                                       disabled=not mv_ticker)
            with p2:
                if mv_ticker:
                    st.caption(f"Pulls live figures for **{mv_ticker}** as a starting "
                               "point. Every field stays editable afterwards.")
                else:
                    st.caption("Pick a stock above to enable prefill.")

            if do_prefill and mv_ticker:
                with st.spinner(f"Fetching {mv_ticker}..."):
                    try:
                        f = get_stock_fundamentals(mv_ticker)
                    except Exception:
                        f = None
                if not f:
                    st.warning(f"Could not fetch {mv_ticker}. Enter the figures manually.")
                else:
                    # Write to the WIDGET keys so the inputs visibly update
                    st.session_state['mv_price_in'] = float(f.get('price') or 0.0)
                    st.session_state['mv_eps_in'] = float(f.get('trailing_eps') or 0.0)
                    st.session_state['mv_bvps_in'] = float(f.get('book_value') or 0.0)

                    try:
                        if f.get('market_cap') and f.get('price'):
                            st.session_state['mv_shares_in'] = round(
                                (f['market_cap'] / f['price']) / 1e7, 2)
                    except Exception:
                        pass

                    # Forward EPS implied by the forward P/E, when both are sane
                    try:
                        fpe, price = f.get('forward_pe'), f.get('price')
                        if fpe and price and 0 < fpe < 200:
                            st.session_state['mv_fwd_eps_in'] = round(price / fpe, 2)
                    except Exception:
                        pass

                    # Dividend per share from the yield
                    try:
                        dy, price = f.get('dividend_yield'), f.get('price')
                        if dy and price:
                            # yfinance has shipped this as both a fraction and a
                            # percentage; normalise so 2% never becomes 200%.
                            dyf = dy if dy < 1 else dy / 100.0
                            st.session_state['mv_dps_in'] = round(price * dyf, 2)
                    except Exception:
                        pass

                    st.session_state['mv_prefill_note'] = (
                        f"Prefilled from {f.get('name', mv_ticker)}")
                    st.session_state.pop('mv_result', None)
                    st.rerun()

        if st.session_state.get('mv_prefill_note'):
            st.success(f"✅ {st.session_state.pop('mv_prefill_note')} — adjust anything below.")

        # A system result belongs to one ticker; drop it when the selection moves.
        _sysr = st.session_state.get('mv_system')
        if _sysr and _sysr.get('ticker') and _sysr.get('ticker') != mv_ticker:
            st.session_state.pop('mv_system', None)

        # ---- Benchmarks ------------------------------------------------------
        ind_key = None if mv_industry.startswith("—") else mv_industry
        try:
            bench = get_industry_benchmarks(ind_key or 'Other', mv_cap)
        except Exception:
            bench = {'pe': 18.0, 'pb': 2.5, 'ev_ebitda': 12.0, 'roe': 15.0}

        bsrc = "peer average" if bench.get('pe_source') == 'peer' else "pre-fed benchmark"
        st.info(f"📚 **{ind_key or 'Sector default'}** ({mv_cap} cap) — "
                f"P/E **{bench.get('pe', 0):.1f}** · P/B **{bench.get('pb', 0):.1f}** · "
                f"Target ROE **{bench.get('roe', 0):.1f}%**  ·  source: {bsrc}")

        # ------------------------------------------------------------------
        # STEP 2 — Price & Earnings inputs
        # ------------------------------------------------------------------
        st.markdown("#### 2️⃣ Price & Earnings")
        st.caption("All per-share figures in **₹**; share count in **Crore shares**.")

        a1, a2, a3 = st.columns(3)
        with a1:
            mv_price = st.number_input("Current Price (₹)", min_value=0.0, step=1.0,
                                       format="%.2f", key="mv_price_in")
            mv_shares = st.number_input("Shares Outstanding (Cr)", min_value=0.0, step=1.0,
                                        format="%.2f", key="mv_shares_in",
                                        help="Optional — used only to show market cap")
        with a2:
            mv_eps = st.number_input("Reported EPS — TTM (₹)", step=0.5, format="%.2f",
                                     key="mv_eps_in",
                                     help="Actual trailing twelve month EPS")
            mv_fwd_eps = st.number_input("Estimated EPS — forward (₹)", step=0.5,
                                         format="%.2f", key="mv_fwd_eps_in",
                                         help="Your own or consensus forward EPS")
        with a3:
            mv_bvps = st.number_input("Book Value / share (₹)", min_value=0.0, step=1.0,
                                      format="%.2f", key="mv_bvps_in")
            mv_dps = st.number_input("Dividend / share (₹)", min_value=0.0, step=0.5,
                                     format="%.2f", key="mv_dps_in")

        # Derived context
        eps_growth = None
        if mv_eps and mv_fwd_eps and mv_eps > 0:
            eps_growth = (mv_fwd_eps / mv_eps - 1) * 100

        k1, k2, k3 = st.columns(3)
        if mv_price and mv_shares:
            k1.metric("Market Cap", f"₹{mv_price * mv_shares:,.0f} Cr")
        else:
            k1.metric("Market Cap", "—")
        k2.metric("Implied EPS growth",
                  f"{eps_growth:+.1f}%" if eps_growth is not None else "—",
                  help="Reported EPS to forward EPS. Also drives the PEG method.")
        k3.metric("Dividend Yield",
                  f"{mv_dps / mv_price * 100:.2f}%" if (mv_price and mv_dps) else "—")

        # ------------------------------------------------------------------
        # STEP 3 — Target multiples & assumptions
        # ------------------------------------------------------------------
        st.markdown("#### 3️⃣ Target Multiples & Assumptions")
        st.caption("Prefilled from the industry benchmarks above. Override freely.")

        h1, h2, h3, h4 = st.columns(4)
        with h1:
            t_pe = st.number_input("Target P/E", min_value=0.0,
                                   value=float(round(bench.get('pe', 18.0), 1)),
                                   step=0.5, format="%.1f", key="mv_t_pe")
        with h2:
            t_fwd_pe = st.number_input("Forward P/E", min_value=0.0,
                                       value=float(round(bench.get('pe', 18.0) * 0.95, 1)),
                                       step=0.5, format="%.1f", key="mv_t_fpe",
                                       help="Usually a touch below trailing when "
                                            "earnings are growing")
        with h3:
            t_pb = st.number_input("Target P/B", min_value=0.0,
                                   value=float(round(bench.get('pb', 2.5), 2)),
                                   step=0.1, format="%.2f", key="mv_t_pb")
        with h4:
            t_peg = st.number_input("Target PEG", min_value=0.0, value=1.0, step=0.1,
                                    format="%.2f", key="mv_t_peg",
                                    help="PEG of 1 means paying a P/E equal to "
                                         "the growth rate")

        j1, j2, j3 = st.columns(3)
        with j1:
            mv_disc = st.number_input("Required Return (%)", min_value=0.1, value=13.0,
                                      step=0.5, format="%.2f", key="mv_disc_in",
                                      help="Used by Earnings Power and the Dividend "
                                           "Discount model. 12–15% is a common range "
                                           "for Indian equities.")
        with j2:
            mv_div_g = st.number_input("Dividend Growth (%)", value=5.0, step=0.5,
                                       format="%.2f", key="mv_div_g_in",
                                       help="Must stay below the required return")
        with j3:
            mos = st.slider("Margin of Safety (%)", 0, 50, 15, 5, key="mv_mos",
                            help="Discount applied to the blended fair value")

        if mv_div_g >= mv_disc:
            st.warning("⚠️ Dividend growth must be below the required return, or the "
                       "Gordon growth formula diverges. The Dividend Discount method "
                       "will be skipped.")

        # ------------------------------------------------------------------
        # STEP 4 — Calculate
        # ------------------------------------------------------------------
        st.markdown("#### 4️⃣ Calculate")

        # Snapshot of everything the valuation depends on, so we can tell the
        # user when the on-screen result no longer matches the inputs.
        current_sig = (mv_price, mv_eps, mv_fwd_eps, mv_bvps, mv_dps,
                       t_pe, t_fwd_pe, t_pb, t_peg, mv_disc, mv_div_g,
                       ind_key, mv_cap)

        cb1, cb2, cb3 = st.columns([1, 1, 2])
        with cb1:
            calc_clicked = st.button("🧮 Calculate Fair Value", type="primary",
                                     use_container_width=True)
        with cb2:
            sys_clicked = st.button("🤖 System Valuation", use_container_width=True,
                                    disabled=not mv_ticker,
                                    help=("Runs the app's own model on this ticker — "
                                          "the same engine the screeners use — so you "
                                          "can compare it against your own numbers.")
                                         if mv_ticker else
                                         "Pick a stock from the database to enable this")
        with cb3:
            stored = st.session_state.get('mv_result')
            if stored and stored.get('sig') != current_sig:
                st.warning("⚠️ Inputs have changed since the last calculation — "
                           "press Calculate to refresh.")
            elif not stored:
                st.caption("Fill in a price plus either an EPS or a book value, "
                           "then press Calculate.")

        if sys_clicked and mv_ticker:
            with st.spinner(f"Running the system model on {mv_ticker}..."):
                s_vals, s_fund, s_info, s_err = compute_system_valuation(mv_ticker)
            if s_err or not s_vals:
                st.session_state['mv_system'] = {'error': s_err or "Model returned nothing"}
            else:
                s_fairs = [v for v in [s_vals.get('fair_value_pe'),
                                       s_vals.get('fair_value_ev')] if v]
                s_ups = [v for v in [s_vals.get('upside_pe'),
                                     s_vals.get('upside_ev')] if v is not None]
                st.session_state['mv_system'] = {
                    'error': None,
                    'vals': s_vals,
                    'ticker': mv_ticker,
                    'company': (s_info or {}).get('longName', mv_ticker),
                    'sector': (s_info or {}).get('sector', 'N/A'),
                    'industry': (s_info or {}).get('industry', 'N/A'),
                    'fair_value': float(np.mean(s_fairs)) if s_fairs else None,
                    'upside': float(np.mean(s_ups)) if s_ups else None,
                }
            st.rerun()

        if calc_clicked:
            ddm_ok = mv_div_g < mv_disc
            methods = {
                "P/E (reported EPS)":     fv_pe(mv_eps, t_pe),
                "Forward P/E (est. EPS)": fv_forward_pe(mv_fwd_eps, t_fwd_pe),
                "P/B":                    fv_pb(mv_bvps, t_pb),
                "PEG-implied P/E":        fv_peg(mv_eps, eps_growth, t_peg),
                "Graham Number":          fv_graham(mv_eps, mv_bvps),
                "Earnings Power":         fv_earnings_power(mv_eps, mv_disc),
                "Dividend Discount":      (fv_ddm(mv_dps, mv_disc, mv_div_g)
                                           if ddm_ok else None),
            }
            st.session_state['mv_result'] = {
                'sig': current_sig,
                'methods': methods,
                'price': mv_price,
                'eps': mv_eps,
                'ticker': mv_ticker or 'MANUAL',
                'name': (db_hit.get('name') if db_hit else '') or '',
                'industry': ind_key or 'Sector default',
                'cap': mv_cap,
                't_pe': t_pe,
                't_peg': t_peg,
                'eps_growth': eps_growth,
            }
            st.rerun()

        # ------------------------------------------------------------------
        # STEP 5 — Results
        # ------------------------------------------------------------------
        res = st.session_state.get('mv_result')

        if res:
            methods = res['methods']
            r_price = res['price']
            r_eps = res['eps']

            DEFAULT_W = {
                "P/E (reported EPS)": 30, "Forward P/E (est. EPS)": 20,
                "P/B": 18, "PEG-implied P/E": 10, "Graham Number": 8,
                "Earnings Power": 7, "Dividend Discount": 7,
            }

            st.markdown("---")
            st.markdown("#### 5️⃣ Valuation Result")

            with st.expander("⚖️ Method weights", expanded=False):
                st.caption("Weights are renormalised across whichever methods produced "
                           "a value, so a method that cannot compute simply drops out — "
                           "it never drags the blend toward zero.")
                weights = {}
                wcols = st.columns(3)
                for n, (name, dflt) in enumerate(DEFAULT_W.items()):
                    with wcols[n % 3]:
                        avail = methods.get(name) is not None
                        weights[name] = st.slider(
                            f"{name}{'' if avail else '  ·  needs inputs'}",
                            0, 40, dflt, 1, key=f"mv_w_{n}")

            blended, eff_w = blend_valuations(methods, weights, mos)
            stats = valuation_stats(methods)

            if blended is None or not stats:
                st.info("No method could be computed. Check that you entered a positive "
                        "EPS with a target P/E, or a book value with a target P/B.")
            else:
                upside = ((blended - r_price) / r_price * 100) if r_price else None
                sysres = st.session_state.get('mv_system')
                sys_ok = bool(sysres and not sysres.get('error')
                              and sysres.get('ticker') == res['ticker'])

                # ---- Company header (same card as Individual Analysis) ----
                _name = res['name'] or res['ticker']
                if sys_ok:
                    render_company_header(sysres['company'], res['ticker'],
                                          sysres['sector'], sysres['industry'])
                elif res['ticker'] != 'MANUAL':
                    render_company_header(_name, res['ticker'],
                                          get_sector_for_industry(res['industry']),
                                          res['industry'])
                else:
                    render_company_header("Manual Valuation", "—",
                                          get_sector_for_industry(res['industry']),
                                          res['industry'])

                # ---- Fair value + recommendation cards --------------------
                hc1, hc2 = st.columns([2, 1])
                with hc1:
                    render_fair_value_card(blended, r_price, upside,
                                           title="🧮 Manual Fair Value")
                with hc2:
                    render_recommendation_card(upside)

                # ---- System vs Manual -------------------------------------
                if sys_ok and sysres.get('fair_value'):
                    st.markdown('<div class="section-header">🤖 System vs 🧮 Manual</div>',
                                unsafe_allow_html=True)
                    s_fv = sysres['fair_value']
                    s_up = sysres['upside']
                    gap = ((blended - s_fv) / s_fv * 100) if s_fv else None

                    cmp_cols = st.columns(2)
                    with cmp_cols[0]:
                        render_fair_value_card(s_fv, r_price, s_up,
                                               title="🤖 System Fair Value")
                    with cmp_cols[1]:
                        render_fair_value_card(blended, r_price, upside,
                                               title="🧮 Your Fair Value")

                    d1, d2, d3 = st.columns(3)
                    d1.metric("System Fair Value", f"₹{s_fv:,.2f}",
                              delta=f"{s_up:+.1f}%" if s_up is not None else None)
                    d2.metric("Manual Fair Value", f"₹{blended:,.2f}",
                              delta=f"{upside:+.1f}%" if upside is not None else None)
                    d3.metric("Manual vs System",
                              f"{gap:+.1f}%" if gap is not None else "—",
                              delta=("you are more bullish" if (gap or 0) > 0
                                     else "you are more conservative"),
                              delta_color="off")

                    if gap is not None and abs(gap) > 30:
                        st.warning(
                            f"⚠️ Your valuation differs from the system model by "
                            f"{abs(gap):.0f}%. Worth checking which assumption drives "
                            f"the gap — usually the target multiple or the EPS."
                        )

                    sv = sysres['vals']
                    render_valuation_box("🤖 System Model Inputs", [
                        ("Current P/E", f"{sv['trailing_pe']:.2f}x"
                         if sv.get('trailing_pe') else "N/A"),
                        ("Industry P/E", f"{sv['industry_pe']:.2f}x"
                         if sv.get('industry_pe') else "N/A"),
                        ("EPS (TTM)", f"₹{sv['trailing_eps']:.2f}"
                         if sv.get('trailing_eps') else "N/A"),
                        ("System FV (P/E)", f"₹{sv['fair_value_pe']:,.2f}"
                         if sv.get('fair_value_pe') else "N/A"),
                        ("System FV (EV/EBITDA)", f"₹{sv['fair_value_ev']:,.2f}"
                         if sv.get('fair_value_ev') else "N/A"),
                    ])
                elif sysres and sysres.get('error'):
                    st.info(f"🤖 System valuation unavailable: {sysres['error']}")

                # ---- Key metrics cards ------------------------------------
                st.markdown('<div class="section-header">📊 Key Metrics</div>',
                            unsafe_allow_html=True)
                _mkt = (r_price * mv_shares) if (r_price and mv_shares) else None
                render_metric_cards([
                    ("💰", f"₹{r_price:,.2f}", "Current Price"),
                    ("📈", f"{implied_pe(r_price, r_eps):.2f}x"
                     if implied_pe(r_price, r_eps) else "N/A", "Implied P/E"),
                    ("💵", f"₹{r_eps:,.2f}" if r_eps else "N/A", "EPS (TTM)"),
                    ("🏦", f"₹{_mkt:,.0f}Cr" if _mkt else "N/A", "Market Cap"),
                    ("🎯", f"₹{blended:,.2f}", "Fair Value"),
                    ("📚", f"{res['t_pe']:.1f}x", "Target P/E"),
                ])

                if stats['spread_pct'] and stats['spread_pct'] > 150:
                    st.warning(
                        f"⚠️ The methods disagree by {stats['spread_pct']:.0f}% "
                        f"(₹{stats['min']:,.0f} to ₹{stats['max']:,.0f}). A blended "
                        f"number across a spread this wide is false precision — check "
                        f"which methods are the outliers before trusting it."
                    )

                # ---- Charts (gauges + comparison), same layout as system ---
                st.markdown("---")
                gc1, gc2 = st.columns(2)
                with gc1:
                    st.markdown('<div class="section-header">🎯 Valuation Gauges</div>',
                                unsafe_allow_html=True)
                    _pe_fv = methods.get("P/E (reported EPS)")
                    _pb_fv = methods.get("P/B")
                    _u1 = ((_pe_fv - r_price) / r_price * 100) if (_pe_fv and r_price) else 0
                    _u2 = ((_pb_fv - r_price) / r_price * 100) if (_pb_fv and r_price) else 0
                    st.plotly_chart(create_gauge_chart(_u1, _u2),
                                    use_container_width=True)
                    st.caption("Left: P/E method · Right: P/B method")
                with gc2:
                    st.markdown('<div class="section-header">📊 Price vs Fair Value</div>',
                                unsafe_allow_html=True)
                    cmp_fig = create_manual_comparison_chart(r_price, methods, blended)
                    if cmp_fig:
                        st.plotly_chart(cmp_fig, use_container_width=True)

                st.markdown('<div class="section-header">📐 Valuation Range</div>',
                            unsafe_allow_html=True)
                ff = create_football_field_chart(methods, r_price, blended)
                if ff:
                    st.plotly_chart(ff, use_container_width=True)

                rng1, rng2, rng3 = st.columns(3)
                rng1.metric("Range Low", f"₹{stats['min']:,.2f}")
                rng2.metric("Median", f"₹{stats['median']:,.2f}")
                rng3.metric("Range High", f"₹{stats['max']:,.2f}")

                st.markdown('<div class="section-header">📋 Valuation Breakdown</div>',
                            unsafe_allow_html=True)
                vb1, vb2 = st.columns(2)
                with vb1:
                    _pe_fv = methods.get("P/E (reported EPS)")
                    render_valuation_box("📈 P/E Multiple Method", [
                        ("Implied P/E at LTP",
                         f"{implied_pe(r_price, r_eps):.2f}x"
                         if implied_pe(r_price, r_eps) else "N/A"),
                        ("Target P/E", f"{res['t_pe']:.2f}x"),
                        ("EPS (TTM)", f"₹{r_eps:,.2f}" if r_eps else "N/A"),
                        ("Fair Value (P/E)", f"₹{_pe_fv:,.2f}" if _pe_fv else "N/A"),
                        ("Upside (P/E)",
                         f"{(_pe_fv - r_price)/r_price*100:+.2f}%"
                         if (_pe_fv and r_price) else "N/A"),
                    ])
                with vb2:
                    _pb_fv = methods.get("P/B")
                    render_valuation_box("📚 P/B Multiple Method", [
                        ("Book Value / share", f"₹{mv_bvps:,.2f}" if mv_bvps else "N/A"),
                        ("Target P/B", f"{t_pb:.2f}x"),
                        ("Implied P/B at LTP",
                         f"{r_price / mv_bvps:.2f}x" if (mv_bvps and r_price) else "N/A"),
                        ("Fair Value (P/B)", f"₹{_pb_fv:,.2f}" if _pb_fv else "N/A"),
                        ("Upside (P/B)",
                         f"{(_pb_fv - r_price)/r_price*100:+.2f}%"
                         if (_pb_fv and r_price) else "N/A"),
                    ])

                st.markdown('<div class="section-header">🧾 All Methods</div>',
                            unsafe_allow_html=True)
                mrows = []
                for name, val in methods.items():
                    mrows.append({
                        'Method': name,
                        'Fair Value': f"₹{val:,.2f}" if val else "n/a",
                        'Upside %': (f"{(val - r_price)/r_price*100:+.1f}%"
                                     if val and r_price else "—"),
                        'Weight': f"{weights.get(name, 0)}",
                        'Effective': (f"{eff_w.get(name, 0)*100:.1f}%"
                                      if name in eff_w else "—"),
                        'Status': "✅ used" if name in eff_w else (
                            "⚪ zero weight" if val else "❌ inputs missing"),
                    })
                st.dataframe(pd.DataFrame(mrows), use_container_width=True,
                             hide_index=True)

                # ---- Reverse valuation -------------------------------------
                st.markdown("##### 🔄 What Today's Price Already Assumes")
                imp_pe = implied_pe(r_price, r_eps)
                imp_g = implied_growth_for_pe(r_price, r_eps, res['t_peg'])
                need_eps = implied_eps_for_price(r_price, res['t_pe'])
                v1, v2, v3 = st.columns(3)
                v1.metric("Implied P/E at LTP", f"{imp_pe:,.2f}x" if imp_pe else "—",
                          delta=f"vs target {res['t_pe']:.1f}x" if imp_pe else None,
                          delta_color="off")
                v2.metric(f"Implied growth (PEG {res['t_peg']:.1f})",
                          f"{imp_g:,.1f}%" if imp_g else "—")
                v3.metric(f"EPS needed at {res['t_pe']:.1f}x",
                          f"₹{need_eps:,.2f}" if need_eps else "—",
                          delta=(f"{(need_eps/r_eps - 1)*100:+.1f}% vs now"
                                 if need_eps and r_eps else None), delta_color="off")

                # ---- Scenarios ---------------------------------------------
                scen = build_scenarios(r_eps, res['t_pe'])
                if scen:
                    st.markdown("##### 🎲 Bear / Base / Bull")
                    st.caption("Flexes the two levers that dominate any equity "
                               "valuation: the earnings and the multiple paid for them.")
                    srows = []
                    for label, sv in scen.items():
                        fv = sv['eps'] * sv['pe']
                        srows.append({
                            'Scenario': label,
                            'EPS': f"₹{sv['eps']:,.2f}",
                            'Target P/E': f"{sv['pe']:,.1f}x",
                            'Fair Value': f"₹{fv:,.2f}",
                            'Upside %': (f"{(fv - r_price)/r_price*100:+.1f}%"
                                         if r_price else "—"),
                        })
                    st.dataframe(pd.DataFrame(srows), use_container_width=True,
                                 hide_index=True)

                # ---- Sensitivity -------------------------------------------
                if r_eps and res['t_pe']:
                    st.markdown("##### 🔥 Sensitivity: EPS vs Target P/E")
                    pe_vals = [round(res['t_pe'] * m, 1)
                               for m in (0.7, 0.85, 1.0, 1.15, 1.3)]
                    grid = sensitivity_grid(r_eps, [-30, -15, 0, 15, 30], pe_vals)
                    if grid:
                        gdata = []
                        for row in grid:
                            d = {'EPS': f"₹{row['eps']:,.2f} ({row['eps_delta']:+.0f}%)"}
                            for pe, v in zip(pe_vals, row['values']):
                                d[f"{pe}x"] = f"₹{v:,.0f}" if v else "—"
                            gdata.append(d)
                        st.dataframe(pd.DataFrame(gdata), use_container_width=True,
                                     hide_index=True)
                        st.caption(f"At the current price of ₹{r_price:,.2f}, every cell "
                                   f"above it is upside. The width of this table is the "
                                   f"honest uncertainty in the valuation.")

                # ---- Export -------------------------------------------------
                st.markdown("---")
                exp = pd.DataFrame([{
                    'Ticker': res['ticker'],
                    'Name': res['name'],
                    'Industry': res['industry'],
                    'Cap Type': res['cap'],
                    'Price': r_price,
                    'Reported EPS': r_eps,
                    'EPS Growth %': (round(res['eps_growth'], 2)
                                     if res['eps_growth'] is not None else None),
                    'Blended Fair Value': round(blended, 2),
                    'Upside %': round(upside, 2) if upside is not None else None,
                    'Margin of Safety %': mos,
                    'Range Low': round(stats['min'], 2),
                    'Range High': round(stats['max'], 2),
                    'Median': round(stats['median'], 2),
                    'Methods Used': stats['count'],
                    'Target PE': res['t_pe'],
                    'Implied PE at LTP': round(imp_pe, 2) if imp_pe else None,
                    **{f"FV: {k}": (round(v, 2) if v else None)
                       for k, v in methods.items()}
                }])
                st.download_button(
                    "📥 Download this valuation (CSV)",
                    data=exp.to_csv(index=False),
                    file_name=f"NYZTrade_ManualValuation_{res['ticker']}_"
                              f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv", use_container_width=True
                )

            if st.button("🔄 Clear result", key="mv_clear"):
                st.session_state.pop('mv_result', None)
                st.session_state.pop('mv_system', None)
                st.rerun()

        with st.expander("📖 What each method is good for"):
            st.markdown("""
| Method | Best for | Breaks down when |
|---|---|---|
| **P/E (reported)** | Stable, profitable companies | EPS is negative or hit by one-offs |
| **Forward P/E** | Companies with visible earnings growth | Your estimate is wrong |
| **P/B** | Banks, NBFCs, asset-heavy businesses | Asset-light firms — book value means little |
| **PEG** | Growth companies | No growth, or growth that won't last |
| **Graham Number** | A conservative floor | Growth companies — it will always look expensive |
| **Earnings Power** | No-growth cash cows | Any real growth |
| **Dividend Discount** | High, stable payers (utilities, PSUs) | Low or no dividend |

Every method here runs off the six per-share inputs above, so nothing needs a
balance sheet or a cash flow statement. Treat the **range** across methods as
the real output, not the single blended number.
            """)


    elif mode == "📈 Individual Analysis":
        
        st.markdown("### 📈 Individual Stock Analysis")
        
        # Stock selection methods
        st.sidebar.subheader("Stock Selection")
        
        if "input_method_radio" not in st.session_state:
            st.session_state["input_method_radio"] = "🔍 Search by Name"
        
        input_method = st.sidebar.radio(
            "Input Method",
            ["🔍 Search by Name", "✏️ Direct Ticker", "📋 Browse by Industry"],
            key="input_method_radio"
        )
        
        selected_ticker = None
        
        if input_method == "🔍 Search by Name":
            search_query = st.sidebar.text_input("Search Company", placeholder="e.g., Reliance, TCS, HDFC")
            
            if search_query and len(search_query) >= 2:
                search_results = search_stocks_by_name(search_query, 15)
                if search_results:
                    options = [f"{r['ticker']} - {r['name']}" for r in search_results]
                    selected = st.sidebar.selectbox("Select Stock", [""] + options)
                    if selected:
                        selected_ticker = selected.split(" - ")[0]
                else:
                    st.sidebar.info("No stocks found")
        
        elif input_method == "✏️ Direct Ticker":
            selected_ticker = st.sidebar.text_input(
                "Enter Ticker",
                value=st.session_state.get("deeplink_ticker", ""),
                placeholder="e.g., RELIANCE.NS"
            ).upper()
        
        elif input_method == "📋 Browse by Industry":
            browse_industries = sorted(get_all_categories())
            browse_industry_options = [""] + [f"{industry} ({len(get_stocks_by_category(industry))} stocks)" for industry in browse_industries]
            selected_browse_industry_with_count = st.sidebar.selectbox("Select Industry", browse_industry_options)
            
            if selected_browse_industry_with_count:
                browse_industry = selected_browse_industry_with_count.split(" (")[0]  # Extract industry name
                industry_stocks = get_stocks_by_category(browse_industry)
                stock_options = [f"{ticker} - {name}" for ticker, name in industry_stocks.items()]
                selected_stock = st.sidebar.selectbox("Select Stock", [""] + sorted(stock_options))
                if selected_stock:
                    selected_ticker = selected_stock.split(" - ")[0]
        
        # Analyze button (auto-triggers when arriving from a screener valuation link)
        analyze_clicked = st.sidebar.button("🚀 Analyze", type="primary")
        auto_analyze = st.session_state.pop("auto_analyze", False)
        
        if selected_ticker and (analyze_clicked or auto_analyze):
            
            # Get stock info for industry context
            stock_info = get_stock_info(selected_ticker)
            
            with st.spinner(f"Analyzing {selected_ticker}..."):
                info, error = fetch_stock_data(selected_ticker)
            
            if error or not info:
                st.error(f"❌ Error: {error if error else 'Failed to fetch stock data'}")
                st.stop()
            
            vals = calculate_valuations(info, stock_info['category'] if stock_info else None)
            if not vals:
                st.error("❌ Unable to calculate valuations for this stock")
                st.stop()
            
            # Data Quality Validation
            data_quality_issues = []
            if not vals.get('trailing_pe') or vals['trailing_pe'] <= 0:
                data_quality_issues.append("PE Ratio unavailable or negative")
            if not vals.get('trailing_eps') or vals['trailing_eps'] <= 0:
                data_quality_issues.append("EPS unavailable or negative")
            if not vals.get('fair_value_pe') and not vals.get('fair_value_ev'):
                data_quality_issues.append("No fair value calculation possible")
            
            # Show data quality alert if issues found
            if data_quality_issues:
                st.warning(f"""
                ⚠️ **Data Quality Alert**: Unaudited data suspected and thus limited valuation possible
                
                **Issues detected:**
                - {chr(10).join(['• ' + issue for issue in data_quality_issues])}
                
                **Recommendation**: Verify financial data from official sources before making investment decisions.
                """)
            
            # Extract company info
            company = info.get('longName', selected_ticker)
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            
            # Company Header
            st.markdown(f'''
            <div class="company-header">
                <div class="company-title">{company}</div>
                <div class="company-info">
                    🏷️ {selected_ticker} • 🏢 {sector} • 🏭 {industry}
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Calculate average values
            ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
            avg_up = np.mean(ups) if ups else 0
            fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
            avg_fair = np.mean(fairs) if fairs else vals['price']
            
            # Main metrics row
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Fair Value Card
                st.markdown(f'''
                <div class="fair-value-card">
                    <div class="fair-value-title">📊 Calculated Fair Value</div>
                    <div class="fair-value-amount">₹{avg_fair:,.2f}</div>
                    <div class="fair-value-details">
                        Current Price: ₹{vals["price"]:,.2f}<br>
                        {"📈" if avg_up > 0 else "📉"} {avg_up:+.2f}% Potential
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                # Recommendation
                if avg_up > 25:
                    rec_class, rec_text, rec_icon = "rec-strong-buy", "Significantly Undervalued", "🚀"
                elif avg_up > 15:
                    rec_class, rec_text, rec_icon = "rec-buy", "Undervalued", "✅"
                elif avg_up > 0:
                    rec_class, rec_text, rec_icon = "rec-buy", "Fairly Valued", "📥"
                elif avg_up > -10:
                    rec_class, rec_text, rec_icon = "rec-hold", "Slightly Overvalued", "⏸️"
                else:
                    rec_class, rec_text, rec_icon = "rec-avoid", "Overvalued", "⚠️"
                
                st.markdown(f'''
                <div class="recommendation-card {rec_class}">
                    <h3>{rec_icon} {rec_text}</h3>
                    <p>Expected Return: {avg_up:+.2f}%</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # PDF Download
                if not data_quality_issues:  # Only offer PDF if data quality is good
                    pdf = create_pdf_report(company, selected_ticker, sector, vals)
                    st.download_button(
                        "📥 Download PDF Report",
                        data=pdf,
                        file_name=f"NYZTrade_{selected_ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            # Key Metrics Cards
            st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            
            metrics_data = [
                (m1, "💰", f"₹{vals['price']:,.2f}", "Current Price"),
                (m2, "📈", f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A", "PE Ratio"),
                (m3, "💵", f"₹{vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A", "EPS (TTM)"),
                (m4, "🏦", f"₹{vals['market_cap']/10000000:,.0f}Cr" if vals['market_cap'] else "N/A", "Market Cap"),
                (m5, "📊", f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else "N/A", "EV/EBITDA"),
                (m6, "📚", f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else "N/A", "P/B Ratio")
            ]
            
            for col, icon, value, label in metrics_data:
                with col:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div style="font-size: 1.5rem;">{icon}</div>
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Charts Section
            st.markdown("---")
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown('<div class="section-header">🎯 Valuation Gauges</div>', unsafe_allow_html=True)
                if vals['upside_pe'] is not None or vals['upside_ev'] is not None:
                    fig_gauge = create_gauge_chart(
                        vals['upside_pe'] if vals['upside_pe'] else 0,
                        vals['upside_ev'] if vals['upside_ev'] else 0
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                else:
                    st.info("Insufficient data for gauge charts")
            
            with chart_col2:
                st.markdown('<div class="section-header">📊 Price vs Fair Value</div>', unsafe_allow_html=True)
                fig_bar = create_valuation_comparison_chart(vals)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Insufficient data for comparison chart")
            
            # Additional Chart
            st.markdown('<div class="section-header">📍 52-Week Range</div>', unsafe_allow_html=True)
            range_html = create_52week_range_display(vals)
            if range_html:
                st.markdown(range_html, unsafe_allow_html=True)
            else:
                st.info("52-week data not available")
            
            # Detailed Valuation Methods
            st.markdown("---")
            st.markdown('<div class="section-header">📋 Valuation Breakdown</div>', unsafe_allow_html=True)
            
            val_col1, val_col2 = st.columns(2)
            
            with val_col1:
                if vals['fair_value_pe'] and vals['trailing_pe']:
                    st.markdown(f'''
                    <div class="valuation-box">
                        <div class="valuation-method">📈 PE Multiple Method</div>
                        <div class="valuation-row">
                            <span class="valuation-label">Current PE</span>
                            <span class="valuation-value">{vals['trailing_pe']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Industry PE</span>
                            <span class="valuation-value">{vals['industry_pe']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">EPS (TTM)</span>
                            <span class="valuation-value">₹{vals['trailing_eps']:.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Fair Value (PE)</span>
                            <span class="valuation-value">₹{vals['fair_value_pe']:,.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Upside (PE)</span>
                            <span class="valuation-value">{vals['upside_pe']:+.2f}%</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("PE valuation not available due to data quality issues")
            
            with val_col2:
                if vals['fair_value_ev'] and vals['current_ev_ebitda']:
                    st.markdown(f'''
                    <div class="valuation-box">
                        <div class="valuation-method">💼 EV/EBITDA Method</div>
                        <div class="valuation-row">
                            <span class="valuation-label">Current EV/EBITDA</span>
                            <span class="valuation-value">{vals['current_ev_ebitda']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Industry EV/EBITDA</span>
                            <span class="valuation-value">{vals['industry_ev_ebitda']:.2f}x</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">EBITDA</span>
                            <span class="valuation-value">₹{vals['ebitda']/10000000:,.0f} Cr</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Fair Value (EV)</span>
                            <span class="valuation-value">₹{vals['fair_value_ev']:,.2f}</span>
                        </div>
                        <div class="valuation-row">
                            <span class="valuation-label">Upside (EV)</span>
                            <span class="valuation-value">{vals['upside_ev']:+.2f}%</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("EV/EBITDA valuation not available due to data quality issues")
    
    elif mode == "📊 Industry Explorer":
        
        st.markdown("### 📊 Industry Explorer")
        
        # Show industry statistics
        industry_counts = {industry: len(stocks) for industry, stocks in INDIAN_STOCKS.items()}
        top_industries = dict(sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:12])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Top Industries by Stock Count")
            
            # Create bar chart
            industries_df = pd.DataFrame(list(top_industries.items()), columns=['Industry', 'Stock Count'])
            fig = px.bar(
                industries_df, 
                x='Stock Count', 
                y='Industry',
                orientation='h',
                height=400,
                color='Stock Count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Database Statistics")
            
            st.metric("Total Industries", f"{TOTAL_CATEGORIES}")
            st.metric("Total Stocks", f"{TOTAL_STOCKS:,}")
            st.metric("Avg per Industry", f"{TOTAL_STOCKS // TOTAL_CATEGORIES}")
            
            # Sector distribution
            st.markdown("#### Sector Breakdown")
            sectors_count = {}
            for industry in get_all_categories():
                sector = get_sector_for_industry(industry)
                sectors_count[sector] = sectors_count.get(sector, 0) + 1
            
            for sector, count in sorted(sectors_count.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{sector}: {count}")
        
        # Specific industry exploration
        st.markdown("---")
        st.markdown("#### 🔍 Explore Industry Details")
        
        # Create industry options with stock counts
        explore_industries = sorted(get_all_categories())
        explore_industry_options = [""] + [f"{industry} ({len(get_stocks_by_category(industry))} stocks)" for industry in explore_industries]
        selected_explore_industry_with_count = st.selectbox("Select Industry", explore_industry_options)
        
        if selected_explore_industry_with_count:
            explore_industry = selected_explore_industry_with_count.split(" (")[0]  # Extract industry name
            industry_stocks = get_stocks_by_category(explore_industry)
            sector = get_sector_for_industry(explore_industry)
            
            st.info(f"**{explore_industry}** • Sector: {sector} • {len(industry_stocks)} stocks")
            
            # Show stocks in expandable section
            if st.expander(f"View all {len(industry_stocks)} stocks"):
                stocks_df = pd.DataFrame(list(industry_stocks.items()), columns=['Ticker', 'Company'])
                st.dataframe(stocks_df, use_container_width=True, hide_index=True)
    
    else:
        # Welcome screen
        st.markdown('''
        <div class="welcome-section">
            <div class="welcome-title">👋 Welcome to NYZTrade Platform</div>
            <div class="welcome-subtitle">Your comprehensive solution for stock analysis and industry screening</div>
            
            <div class="feature-list">
                <h4>🎯 Platform Features:</h4>
                <ul>
                    <li>🔍 <strong>Industry Screener:</strong> Advanced filtering with 6 proven strategies</li>
                    <li>📈 <strong>Individual Analysis:</strong> Multi-factor valuation with data quality alerts</li>
                    <li>📊 <strong>Professional Charts:</strong> Interactive visualizations and technical analysis</li>
                    <li>📥 <strong>PDF Reports:</strong> Downloadable professional analysis reports</li>
                    <li>🎯 <strong>Buy/Sell Recommendations:</strong> AI-powered investment guidance</li>
                    <li>📱 <strong>Mobile Optimized:</strong> Perfect for analysis on any device</li>
                </ul>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Footer
    st.markdown('''
    <div class="footer">
        <h3>NYZTrade Comprehensive Platform</h3>
        <p>Professional Stock Analysis & Industry Screening Solution</p>
        <div class="disclaimer">
            ⚠️ Disclaimer: This platform is for educational and research purposes only. 
            Always consult a qualified financial advisor before making investment decisions.
            Past performance does not guarantee future results.
        </div>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
