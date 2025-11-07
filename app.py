import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from typing import Dict, List, Optional, Union
from difflib import get_close_matches

# =============================================================================
# IMPACT MAPPING CONFIGURATION
# =============================================================================

# Level impact mapping based on your framework
LEVEL_IMPACT_MAPPING = {
    'L1': {
        'scope': 'Pod',
        'impact_icons': '👥',
        'impact_audience': 'Peers',
        'impact_summary': 'Pod scope — peers'
    },
    'L2': {
        'scope': 'Pod',
        'impact_icons': '👥🤝',
        'impact_audience': 'Peers, Product/Design/QA',
        'impact_summary': 'Pod scope — peers + product/design/QA'
    },
    'L3': {
        'scope': 'Pod',
        'impact_icons': '👥🤝',
        'impact_audience': 'Peers, Product/Design/QA',
        'impact_summary': 'Pod scope — peers + product/design/QA'
    },
    'L4': {
        'scope': 'Cross-Pod',
        'impact_icons': '👥🤝🏗',
        'impact_audience': 'Peers, Product/Design/QA, Engineering Leadership',
        'impact_summary': 'Cross-Pod scope — peers + product/design/QA + eng leadership'
    },
    'L5': {
        'scope': 'Platform',
        'impact_icons': '👥🤝🏗',
        'impact_audience': 'Peers, Product/Design/QA, Engineering Leadership',
        'impact_summary': 'Platform scope — peers + product/design/QA + eng leadership'
    },
    'L6': {
        'scope': 'Cross-Platform',
        'impact_icons': '👥🤝🏗🎯',
        'impact_audience': 'Peers, Product/Design/QA, Engineering Leadership, Executive Leadership',
        'impact_summary': 'Cross-Platform scope — peers + product/design/QA + eng + exec leadership'
    },
    'L7': {
        'scope': 'Org-Wide',
        'impact_icons': '👥🤝🏗🎯',
        'impact_audience': 'Peers, Product/Design/QA, Engineering Leadership, Executive Leadership',
        'impact_summary': 'Org-Wide scope — peers + product/design/QA + eng + exec leadership'
    }
}

# Icon meanings for legend
ICON_LEGEND = {
    '👥': 'Peers',
    '🤝': 'Product, Design, QA',
    '🏗': 'Engineering Leadership',
    '🎯': 'Executive Leadership'
}

# =============================================================================
# ENHANCED DATA LOADER WITH IMPACT COLUMNS
# =============================================================================

