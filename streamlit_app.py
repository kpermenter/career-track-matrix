"""
Engineering Growth Framework - Home Page
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="Overview",
        page_icon="📋",
        layout="wide"
    )

    # JavaScript to override sidebar navigation link text
    st.markdown("""
    <script>
    function updateSidebarLabel() {
        // Find the span with label="streamlit app"
        const spans = document.querySelectorAll('span[label="streamlit app"]');
        spans.forEach(span => {
            if (span.textContent === 'streamlit app') {
                span.textContent = '📋 Overview';
                span.setAttribute('label', 'Overview');
            }
        });

        // Alternative approach - find spans containing "streamlit app"
        const allSpans = document.querySelectorAll('span');
        allSpans.forEach(span => {
            if (span.textContent === 'streamlit app') {
                span.textContent = '📋 Overview';
            }
        });
    }

    // Run immediately
    updateSidebarLabel();

    // Run when DOM changes (for dynamic updates)
    const observer = new MutationObserver(function(mutations) {
        updateSidebarLabel();
    });

    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Also run after a short delay to catch late-loading elements
    setTimeout(updateSidebarLabel, 100);
    setTimeout(updateSidebarLabel, 500);
    setTimeout(updateSidebarLabel, 1000);
    </script>
    """, unsafe_allow_html=True)

    st.title("Engineering Growth Framework")
    st.caption("A comprehensive framework for engineering career development and progression.")

    st.markdown("""
    ## Welcome to the Engineering Growth Framework

    This application provides two complementary views of our engineering career framework:

    ### 📊 Competencies View
    - **Layout**: Competencies/sections as tabs, levels within each section
    - **Best for**: Understanding what's expected at each level for a specific competency
    - **Features**: Compare mode, advanced filtering, search functionality

    ### 🧭 Levels View
    - **Layout**: Levels as tabs, competencies within each level
    - **Best for**: Understanding the complete scope of a specific level
    - **Features**: Same filtering and functionality as Competencies View

    ---

    **👈 Use the sidebar navigation to explore both views!**

    Both views support:
    - 🔍 Advanced filtering by levels, scopes, and audience impact
    - 🔎 Full-text search across all content
    - 📥 CSV export of filtered data
    - 📊 Interactive impact badges showing scope and audience
    """)

    # Add some helpful stats or info
    st.markdown("""
    ### 🎯 Framework Overview

    - **7 Engineering Levels**: L1 through L7
    - **10 Competency Dimensions**: From technical skills to leadership
    - **5 Impact Scopes**: Pod to Organization-wide influence
    - **4 Audience Types**: From peers to executive leadership
    """)

if __name__ == "__main__":
    main()