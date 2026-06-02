import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Set Page Configuration
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide", page_icon="🍬")

# 2. Title & Overview
st.title("🍬 Nassau Candy Distributor — Route Efficiency Dashboard")
st.markdown("Interactive analytics portal monitoring factory-to-customer logistics performance, delivery timelines, and infrastructure bottlenecks.")
st.hr()

# 3. Load Dataset Safely
@st.cache_data
def load_data():
    df = pd.read_excel('Final Nassau Candy Distributor.xlsx')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Shipping Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    # Safe factory assignment fallback mapping
    factory_map = {
        'Chocolates': 'Sugar Shack',
        'Gummy Bears': 'Secret Factory',
        'Lollipops': 'The Other Factory',
        'Licorice': 'Sweet Station',
        'Fudge': 'Candy Corner'
    }
    
    # Check if 'Category' column actually exists, otherwise use a default fallback
    if 'Category' in df.columns:
        df['Manufacturing Factory'] = df['Category'].map(factory_map).fillna('Main Factory Hub')
    elif 'Product Category' in df.columns:
        df['Manufacturing Factory'] = df['Product Category'].map(factory_map).fillna('Main Factory Hub')
    else:
        df['Manufacturing Factory'] = 'Main Factory Hub'
        
    # Check if 'State/Province' exists, otherwise look for 'State' or 'Region'
    if 'State/Province' in df.columns:
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
    elif 'State' in df.columns:
        df['State/Province'] = df['State']
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
    else:
        df['State/Province'] = 'Unknown State'
        df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province'].astype(str)
    }
    df['Manufacturing Factory'] = df['Category'].map(factory_map).fillna('Main Factory Hub')
    df['Route'] = df['Manufacturing Factory'] + " ➔ " + df['State/Province']
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Error loading dataset file. Please verify 'Final Nassau Candy Distributor.xlsx' is uploaded to your repository.")
    st.stop()

# 4. Sidebar Filters
st.sidebar.header("🎯 Filter Controls")
min_date, max_date = df['Order Date'].min().to_pydatetime(), df['Order Date'].max().to_pydatetime()
start_date, end_date = st.sidebar.date_input("Date Range Selection", [min_date, max_date], min_value=min_date, max_value=max_date)

available_states = sorted(df['State/Province'].dropna().unique())
selected_states = st.sidebar.multiselect("Select Destination States", available_states, default=available_states[:5])

available_modes = sorted(df['Ship Mode'].dropna().unique())
selected_modes = st.sidebar.multiselect("Select Shipping Methods", available_modes, default=available_modes)

max_days = int(df['Shipping Lead Time'].max())
selected_threshold = st.sidebar.slider("Lead-Time Highlight Threshold (Days)", 0, max_days, 1400)

filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) & 
    (df['Order Date'] <= pd.to_datetime(end_date)) & 
    (df['State/Province'].isin(selected_states)) & 
    (df['Ship Mode'].isin(selected_modes))
]

# 5. Core Dashboard KPI Summary Cards
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="📊 Total Shipments Monitored", value=f"{len(filtered_df):,}")
with kpi2:
    st.metric(label="⏱️ Global Average Lead Time", value=f"{filtered_df['Shipping Lead Time'].mean():.2f} Days")
with kpi3:
    st.metric(label="🚨 Shipments Exceeding Threshold", value=f"{len(filtered_df[filtered_df['Shipping Lead Time'] > selected_threshold]):,}")

st.hr()

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

st.hr()

# 7. Required Module B: Geographic Region & State Performance Insights
st.header("2. 🗺️ State-Level Performance Insights & Regional Bottlenecks")
state_geo = filtered_df.groupby('State/Province')['Shipping Lead Time'].mean().reset_index()

fig_map = px.choropleth(
    state_geo, 
    locations='State/Province', 
    locationmode="USA-states", 
    color='Shipping Lead Time',
    scope="usa",
    color_continuous_scale="YlOrRd",
    labels={'Shipping Lead Time':'Avg Lead Time (Days)'},
    title="Geographic Heatmap of Shipping Delays by Destination State"
)
st.plotly_chart(fig_map, use_container_width=True)

st.hr()

# 8. Analytical Findings Executive Text Area
st.header("📌 Operational Insights Summary")
st.info("""
* **The Shipping Paradox:** Standard Processing configurations systematically outpace Express and First Class shipping lanes. This operational conflict highlights severe administrative scheduling bottlenecks inside our primary fulfillment facilities.
* **Geographic Bottlenecks:** Distribution corridors serving New Jersey, New Hampshire, and Connecticut exhibit severe infrastructure friction, with turnaround times stretching to 1,641-1,642 days.
* **Actionable Countermeasure:** We recommend executing an immediate consolidation protocol to shift regional freight management into a centralized logistics hub model.
""")

st.hr()

# 9. Required Module C: Ship Mode Performance Breakdown
st.header("3. 🚢 Shipping Method Operational Comparison")
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

st.hr()

# 10. Required Module D: Order-Level Shipment Timelines (Drill-Down Matrix)
st.header("4. 🔍 Order-Level Drill-Down Audit Trail")
st.markdown("Granular lookup tool displaying raw shipment transactions filtering specific historical outliers.")
st.dataframe(filtered_df[['Order ID', 'Order Date', 'Ship Date', 'Manufacturing Factory', 'State/Province', 'Ship Mode', 'Shipping Lead Time']].sort_values('Shipping Lead Time', ascending=False), use_container_width=True)