@st.cache_data
def load_matrix_table_with_impact(file_path: str = None, uploaded_file=None) -> pd.DataFrame:
    """
    Load and normalize engineering career track matrix data with impact columns.
    Returns DataFrame with: level, section, prefix, body, examples, pod_type, scope, impact_icons, impact_audience, impact_summary
    """

    # Canonical section names (in framework order)
    CANONICAL_SECTIONS = [
        "Experience Overview",
        "Technical Aptitude & Skills",
        "AI Fluency",
        "Scope & Impact",
        "Ownership & Accountability",
        "Planning & Project Management",
        "Product Awareness, User Empathy, and Design Thinking",
        "Collaboration, Communication, and Conflict Resolution",
        "Community & Mentorship",
        "Values in Action"
    ]

    # Section aliases for fuzzy matching
    SECTION_ALIASES = {
        # Experience variations
        "experience": "Experience Overview",
        "exp overview": "Experience Overview",
        "experience_overview": "Experience Overview",

        # Technical variations
        "technical": "Technical Aptitude & Skills",
        "tech skills": "Technical Aptitude & Skills",
        "technical_aptitude": "Technical Aptitude & Skills",
        "aptitude": "Technical Aptitude & Skills",

        # AI variations
        "ai": "AI Fluency",
        "artificial intelligence": "AI Fluency",
        "ai_fluency": "AI Fluency",

        # Scope variations
        "scope": "Scope & Impact",
        "impact": "Scope & Impact",
        "scope_impact": "Scope & Impact",

        # Ownership variations
        "ownership": "Ownership & Accountability",
        "accountability": "Ownership & Accountability",
        "ownership_accountability": "Ownership & Accountability",
        "account": "Ownership & Accountability",

        # Planning variations
        "planning": "Planning & Project Management",
        "project": "Planning & Project Management",
        "project management": "Planning & Project Management",
        "planning_project": "Planning & Project Management",

        # Collaboration variations
        "collaboration": "Collaboration, Communication, and Conflict Resolution",
        "communication": "Collaboration, Communication, and Conflict Resolution",
        "collab": "Collaboration, Communication, and Conflict Resolution",
        "comm": "Collaboration, Communication, and Conflict Resolution",
        "conflict": "Collaboration, Communication, and Conflict Resolution",
        "conflict resolution": "Collaboration, Communication, and Conflict Resolution",

        # Product/Design variations
        "product": "Product Awareness, User Empathy, and Design Thinking",
        "product awareness": "Product Awareness, User Empathy, and Design Thinking",
        "user empathy": "Product Awareness, User Empathy, and Design Thinking",
        "design thinking": "Product Awareness, User Empathy, and Design Thinking",
        "design": "Product Awareness, User Empathy, and Design Thinking",
        "empathy": "Product Awareness, User Empathy, and Design Thinking",

        # Community variations
        "community": "Community & Mentorship",
        "mentorship": "Community & Mentorship",
        "mentor": "Community & Mentorship",

        # Values variations
        "values": "Values in Action",
        "values_action": "Values in Action",
        "action": "Values in Action"
    }

    def normalize_section_name(section_name: str) -> str:
        """Normalize section names using canonical labels and fuzzy matching"""
        if pd.isna(section_name) or not section_name:
            return ""

        section_clean = str(section_name).strip().lower()

        # Direct alias match
        if section_clean in SECTION_ALIASES:
            return SECTION_ALIASES[section_clean]

        # Fuzzy match against canonical sections
        matches = get_close_matches(section_clean,
                                  [s.lower() for s in CANONICAL_SECTIONS],
                                  n=1, cutoff=0.6)
        if matches:
            for canonical in CANONICAL_SECTIONS:
                if canonical.lower() == matches[0]:
                    return canonical

        # Fuzzy match against aliases
        alias_matches = get_close_matches(section_clean,
                                        list(SECTION_ALIASES.keys()),
                                        n=1, cutoff=0.7)
        if alias_matches:
            return SECTION_ALIASES[alias_matches[0]]

        return str(section_name).strip()

    def clean_text_field(value) -> str:
        """Clean and normalize text fields"""
        if pd.isna(value) or value is None:
            return ""
        if isinstance(value, (int, float)):
            if pd.isna(value):
                return ""
            return str(value).strip()
        return str(value).strip()

    def extract_level(text: str) -> str:
        """Extract level (L1-L7) from text"""
        if not text:
            return ""
        level_match = re.search(r'L\s*([1-7])', str(text), re.IGNORECASE)
        if level_match:
            return f"L{level_match.group(1)}"
        return ""

    def add_impact_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add impact-related columns based on level"""
        df = df.copy()

        # Initialize impact columns
        df['scope'] = ""
        df['impact_icons'] = ""
        df['impact_audience'] = ""
        df['impact_summary'] = ""

        # Apply impact mapping for each level
        for idx, row in df.iterrows():
            level = row.get('level', '')
            if level in LEVEL_IMPACT_MAPPING:
                mapping = LEVEL_IMPACT_MAPPING[level]
                df.at[idx, 'scope'] = mapping['scope']
                df.at[idx, 'impact_icons'] = mapping['impact_icons']
                df.at[idx, 'impact_audience'] = mapping['impact_audience']
                df.at[idx, 'impact_summary'] = mapping['impact_summary']

        return df

    # Load the data (using existing logic from previous version)
    df = None
    try:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                try:
                    excel_data = pd.read_excel(uploaded_file, sheet_name=None)
                    if len(excel_data) == 1:
                        df = list(excel_data.values())[0]
                    else:
                        dfs = []
                        for sheet_name, sheet_df in excel_data.items():
                            sheet_df = sheet_df.copy()
                            if 'section' not in sheet_df.columns:
                                sheet_df['section'] = sheet_name
                            dfs.append(sheet_df)
                        df = pd.concat(dfs, ignore_index=True)
                except:
                    df = pd.read_excel(uploaded_file)

        elif file_path and os.path.exists(file_path):
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                try:
                    excel_data = pd.read_excel(file_path, sheet_name=None)
                    if len(excel_data) == 1:
                        df = list(excel_data.values())[0]
                    else:
                        dfs = []
                        for sheet_name, sheet_df in excel_data.items():
                            sheet_df = sheet_df.copy()
                            if 'section' not in sheet_df.columns:
                                sheet_df['section'] = sheet_name
                            dfs.append(sheet_df)
                        df = pd.concat(dfs, ignore_index=True)
                except:
                    df = pd.read_excel(file_path)
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return pd.DataFrame()

    if df is None or df.empty:
        return pd.DataFrame()

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Process data (same logic as before)
    result_data = []

    for idx, row in df.iterrows():
        if row.isna().all():
            continue

        # Extract level
        level = ""
        for col in df.columns:
            if any(keyword in col for keyword in ['level', 'lvl', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']):
                level = extract_level(clean_text_field(row[col]))
                if level:
                    break

        if not level:
            for col in df.columns:
                level = extract_level(clean_text_field(row[col]))
                if level:
                    break

        if not level:
            continue

        # Extract section
        section = ""
        for col in df.columns:
            if 'section' in col:
                section = clean_text_field(row[col])
                break
        section = normalize_section_name(section)

        # Extract other fields
        prefix = ""
        body = ""
        examples = ""
        pod_type = ""

        for col in df.columns:
            if any(keyword in col for keyword in ['prefix', 'title', 'heading']):
                prefix = clean_text_field(row[col])
                break

        for col in df.columns:
            if any(keyword in col for keyword in ['body', 'description', 'content', 'text']):
                body = clean_text_field(row[col])
                break

        for col in df.columns:
            if any(keyword in col for keyword in ['example', 'sample']):
                examples = clean_text_field(row[col])
                break

        for col in df.columns:
            if any(keyword in col for keyword in ['pod', 'type', 'category']):
                pod_type = clean_text_field(row[col])
                break

        # If no specific columns found, extract from any text
        if not prefix and not body:
            text_content = ""
            for col in df.columns:
                if col not in ['level', 'section'] and not pd.isna(row[col]):
                    text_content += " " + clean_text_field(row[col])

            text_content = text_content.strip()
            if text_content:
                sentences = re.split(r'[.!?]\s+', text_content, maxsplit=1)
                if len(sentences) >= 2:
                    prefix = sentences[0].strip()
                    body = sentences[1].strip()
                else:
                    body = text_content

        result_data.append({
            'level': level,
            'section': section,
            'prefix': prefix,
            'body': body,
            'examples': examples,
            'pod_type': pod_type
        })

    # Create DataFrame
    result_df = pd.DataFrame(result_data)

    if result_df.empty:
        return pd.DataFrame(columns=['level', 'section', 'prefix', 'body', 'examples', 'pod_type', 'scope', 'impact_icons', 'impact_audience', 'impact_summary'])

    # Ensure all required columns exist
    required_columns = ['level', 'section', 'prefix', 'body', 'examples', 'pod_type']
    for col in required_columns:
        if col not in result_df.columns:
            result_df[col] = ""
        result_df[col] = result_df[col].astype(str).fillna("").str.strip()

    # Add impact columns
    result_df = add_impact_columns(result_df)

    # Set up proper ordering
    level_order = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    result_df['level'] = pd.Categorical(result_df['level'], categories=level_order, ordered=True)
    result_df['section'] = pd.Categorical(result_df['section'], categories=CANONICAL_SECTIONS, ordered=True)

    # Sort by section then level
    result_df = result_df.sort_values(['section', 'level']).reset_index(drop=True)

    return result_df

# =============================================================================
# UI COMPONENTS FOR IMPACT DISPLAY
# =============================================================================

def render_legend():
    """Render the impact legend"""
    with st.expander("📊 Legend: Level of Impact", expanded=False):
        st.markdown("### Impact Scope & Audience")
        for icon, meaning in ICON_LEGEND.items():
            st.write(f"{icon} {meaning}")

        st.markdown("### Scope Types")
        st.write("• **Pod** — Working within your immediate team")
        st.write("• **Cross-Pod** — Collaborating across multiple pods")
        st.write("• **Platform** — Influencing platform-wide decisions")
        st.write("• **Cross-Platform** — Impact across multiple platforms")
        st.write("• **Org-Wide** — Organization-wide influence")

def render_scope_badge(scope: str, icons: str, audience: str, summary: str):
    """Render scope badge with impact information"""
    if not scope or not icons:
        return

    # Create badge with accessibility
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"**{scope}** &nbsp; {icons}")
        # Accessibility text
        st.caption(f"Audience: {audience}")

    with col3:
        with st.popover("ℹ️ What this means"):
            st.write(summary)
            st.write(f"**Audiences:** {audience}")

def filter_by_minimum_audience(df: pd.DataFrame, min_icons: List[str]) -> pd.DataFrame:
    """Filter DataFrame by minimum audience requirements"""
    if not min_icons:
        return df

    filtered_df = df.copy()
    for icon in min_icons:
        filtered_df = filtered_df[filtered_df['impact_icons'].str.contains(icon, na=False)]

    return filtered_df

# =============================================================================
# QUERY PARAMETER HELPERS (from previous version)
# =============================================================================

def qp_get(name: str, default: Union[str, List[str]] = "") -> Union[str, List[str]]:
    """Safely get query parameter value"""
    try:
        if hasattr(st, 'query_params'):
            value = st.query_params.get(name, default)
            if isinstance(default, list) and isinstance(value, str):
                return [value] if value else default
            return value if value else default
        elif hasattr(st, 'experimental_get_query_params'):
            params = st.experimental_get_query_params()
            value = params.get(name, [default] if not isinstance(default, list) else default)
            if isinstance(default, list):
                return value if isinstance(value, list) else [value]
            else:
                return value[0] if isinstance(value, list) and len(value) > 0 else default
        else:
            return default
    except Exception:
        return default

def qp_set(updates: Dict[str, Union[str, List[str]]]):
    """Safely set query parameter values"""
    try:
        if hasattr(st, 'query_params'):
            for key, value in updates.items():
                if value:
                    if isinstance(value, list):
                        st.query_params[key] = ','.join(str(v) for v in value if v)
                    else:
                        st.query_params[key] = str(value)
        elif hasattr(st, 'experimental_set_query_params'):
            params = {}
            for key, value in updates.items():
                if value:
                    if isinstance(value, list):
                        params[key] = [str(v) for v in value if v]
                    else:
                        params[key] = [str(value)]
            if params:
                st.experimental_set_query_params(**params)
    except Exception:
        pass

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    st.set_page_config(
        page_title="Engineering Career Track Matrix",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🚀 Engineering Career Track Matrix")

    # Render legend at the top
    render_legend()

    # =============================================================================
    # DATA LOADING SECTION
    # =============================================================================

    st.sidebar.header("📁 Load Data")

    load_option = st.sidebar.radio(
        "Data source:",
        ["Upload file", "Local path"],
        help="Choose whether to upload a file or use a local path"
    )

    df = pd.DataFrame()

    if load_option == "Upload file":
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your normalized career track matrix file"
        )
        if uploaded_file:
            df = load_matrix_table_with_impact(uploaded_file=uploaded_file)

    else:
        default_csv = os.path.expanduser("~/Desktop/matrix_streamlit.csv")
        default_excel = os.path.expanduser("~/Desktop/2025H1 Engineering Career Track (1).xlsx")

        file_path = st.sidebar.text_input(
            "File path:",
            value=default_csv if os.path.exists(default_csv) else default_excel,
            help="Enter the path to your CSV or Excel file"
        )
        if file_path and os.path.exists(file_path):
            df = load_matrix_table_with_impact(file_path=file_path)

    # =============================================================================
    # VALIDATION & DEBUG
    # =============================================================================

    if df.empty:
        st.info("👆 Please load a file to view the career track matrix")
        return

    # Get unique values for filters (preserve canonical ordering)
    levels = sorted(df['level'].dropna().unique().tolist())
    unique_sections = df['section'].dropna().unique().tolist()
    sections = [s for s in [
        "Experience Overview",
        "Technical Aptitude & Skills",
        "AI Fluency",
        "Scope & Impact",
        "Ownership & Accountability",
        "Planning & Project Management",
        "Product Awareness, User Empathy, and Design Thinking",
        "Collaboration, Communication, and Conflict Resolution",
        "Community & Mentorship",
        "Values in Action"
    ] if s in unique_sections]
    scopes = sorted([s for s in df['scope'].dropna().unique().tolist() if s])

    # Validation output
    st.subheader("🔍 Data Validation")
    with st.expander("Impact mapping validation", expanded=False):
        st.write("**Level-Impact mapping:**")
        validation_df = df[["level","scope","impact_icons","impact_audience"]].drop_duplicates().sort_values("level")
        st.dataframe(validation_df)

        st.write("**Section × Level count:**")
        count_df = df.groupby(['section', 'level']).size().reset_index(name='count')
        st.dataframe(count_df)

        st.write(f"**Total rows:** {len(df)}")
        st.write(f"**Unique sections:** {len(sections)}")
        st.write(f"**Unique levels:** {len(levels)}")

    # =============================================================================
    # ENHANCED FILTERS
    # =============================================================================

    st.sidebar.header("🔍 Filters")

    # Level filter
    default_levels = qp_get('levels', levels)
    if isinstance(default_levels, str):
        default_levels = default_levels.split(',') if default_levels else levels

    selected_levels = st.sidebar.multiselect(
        "Select Levels:",
        levels,
        default=[lvl for lvl in default_levels if lvl in levels],
        help="Choose which engineering levels to display"
    )

    # Scope filter
    default_scopes = qp_get('scopes', [])
    if isinstance(default_scopes, str):
        default_scopes = default_scopes.split(',') if default_scopes else []

    selected_scopes = st.sidebar.multiselect(
        "Scope Types:",
        scopes,
        default=[scope for scope in default_scopes if scope in scopes],
        help="Filter by impact scope"
    )

    # Minimum audience filter
    st.sidebar.markdown("**Minimum Audience:**")
    audience_filters = []

    if st.sidebar.checkbox("👥 Peers", help="Show levels that impact peers"):
        audience_filters.append("👥")
    if st.sidebar.checkbox("🤝 Product/Design/QA", help="Show levels that impact product teams"):
        audience_filters.append("🤝")
    if st.sidebar.checkbox("🏗 Engineering Leadership", help="Show levels that impact eng leadership"):
        audience_filters.append("🏗")
    if st.sidebar.checkbox("🎯 Executive Leadership", help="Show levels that impact exec leadership"):
        audience_filters.append("🎯")

    # Search filter
    search_term = st.sidebar.text_input(
        "🔎 Search:",
        value=qp_get('search', ''),
        help="Search in prefix, body, or examples"
    )

    # Compare mode
    compare_mode = st.sidebar.checkbox(
        "📊 Compare Mode",
        value=False,
        help="Side-by-side comparison of two levels"
    )

    # Update query params
    qp_set({
        'levels': selected_levels,
        'scopes': selected_scopes,
        'search': search_term
    })

    # =============================================================================
    # APPLY FILTERS
    # =============================================================================

    filtered_df = df.copy()

    if selected_levels:
        filtered_df = filtered_df[filtered_df['level'].isin(selected_levels)]

    if selected_scopes:
        filtered_df = filtered_df[filtered_df['scope'].isin(selected_scopes)]

    if audience_filters:
        filtered_df = filter_by_minimum_audience(filtered_df, audience_filters)

    if search_term:
        search_mask = (
            filtered_df['prefix'].str.contains(search_term, case=False, na=False) |
            filtered_df['body'].str.contains(search_term, case=False, na=False) |
            filtered_df['examples'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]

    st.sidebar.write(f"**{len(filtered_df)} items match filters**")

    # CSV download
    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False)
        st.sidebar.download_button(
            "📥 Download filtered CSV",
            data=csv_data,
            file_name="career_track_filtered.csv",
            mime="text/csv"
        )

    # =============================================================================
    # DISPLAY WITH IMPACT BADGES
    # =============================================================================

    if filtered_df.empty:
        st.warning("No data matches your current filters.")
        return

    if compare_mode:
        st.subheader("📊 Compare Mode")

        col1, col2 = st.columns(2)

        with col1:
            level1 = st.selectbox("First level:", levels, key="compare_level1")
        with col2:
            level2 = st.selectbox("Second level:", levels, key="compare_level2",
                                 index=min(1, len(levels)-1))

        if level1 and level2 and level1 != level2:
            for section in sections:
                section_data = filtered_df[filtered_df['section'] == section]
                if section_data.empty:
                    continue

                st.subheader(f"📋 {section}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"### {level1}")
                    level1_data = section_data[section_data['level'] == level1]
                    for _, row in level1_data.iterrows():
                        # Render badge first
                        render_scope_badge(row['scope'], row['impact_icons'],
                                         row['impact_audience'], row['impact_summary'])

                        # Then content
                        if row['prefix']:
                            st.write(f"**{row['prefix']}**")
                        if row['body']:
                            st.write(row['body'])
                        if row['examples'] and row['examples'] != 'nan':
                            with st.expander("📝 Examples"):
                                st.write(row['examples'])

                with col2:
                    st.markdown(f"### {level2}")
                    level2_data = section_data[section_data['level'] == level2]
                    for _, row in level2_data.iterrows():
                        # Render badge first
                        render_scope_badge(row['scope'], row['impact_icons'],
                                         row['impact_audience'], row['impact_summary'])

                        # Then content
                        if row['prefix']:
                            st.write(f"**{row['prefix']}**")
                        if row['body']:
                            st.write(row['body'])
                        if row['examples'] and row['examples'] != 'nan':
                            with st.expander("📝 Examples"):
                                st.write(row['examples'])

                st.divider()

    else:
        # Regular tabbed view
        if sections:
            tabs = st.tabs([f"📋 {section}" for section in sections])

            for i, section in enumerate(sections):
                with tabs[i]:
                    section_data = filtered_df[filtered_df['section'] == section]

                    if section_data.empty:
                        st.info(f"No data available for {section} with current filters.")
                        continue

                    # Sort by level
                    section_data = section_data.sort_values('level')

                    for _, row in section_data.iterrows():
                        st.markdown(f"### {row['level']}")

                        # Render scope badge
                        render_scope_badge(row['scope'], row['impact_icons'],
                                         row['impact_audience'], row['impact_summary'])

                        # Content
                        if row['prefix']:
                            st.write(f"**{row['prefix']}**")
                        if row['body']:
                            st.write(row['body'])
                        if row['examples'] and row['examples'] != 'nan':
                            with st.expander("📝 Examples"):
                                st.write(row['examples'])
                        if row['pod_type']:
                            st.caption(f"🏷️ Pod Type: {row['pod_type']}")

                        st.divider()

if __name__ == "__main__":
    main()