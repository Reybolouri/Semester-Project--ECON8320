import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Set page configuration 
st.set_page_config(
    page_title="US Labor Market Dashboard",
    page_icon="📊",
    layout="wide"
)

# Mapping series IDs to human-readable names
series_names = {
    "LNS12000000": "Civilian Employment",
    "LNS13000000": "Civilian Unemployment",
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Employment",
    "CES0500000002": "Average Weekly Hours of All Employees",
    "CES0500000003": "Average Hourly Earnings of All Employees"
}

# Load data function with caching for performance
@st.cache_data
def load_data():
    return pd.read_csv('BLS_data.csv', parse_dates=['date'])

# Load the data
data = load_data()

# Add a column for human-readable series names
data['series_name'] = data['series_id'].map(series_names)
data['series_name'] = data['series_name'].fillna('Unknown Series')  # Handle unmapped series



# Sidebar 
st.sidebar.header("Filters :mag: ")
st.sidebar.write("Use the filters below to customize the dashboard.")

# Dynamically assign defaults based on these series available options
available_options = data['series_name'].unique()
default_options = ["Civilian Employment",
                   "Civilian Unemployment",
                   "Unemployment Rate",
                   "Total Nonfarm Employment",
                   "Average Weekly Hours of All Employees",
                   "Average Hourly Earnings of All Employees"]

default_options = [opt for opt in default_options if opt in available_options]

# Multiselect for series names
selected_series_names = st.sidebar.multiselect(
    "Select Data Series:",
    options=available_options,
    default=default_options
)

# Filter by years
selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=int(data['year'].min()),
    max_value=int(data['year'].max()),
    value=(2019, int(data['year'].max()))
)

st.sidebar.markdown(
    """
    ---
    **Data Source:** [Bureau of Labor Statistics](https://www.bls.gov/home.htm)
    """
)

# Map selected series names back to series IDs
selected_series_ids = [
    series_id for series_id, name in series_names.items() if name in selected_series_names
]

# Filter the data
filtered_data = data[
    (data['series_id'].isin(selected_series_ids)) &
    (data['year'].between(selected_years[0], selected_years[1]))
]

# Dashboard Title and Description
st.markdown(
    """
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="color:#0D47A1;">US Labor Market Dashboard</h1>
        <p style="color:gray;"> </p>
    </div>
    """,
    unsafe_allow_html=True
)
# Introduction Section
st.markdown(
    """
    <div style="font-size:18px; line-height:1.5;;">
        <p>
            Welcome to the US Labor Market Dashboard!👋 This dashboard analyzes key labor statistics provided by the 
            <a href="https://www.bls.gov/home.htm" style="color: #0D47A1;">Bureau of Labor Statistics</a>, 
            including civilian employment, unemployment, nonfarm employments, and average earnings trends over time.
        </p>
        <p>
            This dashboard presents the data and its trends using dynamic and interactive visualizations, spanning the years since 2019, 
            and is dynamically updated monthly with the latest data from the U.S. Bureau of Labor Statistics.
        </p>
        <p>
            Use the filters on the sidebar to customize timeline and series of data. You can find and download the filtered data at the bottom of the page.
            Thank you!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)



# Interactive Plot: Unemployment Rates
st.subheader(" :chart_with_upwards_trend: Unemployment Rates")
unemployment_data = filtered_data[filtered_data['series_id'] == 'LNS14000000']
fig_unemployment = go.Figure()

fig_unemployment.add_trace(
    go.Scatter(
        x=unemployment_data['date'],
        y=unemployment_data['value'],
        mode='lines+markers',
        name="Unemployment Rate",
        line=dict(color='blue'),
    )
)

fig_unemployment.update_layout(
    title="Unemployment Rate Over Time",
    xaxis_title="Date",
    yaxis_title="Unemployment Rate (%)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig_unemployment, use_container_width=True)

# Interactive Plot: Total Nonfarm Workers
st.subheader(":construction_worker: Number of Nonfarm Employment")
nonfarm_data = filtered_data[filtered_data['series_id'] == 'CES0000000001']
fig_nonfarm = go.Figure()

fig_nonfarm.add_trace(
    go.Scatter(
        x=nonfarm_data['date'],
        y=nonfarm_data['value'],
        mode='lines+markers',
        name="Total Nonfarm Workers",
        line=dict(color='green'),
    )
)

fig_nonfarm.update_layout(
    title="Total Nonfarm Workers Over Time",
    xaxis_title="Date",
    yaxis_title="Workers (in thousands)",
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(fig_nonfarm, use_container_width=True)

# COVID-19's Impact 
st.markdown(
    """
    <div style="font-size:18px; line-height:1.5;">
        <h3>🦠 COVID-19's Impact on the Labor Market</h3>
        Wow! The impact of COVID-19 on the labor market is hard to miss. 
        In 2020, unemployment rates skyrocketed, and thousands of jobs seemed to disappear suddenly.
        <br><br>
        Quarantines, businesses shutting down, and widespread illness left workplaces empty and people struggling. 
        It was one of the most sudden and dramatic economic shocks in history.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)







