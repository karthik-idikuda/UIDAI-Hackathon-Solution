"""
Utility functions for UIDAI Data Hackathon 2026 Application
Data loading, preprocessing, and common utilities.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

# Base path for data
DATA_BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Dataset folders
ENROLMENT_FOLDER = "api_data_aadhar_enrolment"
DEMOGRAPHIC_FOLDER = "api_data_aadhar_demographic"
BIOMETRIC_FOLDER = "api_data_aadhar_biometric"


@st.cache_data(ttl=3600)
def load_enrolment_data():
    """Load and concatenate all Aadhaar enrolment CSV files."""
    folder_path = os.path.join(DATA_BASE_PATH, ENROLMENT_FOLDER)
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Parse date column
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Calculate total enrolments
    combined_df['total_enrolments'] = (
        combined_df['age_0_5'] + 
        combined_df['age_5_17'] + 
        combined_df['age_18_greater']
    )
    
    return combined_df


@st.cache_data(ttl=3600)
def load_demographic_data():
    """Load and concatenate all Aadhaar demographic update CSV files."""
    folder_path = os.path.join(DATA_BASE_PATH, DEMOGRAPHIC_FOLDER)
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Parse date column
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Calculate total demographic updates
    combined_df['total_demo_updates'] = (
        combined_df['demo_age_5_17'] + 
        combined_df['demo_age_17_']
    )
    
    return combined_df


@st.cache_data(ttl=3600)
def load_biometric_data():
    """Load and concatenate all Aadhaar biometric update CSV files."""
    folder_path = os.path.join(DATA_BASE_PATH, BIOMETRIC_FOLDER)
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    dfs = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Parse date column
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%d-%m-%Y', errors='coerce')
    
    # Calculate total biometric updates
    combined_df['total_bio_updates'] = (
        combined_df['bio_age_5_17'] + 
        combined_df['bio_age_17_']
    )
    
    return combined_df


def get_unique_states(df):
    """Get sorted list of unique states from dataframe."""
    states = df['state'].dropna().unique().tolist()
    return sorted(states)


def get_unique_districts(df, state=None):
    """Get sorted list of unique districts, optionally filtered by state."""
    if state and state != "All States":
        filtered_df = df[df['state'] == state]
    else:
        filtered_df = df
    districts = filtered_df['district'].dropna().unique().tolist()
    return sorted(districts)


def filter_by_state(df, state):
    """Filter dataframe by state."""
    if state and state != "All States":
        return df[df['state'] == state]
    return df


def filter_by_district(df, district):
    """Filter dataframe by district."""
    if district and district != "All Districts":
        return df[df['district'] == district]
    return df


def filter_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range."""
    if start_date and end_date:
        return df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return df


def filter_enrolment_by_age(df, age_groups):
    """
    Filter enrolment data by age groups and return relevant columns.
    age_groups: list of selected age groups ['0-5 years', '5-17 years', '18+ years']
    """
    columns_to_sum = []
    if '0-5 years' in age_groups:
        columns_to_sum.append('age_0_5')
    if '5-17 years' in age_groups:
        columns_to_sum.append('age_5_17')
    if '18+ years' in age_groups:
        columns_to_sum.append('age_18_greater')
    
    if columns_to_sum:
        df = df.copy()
        df['filtered_total'] = df[columns_to_sum].sum(axis=1)
        return df
    return df


def filter_demographic_by_age(df, age_groups):
    """
    Filter demographic data by age groups.
    age_groups: list of selected age groups ['5-17 years', '17+ years']
    """
    columns_to_sum = []
    if '5-17 years' in age_groups:
        columns_to_sum.append('demo_age_5_17')
    if '17+ years' in age_groups:
        columns_to_sum.append('demo_age_17_')
    
    if columns_to_sum:
        df = df.copy()
        df['filtered_total'] = df[columns_to_sum].sum(axis=1)
        return df
    return df


