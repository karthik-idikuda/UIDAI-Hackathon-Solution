"""
Enrolment Analysis Page - UIDAI Data Hackathon 2026
Detailed analysis of Aadhaar enrolment data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_enrolment_data, get_unique_states, get_unique_districts,
    filter_by_state, filter_by_district, filter_enrolment_by_age,
    get_state_aggregation, get_district_aggregation, get_daily_trend,
    format_indian_number, get_date_range, get_top_n_regions
)
from styles import apply_plotly_theme, COLORS


def render_filters(df):
    """Render simplified filter controls for enrolment page."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        states = ["All States"] + get_unique_states(df)
        selected_state = st.selectbox("State", states, key="enrolment_state_filter")
    
    with col2:
        if selected_state != "All States":
            districts = ["All Districts"] + get_unique_districts(df, selected_state)
        else:
            districts = ["All Districts"]
        selected_district = st.selectbox("District", districts, key="enrolment_district_filter")
    
    with col3:
        age_options = ["All Age Groups", "0-5 years", "5-17 years", "18+ years"]
        selected_age = st.selectbox("Age Group", age_options, key="enrolment_age_filter")
        if selected_age == "All Age Groups":
            age_groups = ["0-5 years", "5-17 years", "18+ years"]
        else:
            age_groups = [selected_age]
    
    with col4:
        min_date, max_date = get_date_range(df)
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="enrolment_date_filter"
        )
    
    return selected_state, selected_district, age_groups, date_range


def render_summary_metrics(df, age_groups):
    """Render summary metrics."""
    # Apply age filter
    if age_groups:
        df = filter_enrolment_by_age(df, age_groups)
        total_col = 'filtered_total' if 'filtered_total' in df.columns else 'total_enrolments'
    else:
        total_col = 'total_enrolments'
    
    total = df[total_col].sum()
    avg_daily = df.groupby('date')[total_col].sum().mean()
    peak_day = df.groupby('date')[total_col].sum().max()
    unique_locations = df['pincode'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Enrolments", format_indian_number(total))
    with col2:
        st.metric("Avg Daily Enrolments", format_indian_number(avg_daily))
    with col3:
        st.metric("Peak Day Enrolments", format_indian_number(peak_day))
    with col4:
        st.metric("Unique PIN Codes", f"{unique_locations:,}")


def render_state_chart(df):
    """Render state-wise enrolment chart."""
    st.markdown("### State-wise Enrolment Analysis")
    
    state_data = get_state_aggregation(df, 'total_enrolments')
    
    fig = px.bar(
        state_data.head(15),
        x='total_enrolments',
        y='state',
        orientation='h',
        color='total_enrolments',
        color_continuous_scale=[[0, COLORS["accent_secondary"]], [1, COLORS["accent_primary"]]],
    )
    fig.update_layout(
        xaxis_title="Total Enrolments",
        yaxis_title="State",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        height=500,
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_district_chart(df, state):
    """Render district-wise enrolment chart."""
    st.markdown("### District-wise Enrolment Analysis")
    
    if state == "All States":
        # Show top districts across all states
        district_data = get_district_aggregation(df, 'total_enrolments').head(15)
        district_data['label'] = district_data['district'] + ' (' + district_data['state'] + ')'
    else:
        district_data = df.groupby('district')['total_enrolments'].sum().reset_index()
        district_data = district_data.sort_values('total_enrolments', ascending=False).head(15)
        district_data['label'] = district_data['district']
    
    fig = px.bar(
        district_data,
        x='total_enrolments',
        y='label',
        orientation='h',
        color='total_enrolments',
        color_continuous_scale=[[0, COLORS["success"]], [1, COLORS["accent_secondary"]]],
    )
    fig.update_layout(
        xaxis_title="Total Enrolments",
        yaxis_title="District",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        height=500,
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_age_analysis(df):
    """Render age group analysis."""
    st.markdown("### Age Group Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_data = pd.DataFrame({
            'Age Group': ['0-5 Years', '5-17 Years', '18+ Years'],
            'Count': [
                df['age_0_5'].sum(),
                df['age_5_17'].sum(),
                df['age_18_greater'].sum()
            ]
        })
        
        fig = px.pie(
            age_data,
            values='Count',
            names='Age Group',
            color_discrete_sequence=[COLORS["accent_primary"], COLORS["accent_secondary"], COLORS["success"]],
            hole=0.4
        )
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(height=350, showlegend=False)
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Age group trend over time
        age_trend = df.groupby('date').agg({
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=age_trend['date'], y=age_trend['age_0_5'], 
                                  name='0-5 Years', line=dict(color=COLORS["accent_primary"])))
        fig.add_trace(go.Scatter(x=age_trend['date'], y=age_trend['age_5_17'], 
                                  name='5-17 Years', line=dict(color=COLORS["accent_secondary"])))
        fig.add_trace(go.Scatter(x=age_trend['date'], y=age_trend['age_18_greater'], 
                                  name='18+ Years', line=dict(color=COLORS["success"])))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Enrolments",
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_trend_analysis(df):
    """Render trend analysis."""
    st.markdown("### Enrolment Trend Analysis")
    
    daily_trend = get_daily_trend(df, 'total_enrolments')
    
    # Calculate 7-day moving average
    daily_trend['ma_7'] = daily_trend['total_enrolments'].rolling(window=7).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['total_enrolments'],
        mode='lines',
        name='Daily Enrolments',
        line=dict(color=COLORS["accent_primary"], width=1),
        opacity=0.6
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['ma_7'],
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color=COLORS["warning"], width=2)
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Enrolments",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_top_pincodes(df):
    """Render top PIN codes table."""
    st.markdown("### Top PIN Codes by Enrolment")
    
    pincode_data = df.groupby(['state', 'district', 'pincode'])['total_enrolments'].sum().reset_index()
    pincode_data = pincode_data.sort_values('total_enrolments', ascending=False).head(20)
    pincode_data.columns = ['State', 'District', 'PIN Code', 'Total Enrolments']
    pincode_data['Total Enrolments'] = pincode_data['Total Enrolments'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        pincode_data,
        use_container_width=True,
        hide_index=True
    )


def render_enrolment():
    """Main enrolment page render function."""
    st.markdown("# Enrolment Analysis")
    st.markdown("Detailed analysis of Aadhaar enrolment patterns across India")
    
    # Load data
    with st.spinner("Loading enrolment data..."):
        df = load_enrolment_data()
    
    # Render filters
    selected_state, selected_district, age_groups, date_range = render_filters(df)
    
    # Apply filters
    filtered_df = filter_by_state(df, selected_state)
    filtered_df = filter_by_district(filtered_df, selected_district)
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'] >= pd.Timestamp(start_date)) & 
            (filtered_df['date'] <= pd.Timestamp(end_date))
        ]
    
    st.markdown("---")
    
    # Render summary metrics
    render_summary_metrics(filtered_df, age_groups)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_state_chart(filtered_df)
    
    with col2:
        render_district_chart(filtered_df, selected_state)
    
    # Age analysis
    render_age_analysis(filtered_df)
    
    # Trend analysis
    render_trend_analysis(filtered_df)
    
    # Top PIN codes
    render_top_pincodes(filtered_df)
