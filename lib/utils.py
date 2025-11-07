"""
Shared utilities for the Engineering Growth Framework Streamlit app.
Contains data loading, UI components, and helper functions.
"""

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

# Level titles mapping
LEVEL_TITLES = {
    'L1': 'Junior Engineer',
    'L2': 'Engineer',
    'L3': 'Senior Engineer',
    'L4': 'Staff Engineer',
    'L5': 'Senior Staff Engineer',
    'L6': 'Principal Engineer',
    'L7': 'Architect'
}

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

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

@st.cache_data
def load_matrix_table(file_path: str = None, uploaded_file=None) -> pd.DataFrame:
    """
    Load and normalize engineering career track matrix data with impact columns.
    Returns DataFrame with: level, section, prefix, body, examples, pod_type, scope, impact_icons, impact_audience, impact_summary
    """

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

    # Load the data
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

    # Process data
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
        return pd.DataFrame(columns=['level', 'section', 'prefix', 'body', 'examples', 'pod_type', 'scope', 'impact_icons', 'impact_audience', 'impact_summary', 'level_title'])

    # Ensure all required columns exist
    required_columns = ['level', 'section', 'prefix', 'body', 'examples', 'pod_type']
    for col in required_columns:
        if col not in result_df.columns:
            result_df[col] = ""
        result_df[col] = result_df[col].astype(str).fillna("").str.strip()

    # Add impact columns
    result_df = add_impact_columns(result_df)

    # Add level titles
    result_df['level_title'] = result_df['level'].map(LEVEL_TITLES).fillna(result_df['level'])

    # Debug print for validation
    level_mapping = result_df[['level', 'level_title']].drop_duplicates().sort_values('level')
    print("Level mapping validation:")
    print(level_mapping)

    # Set up proper ordering
    level_order = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    result_df['level'] = pd.Categorical(result_df['level'], categories=level_order, ordered=True)
    result_df['section'] = pd.Categorical(result_df['section'], categories=CANONICAL_SECTIONS, ordered=True)

    # Sort by section then level
    result_df = result_df.sort_values(['section', 'level']).reset_index(drop=True)

    return result_df

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_legend():
    """Render the impact legend"""
    with st.expander("Legend: Scope of Impact", expanded=False):
        st.write("👥 Peers")
        st.write("🤝 Product, Design, QA")
        st.write("🏗 Engineering Leadership")
        st.write("🎯 Executive Leadership")

        st.markdown("### Operating Scope")
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
# QUERY PARAMETER HELPERS
# =============================================================================

# Query param helpers (using modern st.query_params only)
def qp_get(name: str, default: str = "") -> str:
    """Get query parameter value as string"""
    try:
        return st.query_params.get(name, default) or default
    except:
        return default

def qp_set(updates: dict) -> None:
    """Set query parameter values"""
    try:
        for k, v in updates.items():
            if v:  # Only set non-empty values
                st.query_params[k] = str(v)
    except:
        pass  # Silently fail if query params don't work

# =============================================================================
# CSS STYLING
# =============================================================================

def inject_custom_css():
    """Inject custom CSS for the app"""
    st.markdown("""
    <style>
        /* Main styling */
        .main-header {
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            border-bottom: 2px solid #e0e0e0;
        }

        .level-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            background-color: var(--background-color);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .level-header {
            font-size: 1.3rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #1f77b4;
        }

        .prefix-text {
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .body-text {
            line-height: 1.8;
            margin-bottom: 1rem;
            text-align: justify;
        }

        .examples-section {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            border-left: 4px solid #28a745;
            margin-top: 1rem;
        }

        .pod-type-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 0.5rem;
        }

        .pod-badge { background-color: #e3f2fd; color: #1976d2; }
        .cross-pod-badge { background-color: #f3e5f5; color: #7b1fa2; }
        .platform-badge { background-color: #e8f5e8; color: #388e3c; }
        .cross-platform-badge { background-color: #fff3e0; color: #f57c00; }

        /* Print-friendly styles */
        @media print {
            .stSidebar { display: none !important; }
            .main-header { border-bottom: 2px solid #000; }
            .level-card {
                border: 1px solid #000;
                box-shadow: none;
                page-break-inside: avoid;
                margin: 0.5rem 0;
            }
            .level-header {
                color: #000 !important;
                border-bottom: 1px solid #000;
            }
            .examples-section {
                background-color: #f5f5f5;
                border-left: 2px solid #000;
            }
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .level-card {
                background-color: #1e1e1e;
                border-color: #444;
            }
            .examples-section {
                background-color: #2d2d2d;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def print_validation_info(df: pd.DataFrame):
    """Print validation information for debugging"""
    if df.empty:
        st.warning("DataFrame is empty")
        return

    # Level-impact mapping validation
    validation_df = df[["level","scope","impact_icons","impact_audience"]].drop_duplicates().sort_values("level")
    st.write("**Level Impact & Scope Summary:**")
    st.dataframe(validation_df)

    # Section × Level count
    count_df = df.groupby(['section', 'level'], observed=False).size().reset_index(name='count')
    st.write("**Competency Coverage by Level:**")
    st.dataframe(count_df)

    st.write(f"**Total items:** {len(df)}")
    st.write(f"**Competency dimensions:** {len(df['section'].dropna().unique())}")
    st.write(f"**Engineering levels:** {len(df['level'].dropna().unique())}")