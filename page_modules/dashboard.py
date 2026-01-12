"""
Dashboard Page - UIDAI Data Hackathon 2026
Main dashboard with KPIs, national overview, and key insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_enrolment_data, load_demographic_data, load_biometric_data,
    get_unique_states, filter_by_state, get_state_aggregation,
    get_daily_trend, format_indian_number, get_date_range,
    filter_enrolment_by_age, calculate_data_quality_score,
    generate_intelligent_insights, get_security_compliance_info,
    get_performance_stats
)
from styles import apply_plotly_theme, COLORS


def render_filters(enrolment_df):
    """Render simplified filter controls."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        states = ["All States"] + get_unique_states(enrolment_df)
        selected_state = st.selectbox(
            "State",
            states,
            key="dashboard_state_filter"
        )
    
    with col2:
        age_options = ["All Age Groups", "0-5 years", "5-17 years", "18+ years"]
        selected_age = st.selectbox(
            "Age Group",
            age_options,
            key="dashboard_age_filter"
        )
        # Convert to list format for compatibility
        if selected_age == "All Age Groups":
            age_groups = ["0-5 years", "5-17 years", "18+ years"]
        else:
            age_groups = [selected_age]
    
    with col3:
        min_date, max_date = get_date_range(enrolment_df)
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="dashboard_date_filter"
        )
    
    return selected_state, age_groups, date_range


def render_kpi_cards(enrolment_df, demographic_df, biometric_df, state, age_groups):
    """Render KPI metric cards."""
    # Filter by state
    filtered_enrolment = filter_by_state(enrolment_df, state)
    filtered_demographic = filter_by_state(demographic_df, state)
    filtered_biometric = filter_by_state(biometric_df, state)
    
    # Apply age filter for enrolment
    if age_groups:
        filtered_enrolment = filter_enrolment_by_age(filtered_enrolment, age_groups)
        total_enrolments = filtered_enrolment['filtered_total'].sum() if 'filtered_total' in filtered_enrolment.columns else filtered_enrolment['total_enrolments'].sum()
    else:
        total_enrolments = filtered_enrolment['total_enrolments'].sum()
    
    total_demographic = filtered_demographic['total_demo_updates'].sum()
    total_biometric = filtered_biometric['total_bio_updates'].sum()
    
    # Calculate additional metrics
    unique_states = filtered_enrolment['state'].nunique()
    unique_districts = filtered_enrolment['district'].nunique()
    unique_pincodes = filtered_enrolment['pincode'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Enrolments",
            value=format_indian_number(total_enrolments),
            delta=f"{unique_states} States"
        )
    
    with col2:
        st.metric(
            label="Demographic Updates",
            value=format_indian_number(total_demographic),
            delta=f"{unique_districts} Districts"
        )
    
    with col3:
        st.metric(
            label="Biometric Updates",
            value=format_indian_number(total_biometric),
            delta=f"{unique_pincodes} PIN Codes"
        )
    
    with col4:
        total_transactions = total_enrolments + total_demographic + total_biometric
        st.metric(
            label="Total Transactions",
            value=format_indian_number(total_transactions),
            delta="Combined"
        )


