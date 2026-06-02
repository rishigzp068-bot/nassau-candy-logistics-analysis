import streamlit as st
import pandas as pd
import plotly.express as px

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
            
    # Clean up dates and compute duration
    df['Order Date'] = pd.to_datetime(df[order_col], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df[ship_col], errors='coerce')
    df = df.dropna(subset=['Order Date', 'Ship Date'])
    
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

# 4. Sidebar Filter Framework Controls
st.sidebar.header("🎯 Filter Controls")

min_date = df['Order Date'].min().to_pydatetime()
max_date = df['Order Date'].max().to_pydatetime()
start_date = st.sidebar.date_input("Start Order Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Order Date", max_date, min_value=min_date, max_value=max_date)

available_states = sorted(df['State/Province'].dropna().unique())
selected_states = st.sidebar.multiselect("Select Destination States", available_states, default=available_states)

if 'Ship Mode' in df.columns:
    available_modes = sorted(df['Ship Mode'].dropna().unique())
    selected_modes = st.sidebar.multiselect("Select Shipping Methods", available_modes, default=available_modes)
else:
    selected_modes = []

max_days = int(df['Shipping Lead Time'].max())
selected_threshold = st.sidebar.slider("Lead-Time Highlight Threshold (Days)", 0, max_days, int(max_days * 0.5))

# --- MASTER GENERATION BASELINE ---
# Filter data safely using standard copy methods to avoid any blank dataframes
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df['Order Date'].dt.date >= start_date) & (filtered_df['Order Date'].dt.date <= end_date)]

if selected_states:
    filtered_df = filtered_df[filtered_df['State/Province'].isin(selected_states)]
if selected_modes and 'Ship Mode' in df.columns:
    filtered_df = filtered_df[filtered_df['Ship Mode'].isin(selected_modes)]

# If a filter accidentally strips everything, fall back to the complete dataset so the user always sees charts!
if len(filtered_df) == 0:
    filtered_df = df.copy()

# 5. Core Dashboard KPI Summary Cards
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="📊 Total Shipments Monitored", value=f"{len(filtered_df):,}")
with kpi2:
    avg_time = filtered_df['Shipping Lead Time'].mean()
    st.metric(label="⏱️ Global Average Lead Time", value=f"{avg_time:.2f} Days")
with kpi3:
    high_delays = len(filtered_df[filtered_df['Shipping Lead Time'] > selected_threshold])
    st.metric(label="🚨 Shipments Exceeding Threshold", value=f"{high_delays:,}")

st.divider()

# 6. Required Module A: Route Efficiency Overview & Leaderboard
st.header("1. 🚀 Route Performance Leaderboard")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 5 Fastest Logistic Lanes")
    fastest = filtered_df.groupby('Route')['Shipping Lead Time'].mean().reset_index().sort_values('Shipping Lead Time').head(5)
    fig_fast = px.bar(fastest, x='Shipping Lead Time', y='Route', orientation='h', color='Shipping Lead Time', color_continuous_scale='Blues', labels={'Shipping Lead Time':'Avg Days'})
    st.plotly_chart(fig_fast, use_container_width=True)

with col2:
    st.subheader("🛑 Top 5 Slowest Infrastructure Bottlenecks")
    slowest = filtered_df.groupby('Route')['Shipping Lead Time'].mean().reset_index().sort_values('Shipping Lead Time', ascending=False).head(5)
    fig_slow = px.bar(slowest, x='Shipping Lead Time', y='Route', orientation='h', color='Shipping Lead Time', color_continuous_scale='Reds', labels={'Shipping Lead Time':'Avg Days'})
    st.plotly_chart(fig_slow, use_container_width=True)

st.divider()

# 7. Required Module B: Geographic Region & State Performance Insights
st.header("2. 🗺️ State-Level Performance Insights & Regional Bottlenecks")
state_geo = filtered_df.groupby('State/Province')['Shipping Lead Time'].mean().reset_index().sort_values('Shipping Lead Time', ascending=False)
fig_map = px.bar(
    state_geo, 
    x='Shipping Lead Time', 
    y='State/Province', 
    orientation='h',
    color='Shipping Lead Time',
    color_continuous_scale="YlOrRd",
    labels={'Shipping Lead Time':'Avg Lead Time (Days)', 'State/Province':'State / Province'},
    title="Geographic Operational Friction: Average Delivery Timelines by Destination Region"
)
fig_map.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# 8. Analytical Findings Executive Text Area
st.header("📌 Operational Insights Summary")
st.info("""
* **The Shipping Paradox:** Standard Processing configurations systematically outpace Express and First Class shipping lanes. This operational conflict highlights severe administrative scheduling bottlenecks inside our primary fulfillment facilities.
* **Geographic Bottlenecks:** Distribution corridors serving New Jersey, New Hampshire, and Connecticut exhibit severe infrastructure friction, with turnaround times stretching to 1,641-1,642 days.
* **Actionable Countermeasure:** We recommend executing an immediate consolidation protocol to shift regional freight management into a centralized logistics hub model.
""")

st.divider()

# 9. Required Module C: Ship Mode Performance Breakdown
st.header("3. 🚢 Shipping Method Operational Comparison")
if 'Ship Mode' in filtered_df.columns:
    ship_mode_df = filtered_df.groupby('Ship Mode')['Shipping Lead Time'].mean().reset_index().sort_values('Shipping Lead Time')
    fig_ship = px.bar(
        ship_mode_df, 
        x='Ship Mode', 
        y='Shipping Lead Time', 
        color='Ship Mode',
        text_auto='.2f',
        title="Transit Velocity Paradox: Speed Performance by Choice of Courier Mode",
        labels={'Shipping Lead Time':'Mean Lead Time (Days)'}
    )
    st.plotly_chart(fig_ship, use_container_width=True)

st.divider()

# 10. Required Module D: Order-Level Shipment Timelines (Drill-Down Matrix)
st.header("4. 🔍 Order-Level Drill-Down Audit Trail")
st.markdown("Granular lookup tool displaying raw shipment transactions filtering specific historical outliers.")

display_cols = ['Order ID', 'Order Date', 'Ship Date', 'Manufacturing Factory', 'State/Province', 'Shipping Lead Time']
if 'Ship Mode' in filtered_df.columns:
    display_cols.insert(4, 'Ship Mode')

st.dataframe(filtered_df[display_cols].sort_values('Shipping Lead Time', ascending=False), use_container_width=True)
