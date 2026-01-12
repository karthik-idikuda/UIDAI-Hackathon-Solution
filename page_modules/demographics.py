"""
Demographics Analysis Page - UIDAI Data Hackathon 2026
Analysis of Aadhaar demographic update data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_demographic_data, get_unique_states, get_unique_districts,
    filter_by_state, filter_by_district, filter_demographic_by_age,
    get_state_aggregation, get_daily_trend, format_indian_number, get_date_range
)
from styles import apply_plotly_theme, COLORS


def render_filters(df):
    """Render simplified filter controls."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        states = ["All States"] + get_unique_states(df)
        selected_state = st.selectbox("State", states, key="demo_state_filter")
    
    with col2:
        if selected_state != "All States":
            districts = ["All Districts"] + get_unique_districts(df, selected_state)
        else:
            districts = ["All Districts"]
        selected_district = st.selectbox("District", districts, key="demo_district_filter")
    
    with col3:
        age_options = ["All Age Groups", "5-17 years", "17+ years"]
        selected_age = st.selectbox("Age Group", age_options, key="demo_age_filter")
        if selected_age == "All Age Groups":
            age_groups = ["5-17 years", "17+ years"]
        else:
            age_groups = [selected_age]
    
    with col4:
        min_date, max_date = get_date_range(df)
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="demo_date_filter"
        )
    
    return selected_state, selected_district, age_groups, date_range


def render_summary_metrics(df, age_groups):
    """Render summary metrics."""
    if age_groups:
        df = filter_demographic_by_age(df, age_groups)
        total_col = 'filtered_total' if 'filtered_total' in df.columns else 'total_demo_updates'
    else:
        total_col = 'total_demo_updates'
    
    total = df[total_col].sum()
    avg_daily = df.groupby('date')[total_col].sum().mean()
    peak_day = df.groupby('date')[total_col].sum().max()
    unique_states = df['state'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Demographic Updates", format_indian_number(total))
    with col2:
        st.metric("Avg Daily Updates", format_indian_number(avg_daily))
    with col3:
        st.metric("Peak Day Updates", format_indian_number(peak_day))
    with col4:
        st.metric("States Covered", f"{unique_states}")


def render_state_distribution(df):
    """Render state-wise distribution."""
    st.markdown("### State-wise Demographic Updates")
    
    state_data = get_state_aggregation(df, 'total_demo_updates')
    
    fig = px.bar(
        state_data.head(15),
        x='total_demo_updates',
        y='state',
        orientation='h',
        color='total_demo_updates',
        color_continuous_scale=[[0, COLORS["accent_secondary"]], [1, COLORS["accent_primary"]]],
    )
    fig.update_layout(
        xaxis_title="Total Updates",
        yaxis_title="State",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        height=500,
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_age_comparison(df):
    """Render age group comparison."""
    st.markdown("### Age Group Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_data = pd.DataFrame({
            'Age Group': ['5-17 Years', '17+ Years'],
            'Count': [
                df['demo_age_5_17'].sum(),
                df['demo_age_17_'].sum()
            ]
        })
        
        fig = px.pie(
            age_data,
            values='Count',
            names='Age Group',
            color_discrete_sequence=[COLORS["accent_primary"], COLORS["accent_secondary"]],
            hole=0.4
        )
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(height=350, showlegend=False)
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # State-wise age comparison
        state_age = df.groupby('state').agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum'
        }).reset_index()
        state_age['total'] = state_age['demo_age_5_17'] + state_age['demo_age_17_']
        state_age = state_age.sort_values('total', ascending=False).head(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='5-17 Years',
            x=state_age['state'],
            y=state_age['demo_age_5_17'],
            marker_color=COLORS["accent_primary"]
        ))
        fig.add_trace(go.Bar(
            name='17+ Years',
            x=state_age['state'],
            y=state_age['demo_age_17_'],
            marker_color=COLORS["accent_secondary"]
        ))
        
        fig.update_layout(
            barmode='stack',
            xaxis_title="State",
            yaxis_title="Updates",
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_trend_analysis(df):
    """Render trend analysis."""
    st.markdown("### Demographic Update Trends")
    
    daily_trend = get_daily_trend(df, 'total_demo_updates')
    daily_trend['ma_7'] = daily_trend['total_demo_updates'].rolling(window=7).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['total_demo_updates'],
        mode='lines',
        name='Daily Updates',
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
        yaxis_title="Total Updates",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_district_analysis(df, state):
    """Render district-level analysis."""
    st.markdown("### District-wise Analysis")
    
    if state == "All States":
        district_data = df.groupby(['state', 'district'])['total_demo_updates'].sum().reset_index()
        district_data = district_data.sort_values('total_demo_updates', ascending=False).head(15)
        district_data['label'] = district_data['district'] + ' (' + district_data['state'] + ')'
    else:
        district_data = df.groupby('district')['total_demo_updates'].sum().reset_index()
        district_data = district_data.sort_values('total_demo_updates', ascending=False).head(15)
        district_data['label'] = district_data['district']
    
    fig = px.bar(
        district_data,
        x='total_demo_updates',
        y='label',
        orientation='h',
        color='total_demo_updates',
        color_continuous_scale=[[0, COLORS["success"]], [1, COLORS["accent_secondary"]]],
    )
    fig.update_layout(
        xaxis_title="Total Updates",
        yaxis_title="District",
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False,
        height=450,
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_top_pincodes(df):
    """Render top PIN codes."""
    st.markdown("### Top PIN Codes by Demographic Updates")
    
    pincode_data = df.groupby(['state', 'district', 'pincode'])['total_demo_updates'].sum().reset_index()
    pincode_data = pincode_data.sort_values('total_demo_updates', ascending=False).head(20)
    pincode_data.columns = ['State', 'District', 'PIN Code', 'Total Updates']
    pincode_data['Total Updates'] = pincode_data['Total Updates'].apply(lambda x: f"{x:,}")
    
    st.dataframe(
        pincode_data,
        use_container_width=True,
        hide_index=True
    )


def render_demographics():
    """Main demographics page render function."""
    st.markdown("# Demographic Updates Analysis")
    st.markdown("Analysis of Aadhaar demographic data updates across India")
    
    # Load data
    with st.spinner("Loading demographic data..."):
        df = load_demographic_data()
    
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
    
    # Summary metrics
    render_summary_metrics(filtered_df, age_groups)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_state_distribution(filtered_df)
    
    with col2:
        render_district_analysis(filtered_df, selected_state)
    
    # Age comparison
    render_age_comparison(filtered_df)
    
    # Trend analysis
    render_trend_analysis(filtered_df)
    
    # Top PIN codes
    render_top_pincodes(filtered_df)