def render_state_distribution(enrolment_df, state):
    """Render state-wise distribution chart."""
    st.markdown("### State-wise Enrolment Distribution")
    
    if state == "All States":
        state_data = get_state_aggregation(enrolment_df, 'total_enrolments')
        top_10 = state_data.head(10)
        
        fig = px.bar(
            top_10,
            x='state',
            y='total_enrolments',
            color='total_enrolments',
            color_continuous_scale=[[0, COLORS["accent_secondary"]], [1, COLORS["accent_primary"]]],
        )
        fig.update_layout(
            xaxis_title="State",
            yaxis_title="Total Enrolments",
            showlegend=False,
            coloraxis_showscale=False,
            height=400,
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Show district distribution for selected state
        filtered_df = filter_by_state(enrolment_df, state)
        district_data = filtered_df.groupby('district')['total_enrolments'].sum().reset_index()
        district_data = district_data.sort_values('total_enrolments', ascending=False).head(10)
        
        fig = px.bar(
            district_data,
            x='district',
            y='total_enrolments',
            color='total_enrolments',
            color_continuous_scale=[[0, COLORS["accent_secondary"]], [1, COLORS["accent_primary"]]],
        )
        fig.update_layout(
            xaxis_title="District",
            yaxis_title="Total Enrolments",
            showlegend=False,
            coloraxis_showscale=False,
            height=400,
        )
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_age_distribution(enrolment_df, state):
    """Render age group distribution."""
    st.markdown("### Age Group Distribution")
    
    filtered_df = filter_by_state(enrolment_df, state)
    
    age_data = pd.DataFrame({
        'Age Group': ['0-5 Years', '5-17 Years', '18+ Years'],
        'Count': [
            filtered_df['age_0_5'].sum(),
            filtered_df['age_5_17'].sum(),
            filtered_df['age_18_greater'].sum()
        ]
    })
    
    fig = px.pie(
        age_data,
        values='Count',
        names='Age Group',
        color_discrete_sequence=[COLORS["accent_primary"], COLORS["accent_secondary"], COLORS["success"]]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350, showlegend=True)
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_trend_chart(enrolment_df, state):
    """Render daily trend chart."""
    st.markdown("### Enrolment Trend Over Time")
    
    filtered_df = filter_by_state(enrolment_df, state)
    daily_trend = get_daily_trend(filtered_df, 'total_enrolments')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_trend['date'],
        y=daily_trend['total_enrolments'],
        mode='lines+markers',
        name='Enrolments',
        line=dict(color=COLORS["accent_primary"], width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor=f"rgba(59, 130, 246, 0.1)"
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Enrolments",
        height=350,
        hovermode='x unified'
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_comparison_chart(demographic_df, biometric_df, state):
    """Render demographic vs biometric comparison."""
    st.markdown("### Demographic vs Biometric Updates Comparison")
    
    demo_filtered = filter_by_state(demographic_df, state)
    bio_filtered = filter_by_state(biometric_df, state)
    
    # Get daily trends
    demo_trend = demo_filtered.groupby('date')['total_demo_updates'].sum().reset_index()
    bio_trend = bio_filtered.groupby('date')['total_bio_updates'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=demo_trend['date'],
        y=demo_trend['total_demo_updates'],
        mode='lines',
        name='Demographic Updates',
        line=dict(color=COLORS["accent_primary"], width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=bio_trend['date'],
        y=bio_trend['total_bio_updates'],
        mode='lines',
        name='Biometric Updates',
        line=dict(color=COLORS["accent_secondary"], width=2)
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Updates",
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def render_dashboard():
    """Main dashboard render function."""
    st.markdown("# Dashboard")
    st.markdown("Overview of Aadhaar enrolment and update activities across India")
    
    # Load data
    with st.spinner("Loading data..."):
        enrolment_df = load_enrolment_data()
        demographic_df = load_demographic_data()
        biometric_df = load_biometric_data()
    
    # =============================================
    # WINNING FEATURE 1: Data Quality Score
    # =============================================
    enrol_score, enrol_issues = calculate_data_quality_score(enrolment_df, 'total_enrolments')
    demo_score, demo_issues = calculate_data_quality_score(demographic_df, 'total_demo_updates')
    bio_score, bio_issues = calculate_data_quality_score(biometric_df, 'total_bio_updates')
    avg_score = round((enrol_score + demo_score + bio_score) / 3, 1)
    
    score_color = COLORS["success"] if avg_score >= 90 else (COLORS["warning"] if avg_score >= 70 else COLORS["error"])
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700; color: {score_color};">{avg_score}%</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Data Quality Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col_q2:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 600; color: {COLORS['text_primary']};">{enrol_score}%</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Enrolment Data</div>
        </div>
        """, unsafe_allow_html=True)
    with col_q3:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 600; color: {COLORS['text_primary']};">{demo_score}%</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Demographic Data</div>
        </div>
        """, unsafe_allow_html=True)
    with col_q4:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 600; color: {COLORS['text_primary']};">{bio_score}%</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Biometric Data</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Render filters
    selected_state, age_groups, date_range = render_filters(enrolment_df)
    
    # Apply date filter if valid
    if len(date_range) == 2:
        start_date, end_date = date_range
        enrolment_df = enrolment_df[
            (enrolment_df['date'] >= pd.Timestamp(start_date)) & 
            (enrolment_df['date'] <= pd.Timestamp(end_date))
        ]
        demographic_df = demographic_df[
            (demographic_df['date'] >= pd.Timestamp(start_date)) & 
            (demographic_df['date'] <= pd.Timestamp(end_date))
        ]
        biometric_df = biometric_df[
            (biometric_df['date'] >= pd.Timestamp(start_date)) & 
            (biometric_df['date'] <= pd.Timestamp(end_date))
        ]
    
    # Render KPI cards
    render_kpi_cards(enrolment_df, demographic_df, biometric_df, selected_state, age_groups)
    
    # =============================================
    # WINNING FEATURE 2: Intelligent Insights
    # =============================================
    st.markdown("---")
    st.markdown("### Auto-Generated Insights")
    
    insights = generate_intelligent_insights(enrolment_df, demographic_df, biometric_df)
    
    insight_cols = st.columns(2)
    for i, insight in enumerate(insights):
        with insight_cols[i % 2]:
            st.markdown(f"""
            <div style="background-color: {COLORS['surface']}; border-left: 3px solid {COLORS['accent_primary']}; 
                        padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 0 6px 6px 0;">
                <span style="color: {COLORS['text_primary']}; font-size: 0.85rem;">{insight}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        render_state_distribution(enrolment_df, selected_state)
    
    with col2:
        render_age_distribution(enrolment_df, selected_state)
    
    # Charts row 2
    col3, col4 = st.columns(2)
    
    with col3:
        render_trend_chart(enrolment_df, selected_state)
    
    with col4:
        render_comparison_chart(demographic_df, biometric_df, selected_state)
    
    st.markdown("---")
    
    # =============================================
    # WINNING FEATURE 5: Security & Ethics Panel
    # =============================================
    with st.expander("Security & Data Ethics Compliance", expanded=False):
        security_info = get_security_compliance_info()
        
        sec_col1, sec_col2, sec_col3 = st.columns(3)
        
        with sec_col1:
            st.markdown(f"**Data Handling**")
            for item in security_info["data_handling"]:
                st.markdown(f"- {item}")
        
        with sec_col2:
            st.markdown(f"**Compliance**")
            for item in security_info["compliance"]:
                st.markdown(f"- {item}")
        
        with sec_col3:
            st.markdown(f"**Technical**")
            for item in security_info["technical"]:
                st.markdown(f"- {item}")
    
    # =============================================
    # WINNING FEATURE 4: Performance Footer
    # =============================================
    perf_stats = get_performance_stats(enrolment_df)
    
    st.markdown(f"""
    <div style="background-color: {COLORS['bg_secondary']}; border-top: 1px solid {COLORS['border']}; 
                padding: 0.75rem 1rem; margin-top: 1rem; border-radius: 6px; text-align: center;">
        <span style="color: {COLORS['text_secondary']}; font-size: 0.7rem;">
            Optimized for national-scale datasets | 
            {perf_stats['total_records']:,} records | 
            {perf_stats['states_covered']} States | 
            {perf_stats['date_range_days']} days of data | 
            Lazy loading + cached aggregations
        </span>
    </div>
    """, unsafe_allow_html=True)

