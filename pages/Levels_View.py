"""
Engineering Growth Framework - Levels View
Displays levels as tabs with sections (dimensions) inside each tab.
"""

import streamlit as st
import pandas as pd
import os
import sys

# Add lib directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lib.utils import (
    load_matrix_table,
    render_legend,
    render_scope_badge,
    filter_by_minimum_audience,
    qp_get,
    qp_set,
    inject_custom_css,
    print_validation_info,
    CANONICAL_SECTIONS,
    ICON_LEGEND,
    LEVEL_TITLES
)

def main():
    st.set_page_config(
        page_title="Levels View",
        page_icon="🧭",
        layout="wide"
    )

    # Inject custom CSS
    inject_custom_css()

    st.title("Levels View")
    st.caption("Explore competencies by level and scope of impact.")

    # Render legend at the top
    render_legend()

    # =============================================================================
    # DATA LOADING SECTION
    # =============================================================================

    # Load the bundled file automatically
    df = pd.DataFrame()
    default_file = "data/career_track_matrix.xlsx"
    if os.path.exists(default_file):
        df = load_matrix_table(file_path=default_file)
    else:
        st.error("❌ Growth framework data file not found")

    # =============================================================================
    # VALIDATION & DEBUG
    # =============================================================================

    if df.empty:
        st.info("👆 Please load a file to view the growth framework")
        return

    # Get unique values for filters (preserve canonical ordering)
    levels = sorted(df['level'].dropna().unique().tolist())
    unique_sections = df['section'].dropna().unique().tolist()
    sections = [s for s in CANONICAL_SECTIONS if s in unique_sections]
    scopes = sorted([s for s in df['scope'].dropna().unique().tolist() if s])

    # Matrix overview
    with st.expander("📊 Matrix Overview", expanded=False):
        print_validation_info(df)

    # =============================================================================
    # ENHANCED FILTERS
    # =============================================================================

    st.sidebar.header("🔍 Filters")

    # Level filter with query params
    levels_str = qp_get('levels', "")
    pre_levels = [s for s in levels_str.split(",") if s]
    selected_levels = st.sidebar.multiselect(
        "Select Levels:",
        levels,
        default=[lvl for lvl in pre_levels if lvl in levels] or levels,
        help="Choose which engineering levels to display (default: all levels)"
    )

    # Section/Dimension filter (default all)
    sections_str = qp_get('sections', "")
    pre_sections = [s for s in sections_str.split(",") if s]
    selected_sections = st.sidebar.multiselect(
        "Select Dimensions (Sections):",
        sections,
        default=[sec for sec in pre_sections if sec in sections] or sections,
        help="Choose which dimensions to display"
    )

    # Operating Scope filter (renamed from "Scope Types")
    OPERATING_SCOPE_OPTIONS = ["Pod", "Cross-Pod", "Platform", "Cross-Platform", "Org-Wide"]
    pre_scope = [s for s in qp_get("operating_scope", "").split(",") if s]
    operating_scope = st.sidebar.multiselect(
        "Operating Scope",
        options=OPERATING_SCOPE_OPTIONS,
        default=[s for s in pre_scope if s in OPERATING_SCOPE_OPTIONS],
        help="Filter by where the work primarily operates or scales.",
    )

    # Scope of Impact filter (renamed from "Minimum Audience")
    IMPACT_OPTIONS = [
        "👥 Peers",
        "🤝 Product, Design, QA",
        "🏗 Engineering Leadership",
        "🎯 Executive Leadership",
    ]
    pre_impact = [s for s in qp_get("scope_of_impact", "").split(",") if s]
    scope_of_impact = st.sidebar.multiselect(
        "Scope of Impact",
        options=IMPACT_OPTIONS,
        default=[s for s in pre_impact if s in IMPACT_OPTIONS],
        help="Filter by the audience level your work influences.",
    )

    # Show examples toggle
    show_examples = st.sidebar.checkbox(
        "📝 Show examples",
        value=True,
        help="Toggle expandable examples sections"
    )

    # Persist to URL
    qp_set({
        "levels": ",".join(selected_levels),
        "sections": ",".join(selected_sections),
        "operating_scope": ",".join(operating_scope),
        "scope_of_impact": ",".join(scope_of_impact)
    })

    # =============================================================================
    # APPLY FILTERS
    # =============================================================================

    filtered_df = df.copy()

    if selected_levels:
        filtered_df = filtered_df[filtered_df['level'].isin(selected_levels)]

    if selected_sections:
        filtered_df = filtered_df[filtered_df['section'].isin(selected_sections)]

    # Apply Operating Scope (if you have a 'scope' or 'pod_type' column; prefer 'scope' if present)
    if operating_scope:
        scope_col = "scope" if "scope" in filtered_df.columns else ("pod_type" if "pod_type" in filtered_df.columns else None)
        if scope_col:
            filtered_df = filtered_df[filtered_df[scope_col].isin(operating_scope)]

    # Apply Scope of Impact (icons) — keep row if its impact_icons contains ANY selected icon
    if scope_of_impact:
        def matches_icons(icon_str: str) -> bool:
            return any(icon.split()[0] in (icon_str or "") for icon in scope_of_impact)
        filtered_df = filtered_df[filtered_df.get("impact_icons", "").apply(matches_icons)]

    st.sidebar.write(f"**{len(filtered_df)} items match filters**")

    # CSV download
    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False)
        st.sidebar.download_button(
            "📥 Download filtered CSV",
            data=csv_data,
            file_name="growth_framework_levels_filtered.csv",
            mime="text/csv"
        )

    # =============================================================================
    # DISPLAY LEVELS AS TABS
    # =============================================================================

    if filtered_df.empty:
        st.warning("No data matches your current filters.")
        return

    if not selected_levels:
        st.warning("Please select at least one level to display.")
        return

    # Create tabs for each selected level
    level_tabs = st.tabs([f"🎯 {level} — {LEVEL_TITLES.get(level, level)}" for level in selected_levels])

    for i, level in enumerate(selected_levels):
        with level_tabs[i]:
            level_data = filtered_df[filtered_df['level'] == level]

            if level_data.empty:
                st.info(f"No data available for {level} with current filters.")
                continue

            # Display sections within this level
            for section in selected_sections:
                section_data = level_data[level_data['section'] == section]

                if section_data.empty:
                    continue

                # Section title as subheader
                st.subheader(f"📋 {section}")

                # Display each row for this section/level combination
                for _, row in section_data.iterrows():
                    # Render scope badge first
                    render_scope_badge(row['scope'], row['impact_icons'],
                                     row['impact_audience'], row['impact_summary'])

                    # Create content card
                    with st.container():
                        # Bold prefix
                        if row['prefix']:
                            st.markdown(f"**{row['prefix']}**")

                        # Double-spaced body text
                        if row['body']:
                            st.markdown(f"<div style='line-height: 1.8; margin-bottom: 1rem;'>{row['body']}</div>",
                                      unsafe_allow_html=True)

                        # Expandable examples if present and enabled
                        if show_examples and row['examples'] and row['examples'] != 'nan':
                            with st.expander("📝 Examples"):
                                st.write(row['examples'])

                        # Pod type info
                        if row['pod_type']:
                            st.caption(f"🏷️ Pod Type: {row['pod_type']}")

                    st.divider()

            # If no sections had data for this level
            if not any(level_data[level_data['section'] == sec].shape[0] > 0 for sec in selected_sections):
                st.info(f"No data available for {level} in the selected dimensions.")


if __name__ == "__main__":
    main()