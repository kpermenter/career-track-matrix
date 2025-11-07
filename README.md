# Engineering Career Track Matrix - Multi-Page Streamlit App

A comprehensive Streamlit application for visualizing and navigating an engineering career track matrix across levels L1-L7 and competency dimensions.

## 🚀 Features

### Core Functionality
- **Multi-page navigation** with two distinct views
- **Robust data loading** from Excel/CSV files with intelligent parsing
- **Impact visualization** with scope badges and audience indicators
- **Advanced filtering** by levels, sections, scopes, and audience
- **Search functionality** across all text content
- **Compare mode** for side-by-side level comparison
- **URL parameter persistence** for shareable filtered views
- **CSV export** of filtered data

### Views

#### 1. Competencies View (Main Page)
- **Layout**: Competencies/sections as tabs, levels within each section
- **Default**: Shows all levels and all sections
- **Features**: Compare mode, search, full filtering suite

#### 2. Levels View (Page 2)
- **Layout**: Levels as tabs, sections within each level
- **Default**: Shows all levels and all sections
- **Features**: Same filtering and functionality as main page

## 📁 Project Structure

```
├── streamlit_app.py              # Main app (Competencies view)
├── pages/
│   └── 02_Levels_View.py        # Levels-as-tabs view
├── lib/
│   └── utils.py                 # Shared utilities and components
├── data/
│   └── career_track_matrix.xlsx # Bundled data file
├── test_app.py                  # Validation tests
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🎯 Impact Framework

The app automatically maps each level to its impact scope and audience:

| Level | Scope | Icons | Audience |
|-------|-------|-------|----------|
| L1 | Pod | 👥 | Peers |
| L2-L3 | Pod | 👥🤝 | Peers + Product/Design/QA |
| L4 | Cross-Pod | 👥🤝🏗 | + Engineering Leadership |
| L5 | Platform | 👥🤝🏗 | + Engineering Leadership |
| L6 | Cross-Platform | 👥🤝🏗🎯 | + Executive Leadership |
| L7 | Org-Wide | 👥🤝🏗🎯 | + Executive Leadership |

## 📋 Competency Dimensions

1. **Experience Overview**
2. **Technical Aptitude & Skills**
3. **AI Fluency**
4. **Scope & Impact**
5. **Ownership & Accountability**
6. **Planning & Project Management**
7. **Product Awareness, User Empathy, and Design Thinking**
8. **Collaboration, Communication, and Conflict Resolution**
9. **Community & Mentorship**
10. **Values in Action**

## 🛠 Installation & Setup

### Prerequisites
- Python 3.7+
- Virtual environment (recommended)

### Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd engineering-career-matrix
   python -m venv streamlit-env
   source streamlit-env/bin/activate  # On Windows: streamlit-env\\Scripts\\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas openpyxl
   ```

3. **Run the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access the app**:
   - Open http://localhost:8501 in your browser
   - Navigate between views using the sidebar menu

## 📊 Data Format

The app uses a bundled Excel file (`data/career_track_matrix.xlsx`) that contains the engineering career track matrix data. The file is automatically loaded when the app starts.

### Expected Data Structure
- **Level**: L1, L2, L3, L4, L5, L6, L7
- **Section**: Competency dimension name
- **Prefix**: Brief title/heading
- **Body**: Main description text
- **Examples**: Supporting examples (optional)
- **Pod Type**: Category information (optional)

## 🔧 Configuration

### URL Parameters
The app supports URL parameters for deep linking:
- `?levels=L3,L4` - Pre-select specific levels
- `?sections=Technical,Scope` - Pre-select sections
- `?scopes=Pod,Cross-Pod` - Pre-select scopes
- `?search=leadership` - Pre-populate search

Example: `http://localhost:8501/?levels=L3,L4&search=technical`

## 🎨 Styling & Accessibility

### Features
- **Dark mode support** - Respects system preferences
- **Screen reader friendly** - Proper ARIA labels and semantic HTML
- **Responsive design** - Works on desktop and mobile
- **High contrast** - Clear visual hierarchy
- **Interactive tooltips** - Hover information for impact badges