# Relationship between "Average Weekly Hours" and "Average Hourly Earnings"
st.subheader(":timer_clock: :heavy_dollar_sign: Trends: Weekly Hours vs Hourly Earnings Over Time")

hours_data = data[data['series_id'] == 'CES0500000002']
earnings_data = data[data['series_id'] == 'CES0500000003']
merged_data = pd.merge(
    hours_data[['date', 'value']].rename(columns={'value': 'avg_weekly_hours'}),
    earnings_data[['date', 'value']].rename(columns={'value': 'avg_hourly_earnings'}),
    on='date'
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['avg_weekly_hours'],
        mode='lines',
        name="Average Weekly Hours",
        line=dict(color='blue', width=2),
        hovertemplate="Date: %{x}<br>Weekly Hours: %{y:.2f}<extra></extra>"
    )
)

fig.add_trace(
    go.Scatter(
        x=merged_data['date'],
        y=merged_data['avg_hourly_earnings'],
        mode='lines',
        name="Average Hourly Earnings",
        line=dict(color='orange', width=2, dash='dot'),
        hovertemplate="Date: %{x}<br>Hourly Earnings: $%{y:.2f}<extra></extra>"
    )
)

fig.update_layout(
    title="Weekly Hours and Hourly Earnings Trends",
    xaxis=dict(
        title="Date",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False
    ),
    yaxis=dict(
        title="Value",
        showgrid=True,
        gridcolor='lightgray',
        zeroline=False
    ),
    legend=dict(
        title="Metrics",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)


# hours and wage text
st.markdown(
    """
    <div style="font-size:18px; line-height:1.5;">
        The plot above shows the weekly hours of work in comparison to the compensation. 
        You can view the exact values by hovering over the plot.
        <br><br>
        Overall the average hourly earnings seems to be increasing throughout the years and the average weekly hours of work follows the same trend.
        However other economical factors,like inflation and job market need to be fully studied for a better interpretation.
    </div>
    """,
    unsafe_allow_html=True
)



# Pie Chart for Employment vs Unemployment 
st.subheader("📊 Civilian Employment vs Civilian Unemployment")

# Filter data based on the selected year range
filtered_employment = data[(data['series_id'] == 'LNS12000000') & (data['year'].between(selected_years[0], selected_years[1]))]
filtered_unemployment = data[(data['series_id'] == 'LNS13000000') & (data['year'].between(selected_years[0], selected_years[1]))]

# Aggregate the total values over the selected year range
employment_total = filtered_employment['value'].sum()
unemployment_total = filtered_unemployment['value'].sum()

# Create a DataFrame for the pie chart
pie_data = pd.DataFrame({
    "Category": ["Employment", "Unemployment"],
    "Value": [employment_total, unemployment_total]
})

# Create the pie chart
fig_pie = px.pie(
    pie_data,
    names="Category",
    values="Value",
    title=f"Employment vs Unemployment ({selected_years[0]} - {selected_years[1]})",
    color="Category",
    color_discrete_map={"Employment": "blue", "Unemployment": "red"}
)

# Display the pie chart
st.plotly_chart(fig_pie, use_container_width=True)



# Civilian Text
st.markdown(
    """
    <div style="font-size:18px; line-height:1.5;">
        The pie chart shows the proportions of civilian employment in blue and civilian unemployment in red.
        You can select the year range on the left in the sidebar to compare different years.
        <br><br>
        There it is again!🦠  You can find the effect of the pandemic on unemployment. In 2020, unemployment jumped from 3.6 to 8.06!
        
    </div>
    
    
    """,
    unsafe_allow_html=True
)


# Summary Statistics
st.subheader(":clipboard: Summary Statistics")
summary = filtered_data.groupby('series_name')['value'].describe()
st.dataframe(summary)

# Data Table
st.subheader("📑Filtered Data Table")
st.write(filtered_data)

# Download button for filtered data
st.download_button(
    label="⬇️ Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_bls_data.csv",
    mime="text/csv"
)
