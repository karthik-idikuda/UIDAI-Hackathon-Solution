"""
Anomaly Detection Page - UIDAI Data Hackathon 2026
Statistical anomaly detection in Aadhaar data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_enrolment_data, load_demographic_data, load_biometric_data,
    get_unique_states, filter_by_state, detect_anomalies_iqr,
    format_indian_number, get_date_range
)
from styles import apply_plotly_theme, COLORS


def render_filters(df):
    """Render simplified filter controls."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        states = ["All States"] + get_unique_states(df)
        selected_state = st.selectbox("State", states, key="anomaly_state_filter")
    
    with col2:
        data_type = st.selectbox("Data Type", ["Enrolment", "Demographic Updates", "Biometric Updates"], key="anomaly_data_type")
    
    with col3:
        sensitivity_options = ["Low (3.0)", "Medium (1.5)", "High (1.0)"]
        selected_sens = st.selectbox("Sensitivity", sensitivity_options, index=1, key="anomaly_sensitivity_select")
        sensitivity = {"Low (3.0)": 3.0, "Medium (1.5)": 1.5, "High (1.0)": 1.0}[selected_sens]
    
    with col4:
        min_date, max_date = get_date_range(df)
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="anomaly_date_filter"
        )
    
    return selected_state, data_type, sensitivity, date_range


def render_anomaly_summary(df, anomaly_df, value_col):
    """Render anomaly detection summary."""
    total_records = len(anomaly_df)
    anomaly_count = anomaly_df['is_anomaly'].sum()
    high_anomalies = (anomaly_df['anomaly_type'] == 'High').sum()
    low_anomalies = (anomaly_df['anomaly_type'] == 'Low').sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records Analyzed", f"{total_records:,}")
    with col2:
        st.metric("Anomalies Detected", f"{anomaly_count:,}", 
                  delta=f"{(anomaly_count/total_records*100):.1f}%")
    with col3:
        st.metric("High Activity Anomalies", f"{high_anomalies:,}")
    with col4:
        st.metric("Low Activity Anomalies", f"{low_anomalies:,}")