def filter_biometric_by_age(df, age_groups):
    """
    Filter biometric data by age groups.
    age_groups: list of selected age groups ['5-17 years', '17+ years']
    """
    columns_to_sum = []
    if '5-17 years' in age_groups:
        columns_to_sum.append('bio_age_5_17')
    if '17+ years' in age_groups:
        columns_to_sum.append('bio_age_17_')
    
    if columns_to_sum:
        df = df.copy()
        df['filtered_total'] = df[columns_to_sum].sum(axis=1)
        return df
    return df


def detect_anomalies_iqr(df, column, multiplier=1.5):
    """
    Detect anomalies using IQR method.
    Returns dataframe with anomaly flag.
    """
    df = df.copy()
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    df['is_anomaly'] = (df[column] < lower_bound) | (df[column] > upper_bound)
    df['anomaly_type'] = np.where(
        df[column] > upper_bound, 'High',
        np.where(df[column] < lower_bound, 'Low', 'Normal')
    )
    
    return df, lower_bound, upper_bound


def get_summary_stats(df, value_column):
    """Get summary statistics for a value column."""
    return {
        'total': df[value_column].sum(),
        'mean': df[value_column].mean(),
        'median': df[value_column].median(),
        'std': df[value_column].std(),
        'min': df[value_column].min(),
        'max': df[value_column].max(),
        'count': len(df),
    }


def get_state_aggregation(df, value_column):
    """Aggregate data by state."""
    return df.groupby('state')[value_column].sum().reset_index().sort_values(
        value_column, ascending=False
    )


def get_district_aggregation(df, value_column):
    """Aggregate data by district."""
    return df.groupby(['state', 'district'])[value_column].sum().reset_index().sort_values(
        value_column, ascending=False
    )


def get_daily_trend(df, value_column):
    """Get daily trend data."""
    return df.groupby('date')[value_column].sum().reset_index().sort_values('date')


def get_weekly_trend(df, value_column):
    """Get weekly trend data."""
    df = df.copy()
    df['week'] = df['date'].dt.isocalendar().week
    df['year'] = df['date'].dt.year
    weekly = df.groupby(['year', 'week'])[value_column].sum().reset_index()
    return weekly


def get_monthly_trend(df, value_column):
    """Get monthly trend data."""
    df = df.copy()
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month')[value_column].sum().reset_index()
    monthly['month'] = monthly['month'].astype(str)
    return monthly