## 🧪 Testing

Run the validation tests:

```bash
python test_app.py
```

This validates:
- File structure integrity
- Data loading functionality
- Impact mapping correctness
- Filter operations
- Column presence and types

## 🚀 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Complete multi-page career matrix app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Visit https://share.streamlit.io
   - Connect your GitHub repository
   - Select `streamlit_app.py` as the main file
   - Deploy!

### Local Development

```bash
# Development mode with auto-reload
streamlit run streamlit_app.py --server.runOnSave true

# Custom port
streamlit run streamlit_app.py --server.port 8502
```

## 📚 Technical Details

### Key Components

#### `lib/utils.py`
- **`load_matrix_table()`**: Robust data loading with fuzzy matching
- **`render_scope_badge()`**: Impact visualization component
- **`render_legend()`**: Interactive legend component
- **Query parameter helpers**: URL state management
- **Filtering functions**: Advanced data filtering

#### Data Processing Pipeline
1. **File Detection**: Automatically detects Excel format
2. **Column Mapping**: Fuzzy matches column names to expected fields
3. **Level Extraction**: Regex-based level detection (L1-L7)
4. **Section Normalization**: Maps to canonical section names
5. **Impact Enhancement**: Adds scope and audience columns
6. **Validation**: Comprehensive data validation and reporting

### Performance Optimizations
- **`@st.cache_data`**: Caches data loading operations
- **Categorical ordering**: Efficient sorting of levels and sections
- **Memory management**: Proper DataFrame copying and cleanup

## 🎛 Default Settings

### Competencies View (Main Page)
- **Levels**: All levels (L1-L7) selected by default
- **Sections**: All competency dimensions selected by default
- **Layout**: Competencies as tabs → levels within each tab
- **Extras**: Compare mode, search, full filtering

### Levels View (Page 2)
- **Levels**: All levels (L1-L7) selected by default
- **Sections**: All competency dimensions selected by default
- **Layout**: Levels as tabs → competencies within each tab
- **Extras**: Same functionality as main page

## 🔄 Navigation

The app provides two complementary views of the same data:

1. **Switch to Levels View**: Use the sidebar navigation to access the Levels-focused layout
2. **Return to Competencies View**: Navigate back to the main page for the Competencies-focused layout
3. **URL Persistence**: Filters and selections are maintained via URL parameters when switching views

## 📋 User Interface Elements

### Sidebar Controls
- **Level Selection**: Multi-select dropdown for engineering levels
- **Section Selection**: Multi-select dropdown for competency dimensions
- **Scope Filtering**: Multi-select dropdown for impact scopes
- **Audience Filtering**: Checkboxes for minimum audience requirements
- **Search**: Text input for content search
- **Show Examples**: Toggle for expandable example sections
- **Compare Mode**: Toggle for side-by-side level comparison (Competencies view only)

### Main Content
- **Legend**: Expandable section explaining impact icons and scopes
- **Matrix Overview**: Expandable section with data statistics and validation
- **Tabbed Content**: Main navigation between sections or levels
- **Impact Badges**: Visual indicators showing scope and audience for each item
- **CSV Export**: Download button for filtered data

## 🤝 Contributing

### Adding New Features
1. Update `lib/utils.py` for shared functionality
2. Modify both view files if UI changes are needed
3. Add tests to `test_app.py`
4. Update documentation

### Data Format Extensions
- Extend `CANONICAL_SECTIONS` for new dimensions
- Add section aliases in `SECTION_ALIASES`
- Update `LEVEL_IMPACT_MAPPING` for new levels

## 📝 License

MIT License - feel free to adapt for your organization's needs.

## 🎯 Recent Updates

- ✅ Renamed main page to "Competencies View" for clarity
- ✅ Simplified data loading (removed upload options)
- ✅ Updated validation section names to be more descriptive
- ✅ Removed print view options for cleaner interface
- ✅ Set all levels as default selection (instead of just L3/L4)
- ✅ Improved accessibility with better labels and descriptions

---

**Built with ❤️ using Streamlit**

For questions or support, please check the validation tests first (`python test_app.py`) then review the browser console for any errors.