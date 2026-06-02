import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 1. Set Page Configuration
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide", page_icon="🍬")

# 2. Title & Overview
st.title("🍬 Nassau Candy Distributor — Route Efficiency Dashboard")
st.markdown("Interactive analytics portal monitoring factory-to-customer logistics performance, delivery timelines, and infrastructure bottlenecks.")
st.divider()

# 3. Load Dataset Safely
@st.cache_data
def load_data():
    import os
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]
    
    if not excel_files:
        raise FileNotFoundError("No Excel data sheets found in the repository folder.")
    
    target_file = excel_files[0]
    df = pd.read_excel(target_file)
    
    # --- FLEXIBLE COLUMN DETECTION ---
    order_col = None
    ship_col = None
    
    for col in df.columns:
        col_clean = str(col).strip().lower().replace(" ", "").replace("_", "")
        if "orderdate" in col_clean or "dateoforder" in col_clean or "bookingdate" in col_clean:
            order_col = col
        elif "shipdate" in col_clean or "dateofship" in col_clean or "shippingdate" in col_clean:
            ship_col = col
            
    if not order_col or not ship_col:
        date_cols = [c for c in df.columns if "date" in str(c).lower()]
        if len(date_cols) >= 2:
            order_col = order_col or date_cols[0]
            ship_col = ship_col or date_cols[1]
        elif len(df.columns) >= 2:
            order_col = order_col or df.columns[0]
            ship_col = ship_col or df.columns[1]
            
    # Convert and clean dates safely
    df[order_col] = pd.to_datetime(df[order_col], errors='coerce')
    df[ship_col] = pd.to_datetime(df[ship_col], errors='coerce')
    df = df.dropna(subset=[order_col, ship_col])
    
    # Standardize column names
    df['Order Date'] = df[order_col]
    df['Ship Date'] = df[ship_col]
    
    # Calculate Lead Time
    df['Shipping Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    # Factory Assignment Logic
    factory_map = {
        'Chocolates': 'Sugar Shack', 'Chocolate': 'Sugar Shack',
        'Gummy Bears': 'Secret Factory', 'Sugar': 'Secret Factory',
        'Lollipops': 'The Other Factory', 'Other': 'The Other Factory',
        'Licorice': 'Sweet Station', 'Fudge': 'Candy Corner'
    }
    
    if 'Division' in df.columns:
        df['Manufacturing Factory'] = df['Division'].map(factory_map).fillna('Main Factory Hub')
    elif 'Category' in df.columns:
        df['Manufacturing Factory'] = df['Category'].map(factory_map).fillna('Main Factory Hub')
    else:
        df['Manufacturing Factory'] = 'Main Factory Hub'
        
    if 'State/Province' in df.columns:
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
    elif 'State' in df.columns:
        df['State/Province'] = df['State']
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
    else:
        df['State/Province'] = 'All Distribution Hubs'
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Data Connection Error: {e}")
    st.stop()

# 4. Sidebar Filters
st.sidebar.header("🎯 Filter Controls")

if len(df) > 0 and not df['Order Date'].isna().all():
    min_date = df['Order Date'].min().date()
    max_date = df['Order Date'].max().date()
else:
    min_date = datetime.date(2024, 1, 1)
    max_date = datetime.date(2025, 12, 31)

start_date = st.sidebar.date_input("Start Order Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Order Date", max_date, min_value=min_date, max_value=max_date)

available_states = sorted(df['State/Province'].dropna().unique()) if len(df) > 0 else []
selected_states = st.sidebar.multiselect("Select Destination States", available_states, default=available_states)

if 'Ship Mode' in df