def format_number(num):
    """Format large numbers with suffixes."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.0f}"


def format_indian_number(num):
    """Format number in Indian numbering system (lakhs, crores)."""
    if num >= 10_000_000:
        return f"{num/10_000_000:.2f} Cr"
    elif num >= 100_000:
        return f"{num/100_000:.2f} L"
    elif num >= 1_000:
        return f"{num/1_000:.2f} K"
    else:
        return f"{num:.0f}"


def calculate_growth_rate(current, previous):
    """Calculate percentage growth rate."""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def get_top_n_regions(df, group_by, value_column, n=10):
    """Get top N regions by value."""
    aggregated = df.groupby(group_by)[value_column].sum().reset_index()
    return aggregated.nlargest(n, value_column)


def get_date_range(df):
    """Get min and max dates from dataframe."""
    min_date = df['date'].min()
    max_date = df['date'].max()
    return min_date, max_date


# ============================================================================
# WINNING FEATURES - Data Validation, Insights, Policy Modes
# ============================================================================

def calculate_data_quality_score(df, value_column):
    """
    Calculate a comprehensive data quality score.
    Returns score (0-100) and list of issues found.
    """
    issues = []
    score = 100
    
    # Check 1: Missing values
    null_count = df.isnull().sum().sum()
    total_cells = df.size
    null_pct = (null_count / total_cells) * 100
    if null_pct > 0:
        score -= min(null_pct * 2, 10)
        if null_pct > 1:
            issues.append(f"Missing values: {null_pct:.2f}%")
    
    # Check 2: Missing dates (gaps in date sequence)
    if 'date' in df.columns:
        dates = df['date'].dropna().sort_values().unique()
        if len(dates) > 1:
            date_range = pd.date_range(start=dates.min(), end=dates.max())
            missing_dates = len(date_range) - len(dates)
            if missing_dates > 0:
                missing_pct = (missing_dates / len(date_range)) * 100
                score -= min(missing_pct, 15)
                if missing_pct > 5:
                    issues.append(f"Missing date entries: {missing_dates} days")
    
    # Check 3: Zero/negative values detection
    if value_column in df.columns:
        zero_count = (df[value_column] <= 0).sum()
        zero_pct = (zero_count / len(df)) * 100
        if zero_pct > 5:
            score -= min(zero_pct / 2, 10)
            issues.append(f"Zero/negative values: {zero_pct:.1f}% of records")
    
    # Check 4: Duplicate rows
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        dup_pct = (duplicate_count / len(df)) * 100
        score -= min(dup_pct * 3, 15)
        if dup_pct > 1:
            issues.append(f"Duplicate rows: {duplicate_count:,}")
    
    # Check 5: Outlier detection (extreme spikes)
    if value_column in df.columns:
        Q1 = df[value_column].quantile(0.25)
        Q3 = df[value_column].quantile(0.75)
        IQR = Q3 - Q1
        extreme_outliers = ((df[value_column] < Q1 - 3*IQR) | (df[value_column] > Q3 + 3*IQR)).sum()
        outlier_pct = (extreme_outliers / len(df)) * 100
        if outlier_pct > 2:
            score -= min(outlier_pct, 10)
            issues.append(f"Extreme outliers: {extreme_outliers:,} records")
    
    # Check 6: State/Date uniqueness
    if 'state' in df.columns and 'date' in df.columns:
        state_date_dups = df.groupby(['state', 'date']).size()
        excessive_dups = (state_date_dups > state_date_dups.median() * 10).sum()
        if excessive_dups > 0:
            issues.append(f"Unusual state-date concentrations: {excessive_dups}")
    
    score = max(0, min(100, score))
    
    return round(score, 1), issues


def generate_intelligent_insights(enrolment_df, demographic_df, biometric_df):
    """
    Generate rule-based intelligent insights from data.
    Returns list of insight strings.
    """
    insights = []
    from datetime import timedelta
    
    # Insight 1: Week-over-week growth
    max_date = enrolment_df['date'].max()
    week_ago = max_date - timedelta(days=7)
    two_weeks_ago = max_date - timedelta(days=14)
    
    curr_enrol = enrolment_df[enrolment_df['date'] > week_ago]['total_enrolments'].sum()
    prev_enrol = enrolment_df[(enrolment_df['date'] > two_weeks_ago) & (enrolment_df['date'] <= week_ago)]['total_enrolments'].sum()
    
    if prev_enrol > 0:
        growth = ((curr_enrol - prev_enrol) / prev_enrol) * 100
        if growth > 10:
            insights.append(f"Enrolment activity surged by +{growth:.1f}% this week compared to previous week")
        elif growth < -10:
            insights.append(f"Enrolment activity decreased by {growth:.1f}% this week - possible operational slowdown")
        else:
            insights.append(f"Enrolment activity stable with {growth:+.1f}% week-over-week change")
    
    # Insight 2: Top performing state
    top_state = enrolment_df.groupby('state')['total_enrolments'].sum().idxmax()
    top_state_value = enrolment_df.groupby('state')['total_enrolments'].sum().max()
    total_enrol = enrolment_df['total_enrolments'].sum()
    top_pct = (top_state_value / total_enrol) * 100
    insights.append(f"{top_state} leads with {top_pct:.1f}% of total national enrolments")
    
    # Insight 3: Age group analysis
    child_enrol = enrolment_df['age_0_5'].sum() + enrolment_df['age_5_17'].sum()
    adult_enrol = enrolment_df['age_18_greater'].sum()
    child_pct = (child_enrol / total_enrol) * 100
    
    if child_pct > 30:
        insights.append(f"High child enrolment rate ({child_pct:.1f}%) indicates active school-based Aadhaar drives")
    else:
        insights.append(f"Adult enrolments dominate ({100-child_pct:.1f}%) - focus on new adult registrations")
    
    # Insight 4: Biometric vs Demographic comparison
    total_bio = biometric_df['total_bio_updates'].sum()
    total_demo = demographic_df['total_demo_updates'].sum()
    
    if total_bio > total_demo:
        ratio = total_bio / total_demo if total_demo > 0 else 0
        insights.append(f"Biometric updates exceed demographic updates by {ratio:.1f}x - likely due to mandatory revalidation")
    else:
        insights.append(f"Demographic updates higher than biometric - indicates address/name change demand")
    
    # Insight 5: Weekend pattern
    enrol_copy = enrolment_df.copy()
    enrol_copy['weekday'] = enrol_copy['date'].dt.dayofweek
    weekday_avg = enrol_copy[enrol_copy['weekday'] < 5].groupby('date')['total_enrolments'].sum().mean()
    weekend_avg = enrol_copy[enrol_copy['weekday'] >= 5].groupby('date')['total_enrolments'].sum().mean()
    
    if weekday_avg > 0 and weekend_avg > 0:
        drop = ((weekday_avg - weekend_avg) / weekday_avg) * 100
        insights.append(f"Weekend activity drops by {drop:.0f}% - centers operating at reduced capacity")
    
    # Insight 6: Peak detection
    daily_trend = enrolment_df.groupby('date')['total_enrolments'].sum()
    peak_date = daily_trend.idxmax()
    avg_daily = daily_trend.mean()
    peak_value = daily_trend.max()
    peak_ratio = peak_value / avg_daily if avg_daily > 0 else 0
    
    if peak_ratio > 2:
        insights.append(f"Peak activity on {peak_date.strftime('%d %b %Y')} was {peak_ratio:.1f}x normal - possible campaign or deadline")
    
    return insights


def get_policy_view_data(df, value_column, view_mode):
    """
    Transform data based on policy view mode.
    view_mode: 'citizen', 'administrator', 'policymaker'
    """
    if view_mode == 'citizen':
        # Simplified view - state level only
        return {
            'aggregation': 'state',
            'metrics': ['total', 'trend'],
            'detail_level': 'low',
            'focus': 'accessibility_status'
        }
    elif view_mode == 'administrator':
        # Operational view - district level
        return {
            'aggregation': 'district',
            'metrics': ['total', 'daily_avg', 'peak', 'capacity'],
            'detail_level': 'medium',
            'focus': 'operational_efficiency'
        }
    else:  # policymaker
        # Strategic view - regional analysis
        return {
            'aggregation': 'region',
            'metrics': ['total', 'growth', 'anomalies', 'projections'],
            'detail_level': 'high',
            'focus': 'policy_impact'
        }


def get_security_compliance_info():
    """
    Return security and compliance information.
    """
    return {
        "data_handling": [
            "No Personally Identifiable Information (PII) processed",
            "Aggregated statistics only - no individual records",
            "Open Data Policy compliant datasets",
            "Data processed locally - no external transmission"
        ],
        "compliance": [
            "Aligned with MeitY Open Government Data guidelines",
            "UIDAI Data Sharing Policy adherent",
            "Statistical analysis on anonymized aggregates only"
        ],
        "technical": [
            "Cached aggregations for optimal performance",
            "Lazy loading for national-scale datasets",
            "Memory-efficient pandas operations"
        ]
    }


def get_performance_stats(df):
    """
    Get performance and scale statistics.
    """
    return {
        "total_records": len(df),
        "data_size_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
        "columns": len(df.columns),
        "states_covered": df['state'].nunique() if 'state' in df.columns else 0,
        "date_range_days": (df['date'].max() - df['date'].min()).days if 'date' in df.columns else 0,
        "optimization_notes": [
            "Streamlit @st.cache_data for repeated queries",
            "Lazy loading on page navigation",
            "Aggregated computations cached for 1 hour"
        ]
    }
