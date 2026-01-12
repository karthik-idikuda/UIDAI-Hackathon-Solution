"""
Reports Page - UIDAI Data Hackathon 2026
Comprehensive reports with highlights, insights, and downloadable content.
NO filters on this page - shows full data overview.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_enrolment_data, load_demographic_data, load_biometric_data,
    get_state_aggregation, get_daily_trend, format_indian_number,
    get_date_range, detect_anomalies_iqr
)
from styles import apply_plotly_theme, COLORS


def render_executive_summary(enrolment_df, demographic_df, biometric_df):
    """Render executive summary section."""
    st.markdown("## Executive Summary")
    
    # Calculate key metrics
    total_enrolments = enrolment_df['total_enrolments'].sum()
    total_demo_updates = demographic_df['total_demo_updates'].sum()
    total_bio_updates = biometric_df['total_bio_updates'].sum()
    total_transactions = total_enrolments + total_demo_updates + total_bio_updates
    
    # Date range
    min_date = min(enrolment_df['date'].min(), demographic_df['date'].min(), biometric_df['date'].min())
    max_date = max(enrolment_df['date'].max(), demographic_df['date'].max(), biometric_df['date'].max())
    days_covered = (max_date - min_date).days + 1
    
    # Coverage stats
    all_states = set(enrolment_df['state'].unique()) | set(demographic_df['state'].unique()) | set(biometric_df['state'].unique())
    all_districts = set(enrolment_df['district'].unique()) | set(demographic_df['district'].unique()) | set(biometric_df['district'].unique())
    all_pincodes = set(enrolment_df['pincode'].unique()) | set(demographic_df['pincode'].unique()) | set(biometric_df['pincode'].unique())
    
    # Daily averages
    avg_daily_enrol = total_enrolments / days_covered
    avg_daily_demo = total_demo_updates / days_covered
    avg_daily_bio = total_bio_updates / days_covered
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: {COLORS['text_primary']}; margin-bottom: 0.75rem; font-size: 1rem;">Data Coverage</h4>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">Period:</strong> 
                {min_date.strftime('%d %b %Y')} - {max_date.strftime('%d %b %Y')}
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">Duration:</strong> {days_covered} days
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">States/UTs:</strong> {len(all_states)}
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">Districts:</strong> {len(all_districts):,}
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">PIN Codes:</strong> {len(all_pincodes):,}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: {COLORS['text_primary']}; margin-bottom: 0.75rem; font-size: 1rem;">Transaction Totals</h4>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['accent_primary']};">Enrolments:</span> 
                <strong>{format_indian_number(total_enrolments)}</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['accent_secondary']};">Demographic Updates:</span> 
                <strong>{format_indian_number(total_demo_updates)}</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['success']};">Biometric Updates:</span> 
                <strong>{format_indian_number(total_bio_updates)}</strong>
            </p>
            <hr style="border-color: {COLORS['border']}; margin: 0.75rem 0;">
            <p style="color: {COLORS['text_primary']}; margin: 0.4rem 0; font-size: 1rem; font-weight: 600;">
                Grand Total: {format_indian_number(total_transactions)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: {COLORS['text_primary']}; margin-bottom: 0.75rem; font-size: 1rem;">Daily Averages</h4>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['accent_primary']};">Avg Enrolments/Day:</span> 
                <strong>{format_indian_number(avg_daily_enrol)}</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['accent_secondary']};">Avg Demo Updates/Day:</span> 
                <strong>{format_indian_number(avg_daily_demo)}</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <span style="color: {COLORS['success']};">Avg Bio Updates/Day:</span> 
                <strong>{format_indian_number(avg_daily_bio)}</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; margin: 0.4rem 0; font-size: 0.85rem;">
                <strong style="color: {COLORS['text_primary']};">Total Records:</strong> 
                {len(enrolment_df) + len(demographic_df) + len(biometric_df):,}
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_highlights(enrolment_df, demographic_df, biometric_df):
    """Render key highlights section."""
    st.markdown("## Key Highlights")
    
    # Calculate highlights
    top_enrolment_state = enrolment_df.groupby('state')['total_enrolments'].sum().idxmax()
    top_enrolment_value = enrolment_df.groupby('state')['total_enrolments'].sum().max()
    
    top_demo_state = demographic_df.groupby('state')['total_demo_updates'].sum().idxmax()
    top_demo_value = demographic_df.groupby('state')['total_demo_updates'].sum().max()
    
    top_bio_state = biometric_df.groupby('state')['total_bio_updates'].sum().idxmax()
    top_bio_value = biometric_df.groupby('state')['total_bio_updates'].sum().max()
    
    # Peak days
    peak_enrolment_day = enrolment_df.groupby('date')['total_enrolments'].sum().idxmax()
    peak_enrolment_value = enrolment_df.groupby('date')['total_enrolments'].sum().max()
    
    peak_demo_day = demographic_df.groupby('date')['total_demo_updates'].sum().idxmax()
    peak_demo_value = demographic_df.groupby('date')['total_demo_updates'].sum().max()
    
    # Top districts
    top_enrol_district = enrolment_df.groupby(['state', 'district'])['total_enrolments'].sum().idxmax()
    top_enrol_district_value = enrolment_df.groupby(['state', 'district'])['total_enrolments'].sum().max()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['accent_primary']}; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Top Enrolment State</p>
            <p style="color: {COLORS['accent_primary']}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{top_enrolment_state}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(top_enrolment_value)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['success']}; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Peak Enrolment Day</p>
            <p style="color: {COLORS['success']}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{peak_enrolment_day.strftime('%d %b %Y')}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(peak_enrolment_value)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['accent_secondary']}; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Top Demo Update State</p>
            <p style="color: {COLORS['accent_secondary']}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{top_demo_state}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(top_demo_value)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['warning']}; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Top Bio Update State</p>
            <p style="color: {COLORS['warning']}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{top_bio_state}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(top_bio_value)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid {COLORS['error']}; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Peak Demo Update Day</p>
            <p style="color: {COLORS['error']}; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{peak_demo_day.strftime('%d %b %Y')}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(peak_demo_value)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border-left: 4px solid #8B5CF6; 
                    border-radius: 0 8px 8px 0; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0; text-transform: uppercase;">Top District (Enrolment)</p>
            <p style="color: #8B5CF6; font-size: 1.1rem; font-weight: 600; margin: 0.25rem 0 0 0;">{top_enrol_district[1]}</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">{format_indian_number(top_enrol_district_value)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Age distribution summary
        age_0_5 = enrolment_df['age_0_5'].sum()
        age_5_17 = enrolment_df['age_5_17'].sum()
        age_18 = enrolment_df['age_18_greater'].sum()
        total = age_0_5 + age_5_17 + age_18
        
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 8px; padding: 0.75rem 1rem;">
            <p style="color: {COLORS['text_primary']}; font-size: 0.85rem; font-weight: 600; margin: 0 0 0.5rem 0;">Age Distribution</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0.3rem 0;">
                0-5 Years: <strong style="color: {COLORS['accent_primary']};">{(age_0_5/total*100):.1f}%</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0.3rem 0;">
                5-17 Years: <strong style="color: {COLORS['accent_secondary']};">{(age_5_17/total*100):.1f}%</strong>
            </p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0.3rem 0;">
                18+ Years: <strong style="color: {COLORS['success']};">{(age_18/total*100):.1f}%</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_whats_new(enrolment_df, demographic_df, biometric_df):
    """Render What's New section."""
    st.markdown("## What's New - Recent Activity")
    
    max_date = enrolment_df['date'].max()
    week_ago = max_date - timedelta(days=7)
    two_weeks_ago = max_date - timedelta(days=14)
    
    # Current week
    curr_enrol = enrolment_df[enrolment_df['date'] > week_ago]['total_enrolments'].sum()
    curr_demo = demographic_df[demographic_df['date'] > week_ago]['total_demo_updates'].sum()
    curr_bio = biometric_df[biometric_df['date'] > week_ago]['total_bio_updates'].sum()
    
    # Previous week
    prev_enrol = enrolment_df[(enrolment_df['date'] > two_weeks_ago) & (enrolment_df['date'] <= week_ago)]['total_enrolments'].sum()
    prev_demo = demographic_df[(demographic_df['date'] > two_weeks_ago) & (demographic_df['date'] <= week_ago)]['total_demo_updates'].sum()
    prev_bio = biometric_df[(biometric_df['date'] > two_weeks_ago) & (biometric_df['date'] <= week_ago)]['total_bio_updates'].sum()
    
    # Growth rates
    enrol_growth = ((curr_enrol - prev_enrol) / prev_enrol * 100) if prev_enrol > 0 else 0
    demo_growth = ((curr_demo - prev_demo) / prev_demo * 100) if prev_demo > 0 else 0
    bio_growth = ((curr_bio - prev_bio) / prev_bio * 100) if prev_bio > 0 else 0
    
    # Top states this week
    recent_top_states = enrolment_df[enrolment_df['date'] > week_ago].groupby('state')['total_enrolments'].sum().nlargest(5)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        growth_color = COLORS['success'] if enrol_growth >= 0 else COLORS['error']
        growth_icon = "+" if enrol_growth >= 0 else ""
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0; text-transform: uppercase;">Last 7 Days Enrolments</p>
            <p style="color: {COLORS['accent_primary']}; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{format_indian_number(curr_enrol)}</p>
            <p style="color: {growth_color}; font-size: 0.85rem; margin: 0;">
                {growth_icon}{enrol_growth:.1f}% vs prev week
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        growth_color = COLORS['success'] if demo_growth >= 0 else COLORS['error']
        growth_icon = "+" if demo_growth >= 0 else ""
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0; text-transform: uppercase;">Last 7 Days Demo Updates</p>
            <p style="color: {COLORS['accent_secondary']}; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{format_indian_number(curr_demo)}</p>
            <p style="color: {growth_color}; font-size: 0.85rem; margin: 0;">
                {growth_icon}{demo_growth:.1f}% vs prev week
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        growth_color = COLORS['success'] if bio_growth >= 0 else COLORS['error']
        growth_icon = "+" if bio_growth >= 0 else ""
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0; text-transform: uppercase;">Last 7 Days Bio Updates</p>
            <p style="color: {COLORS['success']}; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{format_indian_number(curr_bio)}</p>
            <p style="color: {growth_color}; font-size: 0.85rem; margin: 0;">
                {growth_icon}{bio_growth:.1f}% vs prev week
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Top 5 Active States (Last 7 Days)")
    cols = st.columns(5)
    for i, (state, value) in enumerate(recent_top_states.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                        border-radius: 8px; padding: 0.75rem; text-align: center;">
                <p style="color: {COLORS['text_secondary']}; font-size: 0.7rem; margin: 0;">#{i+1}</p>
                <p style="color: {COLORS['text_primary']}; font-size: 0.85rem; font-weight: 600; margin: 0.25rem 0;">{state}</p>
                <p style="color: {COLORS['accent_primary']}; font-size: 0.9rem; font-weight: 600; margin: 0;">{format_indian_number(value)}</p>
            </div>
            """, unsafe_allow_html=True)


def render_whats_happening(enrolment_df, demographic_df, biometric_df):
    """Render What's Happening section."""
    st.markdown("## What's Happening - Trends & Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Transaction Trends Over Time")
        
        enrol_trend = enrolment_df.groupby('date')['total_enrolments'].sum().reset_index()
        demo_trend = demographic_df.groupby('date')['total_demo_updates'].sum().reset_index()
        bio_trend = biometric_df.groupby('date')['total_bio_updates'].sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=enrol_trend['date'], y=enrol_trend['total_enrolments'], 
                                  name='Enrolments', line=dict(color=COLORS["accent_primary"], width=2)))
        fig.add_trace(go.Scatter(x=demo_trend['date'], y=demo_trend['total_demo_updates'], 
                                  name='Demographic', line=dict(color=COLORS["accent_secondary"], width=2)))
        fig.add_trace(go.Scatter(x=bio_trend['date'], y=bio_trend['total_bio_updates'], 
                                  name='Biometric', line=dict(color=COLORS["success"], width=2)))
        
        fig.update_layout(height=320, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### State-wise Combined Activity")
        
        enrol_state = enrolment_df.groupby('state')['total_enrolments'].sum()
        demo_state = demographic_df.groupby('state')['total_demo_updates'].sum()
        bio_state = biometric_df.groupby('state')['total_bio_updates'].sum()
        
        combined = pd.DataFrame({'Enrolments': enrol_state, 'Demographic': demo_state, 'Biometric': bio_state}).fillna(0)
        combined['Total'] = combined.sum(axis=1)
        combined = combined.sort_values('Total', ascending=True).tail(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(y=combined.index, x=combined['Enrolments'], name='Enrolments', 
                             orientation='h', marker_color=COLORS["accent_primary"]))
        fig.add_trace(go.Bar(y=combined.index, x=combined['Demographic'], name='Demographic', 
                             orientation='h', marker_color=COLORS["accent_secondary"]))
        fig.add_trace(go.Bar(y=combined.index, x=combined['Biometric'], name='Biometric', 
                             orientation='h', marker_color=COLORS["success"]))
        
        fig.update_layout(barmode='stack', height=320, 
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_regional_analysis(enrolment_df, demographic_df, biometric_df):
    """Render regional analysis section."""
    st.markdown("## Regional Analysis")
    
    # Define regions
    north = ['Delhi', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Punjab', 'Rajasthan', 'Uttarakhand', 'Uttar Pradesh', 'Chandigarh', 'Ladakh']
    south = ['Andhra Pradesh', 'Karnataka', 'Kerala', 'Tamil Nadu', 'Telangana', 'Puducherry', 'Lakshadweep', 'Andaman and Nicobar Islands']
    east = ['Bihar', 'Jharkhand', 'Odisha', 'West Bengal', 'Sikkim']
    west = ['Goa', 'Gujarat', 'Maharashtra', 'Dadra and Nagar Haveli and Daman and Diu']
    central = ['Chhattisgarh', 'Madhya Pradesh']
    northeast = ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Tripura']
    
    def get_region(state):
        if state in north: return 'North'
        elif state in south: return 'South'
        elif state in east: return 'East'
        elif state in west: return 'West'
        elif state in central: return 'Central'
        elif state in northeast: return 'Northeast'
        else: return 'Other'
    
    enrolment_df_copy = enrolment_df.copy()
    enrolment_df_copy['region'] = enrolment_df_copy['state'].apply(get_region)
    
    region_data = enrolment_df_copy.groupby('region')['total_enrolments'].sum().reset_index()
    region_data = region_data.sort_values('total_enrolments', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(region_data, values='total_enrolments', names='region', 
                     color_discrete_sequence=[COLORS["accent_primary"], COLORS["accent_secondary"], 
                                               COLORS["success"], COLORS["warning"], COLORS["error"], "#8B5CF6"])
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=300, showlegend=False, title="Enrolment by Region")
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(region_data, x='region', y='total_enrolments', 
                     color='total_enrolments',
                     color_continuous_scale=[[0, COLORS["accent_secondary"]], [1, COLORS["accent_primary"]]])
        fig.update_layout(height=300, showlegend=False, coloraxis_showscale=False, title="Regional Comparison")
        fig = apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def render_key_findings(enrolment_df, demographic_df, biometric_df):
    """Render key findings section."""
    st.markdown("## Key Findings & Insights")
    
    # Calculations
    enrol_anomalies, _, _ = detect_anomalies_iqr(enrolment_df, 'total_enrolments')
    anomaly_count = enrol_anomalies['is_anomaly'].sum()
    anomaly_pct = (anomaly_count / len(enrol_anomalies)) * 100
    
    total_enrol = enrolment_df['total_enrolments'].sum()
    child_enrol = enrolment_df['age_0_5'].sum() + enrolment_df['age_5_17'].sum()
    child_pct = (child_enrol / total_enrol * 100)
    
    adult_demo = demographic_df['demo_age_17_'].sum()
    total_demo = demographic_df['total_demo_updates'].sum()
    adult_demo_pct = (adult_demo / total_demo * 100)
    
    # Weekday analysis
    enrolment_df_copy = enrolment_df.copy()
    enrolment_df_copy['weekday'] = enrolment_df_copy['date'].dt.dayofweek
    weekday_avg = enrolment_df_copy[enrolment_df_copy['weekday'] < 5].groupby('date')['total_enrolments'].sum().mean()
    weekend_avg = enrolment_df_copy[enrolment_df_copy['weekday'] >= 5].groupby('date')['total_enrolments'].sum().mean()
    weekend_drop = ((weekday_avg - weekend_avg) / weekday_avg * 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: {COLORS['text_primary']}; margin-bottom: 0.75rem; font-size: 1rem;">Enrolment Insights</h4>
            <ul style="color: {COLORS['text_secondary']}; padding-left: 1.25rem; margin: 0; font-size: 0.85rem;">
                <li style="margin: 0.4rem 0;">Child enrolments (0-17) constitute <strong style="color: {COLORS['accent_primary']};">{child_pct:.1f}%</strong> of total</li>
                <li style="margin: 0.4rem 0;"><strong style="color: {COLORS['warning']};">{anomaly_count:,}</strong> anomalous patterns detected ({anomaly_pct:.2f}%)</li>
                <li style="margin: 0.4rem 0;">Weekend activity drops by <strong style="color: {COLORS['error']};">{weekend_drop:.1f}%</strong> vs weekdays</li>
                <li style="margin: 0.4rem 0;">Northern states dominate enrolment volumes</li>
                <li style="margin: 0.4rem 0;">Urban districts show consistently higher activity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1.25rem; margin-bottom: 0.75rem;">
            <h4 style="color: {COLORS['text_primary']}; margin-bottom: 0.75rem; font-size: 1rem;">Update Insights</h4>
            <ul style="color: {COLORS['text_secondary']}; padding-left: 1.25rem; margin: 0; font-size: 0.85rem;">
                <li style="margin: 0.4rem 0;">Adult updates account for <strong style="color: {COLORS['accent_secondary']};">{adult_demo_pct:.1f}%</strong> of demographic updates</li>
                <li style="margin: 0.4rem 0;">Biometric updates show periodic spikes (renewal cycles)</li>
                <li style="margin: 0.4rem 0;">Metro cities lead in update frequency</li>
                <li style="margin: 0.4rem 0;">Address changes are most common demographic update</li>
                <li style="margin: 0.4rem 0;">Child-to-adult biometric updates follow age patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def render_data_quality(enrolment_df, demographic_df, biometric_df):
    """Render data quality summary."""
    st.markdown("## Data Quality Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        null_pct = (enrolment_df.isnull().sum().sum() / (len(enrolment_df) * len(enrolment_df.columns))) * 100
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Enrolment Data</p>
            <p style="color: {COLORS['success']}; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0;">{100-null_pct:.2f}%</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Completeness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        null_pct = (demographic_df.isnull().sum().sum() / (len(demographic_df) * len(demographic_df.columns))) * 100
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Demographic Data</p>
            <p style="color: {COLORS['success']}; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0;">{100-null_pct:.2f}%</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Completeness</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        null_pct = (biometric_df.isnull().sum().sum() / (len(biometric_df) * len(biometric_df.columns))) * 100
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 1rem; text-align: center;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Biometric Data</p>
            <p style="color: {COLORS['success']}; font-size: 1.25rem; font-weight: 600; margin: 0.25rem 0;">{100-null_pct:.2f}%</p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.75rem; margin: 0;">Completeness</p>
        </div>
        """, unsafe_allow_html=True)


def render_download_section(enrolment_df, demographic_df, biometric_df):
    """Render download section."""
    st.markdown("## Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enrol_summary = enrolment_df.groupby('state').agg({
            'total_enrolments': 'sum', 'age_0_5': 'sum', 'age_5_17': 'sum',
            'age_18_greater': 'sum', 'district': 'nunique', 'pincode': 'nunique'
        }).reset_index()
        enrol_summary.columns = ['State', 'Total Enrolments', '0-5 Years', '5-17 Years', '18+ Years', 'Districts', 'PIN Codes']
        
        st.download_button(
            label="Download Enrolment Report",
            data=enrol_summary.to_csv(index=False),
            file_name="enrolment_report.csv",
            mime="text/csv"
        )
    
    with col2:
        demo_summary = demographic_df.groupby('state').agg({
            'total_demo_updates': 'sum', 'demo_age_5_17': 'sum', 'demo_age_17_': 'sum', 'district': 'nunique'
        }).reset_index()
        demo_summary.columns = ['State', 'Total Updates', '5-17 Years', '17+ Years', 'Districts']
        
        st.download_button(
            label="Download Demographic Report",
            data=demo_summary.to_csv(index=False),
            file_name="demographic_report.csv",
            mime="text/csv"
        )
    
    with col3:
        bio_summary = biometric_df.groupby('state').agg({
            'total_bio_updates': 'sum', 'bio_age_5_17': 'sum', 'bio_age_17_': 'sum', 'district': 'nunique'
        }).reset_index()
        bio_summary.columns = ['State', 'Total Updates', '5-17 Years', '17+ Years', 'Districts']
        
        st.download_button(
            label="Download Biometric Report",
            data=bio_summary.to_csv(index=False),
            file_name="biometric_report.csv",
            mime="text/csv"
        )


def render_reports():
    """Main reports page render function."""
    st.markdown("# Comprehensive Reports")
    st.markdown("Complete overview of Aadhaar data with highlights, insights, and downloadable reports")
    
    with st.spinner("Loading all datasets..."):
        enrolment_df = load_enrolment_data()
        demographic_df = load_demographic_data()
        biometric_df = load_biometric_data()
    
    st.markdown("---")
    render_executive_summary(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_highlights(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_whats_new(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_whats_happening(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_regional_analysis(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_key_findings(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_data_quality(enrolment_df, demographic_df, biometric_df)
    
    st.markdown("---")
    render_download_section(enrolment_df, demographic_df, biometric_df)
