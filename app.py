"""
UIDAI Data Hackathon 2026 - Main Application
Aadhaar Enrolment & Update Analytics Platform

Team ID: UIDAI_815
Developer: Karthik
"""

import streamlit as st
import base64
import os

# Import styles
from styles import get_main_styles, COLORS

# Import page modules (renamed from pages to avoid Streamlit auto-detection)
from page_modules.dashboard import render_dashboard
from page_modules.enrolment import render_enrolment
from page_modules.demographics import render_demographics
from page_modules.biometrics import render_biometrics
from page_modules.anomaly_detection import render_anomaly_detection
from page_modules.reports import render_reports

# Page configuration with India flag favicon
st.set_page_config(
    page_title="AadhaarInsight360 | Digital Identity Analytics",
    page_icon="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
st.markdown(get_main_styles(), unsafe_allow_html=True)


def get_base64_image(image_path):
    """Convert image to base64 for embedding."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


def render_sidebar():
    """Render the sidebar with navigation and profile."""
    with st.sidebar:
        # UIDAI Logo - compact
        logo_path = os.path.join(os.path.dirname(__file__), "uidai_logo.png")
        logo_base64 = get_base64_image(logo_path)
        
        if logo_base64:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem 0.5rem 0.75rem 0.5rem; border-bottom: 1px solid {COLORS['border']}; margin-bottom: 0.5rem;">
                <img src="data:image/png;base64,{logo_base64}" style="max-width: 120px; height: auto;">
                <div style="color: {COLORS['text_primary']}; font-size: 0.75rem; font-weight: 600; margin-top: 0.25rem;">
                    Data Hackathon 2026
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation
        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Enrolment Analysis",
                "Demographics Analysis",
                "Biometrics Analysis",
                "Anomaly Detection",
                "Reports"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Profile section - compact with proper icons
        profile_path = os.path.join(os.path.dirname(__file__), "profile.jpeg")
        profile_base64 = get_base64_image(profile_path)
        
        profile_img = f'<img src="data:image/jpeg;base64,{profile_base64}" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid {COLORS["accent_primary"]}; object-fit: cover;">' if profile_base64 else f'<div style="width: 60px; height: 60px; border-radius: 50%; background-color: {COLORS["accent_primary"]}; margin: 0 auto; display: flex; align-items: center; justify-content: center; color: {COLORS["text_primary"]}; font-size: 1.5rem; font-weight: 600;">K</div>'
        
        st.markdown(f"""
        <div style="background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; 
                    border-radius: 10px; padding: 0.75rem; text-align: center;">
            {profile_img}
            <div style="color: {COLORS['text_primary']}; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">
                Karthik
            </div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.7rem;">
                Solo Developer
            </div>
            <div style="background-color: {COLORS['accent_primary']}; color: {COLORS['text_primary']}; 
                        padding: 0.2rem 0.6rem; border-radius: 15px; font-size: 0.65rem; 
                        font-weight: 600; display: inline-block; margin: 0.4rem 0;">
                UIDAI_815
            </div>
            <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 0.4rem;">
                <a href="https://github.com/Nytrynox/Karthik" target="_blank" title="GitHub"
                   style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: 1.1rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                </a>
                <a href="https://www.linkedin.com/in/karthik129259/" target="_blank" title="LinkedIn"
                   style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: 1.1rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                    </svg>
                </a>
                <a href="tel:+919494432697" title="Phone"
                   style="color: {COLORS['text_secondary']}; text-decoration: none; font-size: 1.1rem;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                    </svg>
                </a>
            </div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.65rem; margin-top: 0.25rem;">
                +91 9494432697
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return page


def main():
    """Main application entry point."""
    # Render sidebar and get selected page
    selected_page = render_sidebar()
    
    # Render selected page
    if selected_page == "Dashboard":
        render_dashboard()
    elif selected_page == "Enrolment Analysis":
        render_enrolment()
    elif selected_page == "Demographics Analysis":
        render_demographics()
    elif selected_page == "Biometrics Analysis":
        render_biometrics()
    elif selected_page == "Anomaly Detection":
        render_anomaly_detection()
    elif selected_page == "Reports":
        render_reports()


if __name__ == "__main__":
    main()
