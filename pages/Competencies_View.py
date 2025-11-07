"""
Engineering Growth Framework - Competencies View (Main Page)
Displays competencies as tabs with levels inside each section.
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
    ICON_LEGEND
)

def main():
    st.set_page_config(
        page_title="Competencies View",
        page_icon="📊",
        layout="wide"
    )

    # Inject custom CSS
    inject_custom_css()

    st.title("Competencies View")
    st.caption("View competencies as tabs with levels inside each section.")

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
        help="Choose which engineering levels to display"
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

    # Search filter
    search_term = st.sidebar.text_input(
        "🔎 Search:",
        value=qp_get('search', ''),
        help="Search in prefix, body, or examples"
    )

    # Show examples toggle
    show_examples = st.sidebar.checkbox(
        "📝 Show examples",
        value=True,
        help="Toggle expandable examples sections"
    )

    # Compare mode
    compare_mode = st.sidebar.checkbox(
        "📊 Compare Mode",
        value=False,
        help="Side-by-side comparison of two levels"
    )

    # Persist to URL
    qp_set({
        "levels": ",".join(selected_levels),
        "operating_scope": ",".join(operating_scope),
        "scope_of_impact": ",".join(scope_of_impact),
        "search": search_term
    })

    # =============================================================================
    # APPLY FILTERS
    # =============================================================================

    filtered_df = df.copy()

    if selected_levels:
        filtered_df = filtered_df[filtered_df['level'].isin(selected_levels)]

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
            file_name="growth_framework_filtered.csv",
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
                        if show_examples and row['examples'] and row['examples'] != 'nan':
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
                        if show_examples and row['examples'] and row['examples'] != 'nan':
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
                        if show_examples and row['examples'] and row['examples'] != 'nan':
                            with st.expander("📝 Examples"):
                                st.write(row['examples'])
                        if row['pod_type']:
                            st.caption(f"🏷️ Pod Type: {row['pod_type']}")

                        st.divider()

if __name__ == "__main__":
    main()