def render_anomaly_distribution(anomaly_df, value_col, lower_bound, upper_bound):
    """Render anomaly distribution chart."""
    st.markdown("### Value Distribution with Anomaly Bounds")
    
    fig = go.Figure()
    
    # Histogram of values
    fig.add_trace(go.Histogram(
        x=anomaly_df[value_col],
        nbinsx=50,
        name='Distribution',
        marker_color=COLORS["accent_primary"],
        opacity=0.7
    ))
    
    # Add threshold lines
    fig.add_vline(x=lower_bound, line_dash="dash", line_color=COLORS["warning"],
                  annotation_text=f"Lower: {lower_bound:.0f}")
    fig.add_vline(x=upper_bound, line_dash="dash", line_color=COLORS["error"],
                  annotation_text=f"Upper: {upper_bound:.0f}")
    
    fig.update_layout(
        xaxis_title="Value",
        yaxis_title="Frequency",
        height=400,
        showlegend=False
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_anomaly_timeline(anomaly_df, value_col):
    """Render anomaly timeline."""
    st.markdown("### Anomaly Timeline")
    
    daily_data = anomaly_df.groupby(['date', 'anomaly_type'])[value_col].sum().reset_index()
    
    fig = go.Figure()
    
    # Normal data
    normal = daily_data[daily_data['anomaly_type'] == 'Normal']
    fig.add_trace(go.Scatter(
        x=normal['date'],
        y=normal[value_col],
        mode='lines+markers',
        name='Normal',
        line=dict(color=COLORS["accent_primary"], width=1),
        marker=dict(size=4)
    ))
    
    # High anomalies
    high = daily_data[daily_data['anomaly_type'] == 'High']
    fig.add_trace(go.Scatter(
        x=high['date'],
        y=high[value_col],
        mode='markers',
        name='High Anomaly',
        marker=dict(color=COLORS["error"], size=10, symbol='triangle-up')
    ))
    
    # Low anomalies
    low = daily_data[daily_data['anomaly_type'] == 'Low']
    fig.add_trace(go.Scatter(
        x=low['date'],
        y=low[value_col],
        mode='markers',
        name='Low Anomaly',
        marker=dict(color=COLORS["warning"], size=10, symbol='triangle-down')
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_state_anomalies(anomaly_df, value_col):
    """Render state-wise anomaly analysis."""
    st.markdown("### State-wise Anomaly Analysis")
    
    state_anomalies = anomaly_df.groupby('state').agg({
        'is_anomaly': 'sum',
        value_col: 'count'
    }).reset_index()
    state_anomalies.columns = ['state', 'anomaly_count', 'total_records']
    state_anomalies['anomaly_rate'] = (state_anomalies['anomaly_count'] / state_anomalies['total_records'] * 100).round(2)
    state_anomalies = state_anomalies.sort_values('anomaly_count', ascending=False).head(15)
    
    fig = px.bar(
        state_anomalies,
        x='anomaly_count',
        y='state',
        orientation='h',
        color='anomaly_rate',
        color_continuous_scale=[[0, COLORS["success"]], [0.5, COLORS["warning"]], [1, COLORS["error"]]],
        labels={'anomaly_count': 'Anomaly Count', 'anomaly_rate': 'Rate (%)'}
    )
    fig.update_layout(
        xaxis_title="Number of Anomalies",
        yaxis_title="State",
        yaxis={'categoryorder': 'total ascending'},
        height=450,
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_district_anomalies(anomaly_df, value_col, state):
    """Render district-wise anomaly table."""
    st.markdown("### District-wise Anomaly Details")
    
    if state != "All States":
        filtered = anomaly_df[anomaly_df['state'] == state]
    else:
        filtered = anomaly_df
    
    # Get anomaly records only
    anomaly_records = filtered[filtered['is_anomaly'] == True].copy()
    
    if len(anomaly_records) > 0:
        district_anomalies = anomaly_records.groupby(['state', 'district', 'anomaly_type']).agg({
            value_col: ['sum', 'count', 'mean']
        }).reset_index()
        district_anomalies.columns = ['State', 'District', 'Type', 'Total Value', 'Count', 'Avg Value']
        district_anomalies['Total Value'] = district_anomalies['Total Value'].apply(lambda x: f"{x:,.0f}")
        district_anomalies['Avg Value'] = district_anomalies['Avg Value'].apply(lambda x: f"{x:,.0f}")
        district_anomalies = district_anomalies.sort_values('Count', ascending=False).head(20)
        
        st.dataframe(
            district_anomalies,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No anomalies detected with current settings.")


def render_anomaly_heatmap(anomaly_df, value_col):
    """Render anomaly heatmap."""
    st.markdown("### Anomaly Distribution Heatmap")
    
    # Group by state and date
    pivot = anomaly_df.pivot_table(
        values='is_anomaly',
        index='state',
        columns=anomaly_df['date'].dt.strftime('%Y-%m-%d'),
        aggfunc='sum',
        fill_value=0
    )
    
    # Get top states by total anomalies
    top_states = pivot.sum(axis=1).nlargest(15).index
    pivot = pivot.loc[top_states]
    
    # Sample columns if too many
    if len(pivot.columns) > 30:
        step = len(pivot.columns) // 30
        pivot = pivot.iloc[:, ::step]
    
    fig = px.imshow(
        pivot,
        labels=dict(x="Date", y="State", color="Anomalies"),
        color_continuous_scale=[[0, COLORS["bg_secondary"]], [0.5, COLORS["warning"]], [1, COLORS["error"]]],
        aspect="auto"
    )
    fig.update_layout(height=450)
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_top_anomalies_table(anomaly_df, value_col):
    """Render top anomalies table."""
    st.markdown("### Top Anomalous Records")
    
    high_anomalies = anomaly_df[anomaly_df['anomaly_type'] == 'High'].copy()
    high_anomalies = high_anomalies.sort_values(value_col, ascending=False).head(20)
    
    if len(high_anomalies) > 0:
        display_df = high_anomalies[['date', 'state', 'district', 'pincode', value_col, 'anomaly_type']].copy()
        display_df.columns = ['Date', 'State', 'District', 'PIN Code', 'Value', 'Type']
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Value'] = display_df['Value'].apply(lambda x: f"{x:,}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No high-value anomalies detected.")


def render_anomaly_detection():
    """Main anomaly detection page render function."""
    st.markdown("# Anomaly Detection")
    st.markdown("Statistical detection of unusual patterns in Aadhaar data using IQR method")
    
    # Load all data
    with st.spinner("Loading data..."):
        enrolment_df = load_enrolment_data()
        demographic_df = load_demographic_data()
        biometric_df = load_biometric_data()
    
    # Render filters
    selected_state, data_type, sensitivity, date_range = render_filters(enrolment_df)
    
    # Select appropriate dataset and value column
    if data_type == "Enrolment":
        df = enrolment_df.copy()
        value_col = 'total_enrolments'
    elif data_type == "Demographic Updates":
        df = demographic_df.copy()
        value_col = 'total_demo_updates'
    else:
        df = biometric_df.copy()
        value_col = 'total_bio_updates'
    
    # Apply state filter
    df = filter_by_state(df, selected_state)
    
    # Apply date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[
            (df['date'] >= pd.Timestamp(start_date)) & 
            (df['date'] <= pd.Timestamp(end_date))
        ]
    
    st.markdown("---")
    
    # Detect anomalies
    anomaly_df, lower_bound, upper_bound = detect_anomalies_iqr(df, value_col, sensitivity)
    
    # Summary metrics
    render_anomaly_summary(df, anomaly_df, value_col)
    
    st.markdown("---")
    
    # Distribution chart
    render_anomaly_distribution(anomaly_df, value_col, lower_bound, upper_bound)
    
    # Timeline
    render_anomaly_timeline(anomaly_df, value_col)
    
    # State analysis and heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        render_state_anomalies(anomaly_df, value_col)
    
    with col2:
        render_anomaly_heatmap(anomaly_df, value_col)
    
    # District details
    render_district_anomalies(anomaly_df, value_col, selected_state)
    
    # Top anomalies table
    render_top_anomalies_table(anomaly_df, value_col)
