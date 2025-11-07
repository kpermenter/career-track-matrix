# Engineering Career Track Matrix

A Streamlit application for viewing and navigating engineering career track matrices with levels L1-L7, including impact scope visualization and filtering capabilities.

## Features

- 📊 **Impact Visualization** - Shows scope and audience for each level (Pod, Cross-Pod, Platform, etc.)
- 🔍 **Advanced Filtering** - Filter by level, scope, minimum audience, and search terms
- 📋 **Organized Display** - Tabbed interface by competency section
- 📊 **Compare Mode** - Side-by-side level comparison
- 📱 **Responsive Design** - Works on desktop and mobile
- 📥 **Data Export** - Download filtered results as CSV

## Impact Levels

- **L1-L3**: Pod scope (👥 Peers, 🤝 Product/Design/QA)
- **L4**: Cross-Pod scope (+🏗 Engineering Leadership)
- **L5**: Platform scope (+🏗 Engineering Leadership)
- **L6**: Cross-Platform scope (+🎯 Executive Leadership)
- **L7**: Org-Wide scope (+🎯 Executive Leadership)

## Usage

1. Upload your career track matrix file (CSV or Excel)
2. Use filters to focus on specific levels or scope
3. Compare different levels side-by-side
4. Export filtered data for further analysis

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **File Support**: CSV, Excel (.xlsx, .xls)
- **Hosting**: Railway

## Local Development

```bash
pip install -r requirements.txt
streamlit run impact_enhanced_streamlit.py
```

## Deployment

This app is deployed on Railway and automatically updates when changes are pushed to the main branch.