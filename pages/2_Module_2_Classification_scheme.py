"""
Module 2: Land Cover Classification Scheme Definition

This module provides a user interface for defining land cover classification schemes
through three methods: manual input, CSV upload, or default templates.

Architecture:
- Backend (src_modul_2.py): Pure business logic without UI dependencies
- Frontend (this file): Streamlit UI with session state management
- State synchronization ensures data persistence across page interactions
"""

import streamlit as st
import pandas as pd
from epistemx.module_2 import LULC_Scheme_Manager
from modules.nav import Navbar

#Page configuration
st.set_page_config(
    page_title="Land Cover Classification Scheme",
    page_icon="logos/logo_epistem_crop.png",
    layout="wide"
)

# Load custom CSS
def load_css():
    """Load custom CSS for EpistemX theme"""
    try:
        with open('.streamlit/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Apply custom theme
load_css()

# Initialize session state for persistence
def init_session_state():
    """Initialize session state variables for LULC scheme management."""
    session_vars = {
        'lulc_classes': [],
        'lulc_next_id': 1,
        'lulc_edit_mode': False,
        'lulc_edit_idx': None,
        'csv_temp_classes': []
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize session state
init_session_state()

# Create manager and sync with session state
manager = LULC_Scheme_Manager()

def sync_manager_from_session():
    """Sync manager state from Streamlit session state."""
    state = {
        'classes': st.session_state.lulc_classes,
        'next_id': st.session_state.lulc_next_id,
        'edit_mode': st.session_state.lulc_edit_mode,
        'edit_idx': st.session_state.lulc_edit_idx,
        'csv_temp_classes': st.session_state.csv_temp_classes
    }
    manager.set_state(state)

def sync_session_from_manager():
    """Sync Streamlit session state from manager state."""
    state = manager.get_state()
    st.session_state.lulc_classes = state['classes']
    st.session_state.lulc_next_id = state['next_id']
    st.session_state.lulc_edit_mode = state['edit_mode']
    st.session_state.lulc_edit_idx = state['edit_idx']
    st.session_state.csv_temp_classes = state['csv_temp_classes']

# Sync manager with current session state
sync_manager_from_session()

# Add navigation sidebar
Navbar()

# Page header
st.title("Determining LULC Classification Schema and Classes")
st.divider()

st.markdown("""
In this module, you need to define the classification scheme that you will be using to generate the land cover map.
Three methods are supported in this platform:
- **Manual Input**: Add classes one by one
- **CSV Upload**: Import from existing classification file  
- **Default Scheme**: Use predefined RESTORE+ project classes
""")

st.markdown("---")

#Tab layout for different classification definition
tab1, tab2, tab3 = st.tabs(["➕ Manual Input", "📤 Upload CSV", "📋 Default Scheme"])

#Createa function for manual input the class
def render_manual_input_form():
    """
    Render the manual class input form.
    
    Creates input fields for class ID, name, and color, with support for
    both adding new classes and editing existing ones.
    """
    st.markdown("#### Add a New Class")
    #3 columns
    col1, col2, col3 = st.columns([1, 3, 2])
    
    # Sync manager state
    sync_manager_from_session()
    
    # Get current values for edit mode
    if manager.edit_mode and manager.edit_idx is not None:
        current_class = manager.classes[manager.edit_idx]
        default_id = current_class['ID']
        default_name = current_class['Class Name']
        default_color = current_class['Color Code']
        key_suffix = "edit"
    else:
        default_id = manager.next_id
        default_name = ""
        default_color = "#2e8540"
        key_suffix = "new"
    
    with col1:
        class_id = st.number_input(
            "Class ID", 
            value=default_id, 
            min_value=1, 
            step=1,
            key=f"{key_suffix}_class_id"
        )
    
    with col2:
        class_name = st.text_input(
            "Class Name", 
            value=default_name,
            placeholder="e.g., Forest, Settlement",
            key=f"{key_suffix}_class_name"
        )
    
    with col3:
        color_code = st.color_picker(
            "Color Code", 
            value=default_color,
            key=f"{key_suffix}_color_code"
        )
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    with col_btn1:
        button_text = "💾 Update Class" if manager.edit_mode else "➕ Add Class"
        if st.button(button_text, type="primary", use_container_width=True):
            success, message = manager.add_class(class_id, class_name, color_code)
            if success:
                st.session_state['ReferenceDataSource'] = False
                sync_session_from_manager()  # Sync back to session state
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    with col_btn2:
        if manager.edit_mode and st.button("❌ Cancel", use_container_width=True):
            manager.cancel_edit()
            sync_session_from_manager()  # Sync back to session state
            st.rerun()

# Tab 1: Manual Input
with tab1:
    render_manual_input_form()

# Tab 2: Upload CSV
with tab2:
    st.markdown("#### Upload Classification Scheme")
    st.info("""
    **CSV Requirements:**
    - **ID column**: Numeric identifiers (e.g., 'ID', 'Class ID', 'Kode')
    - **Name column**: Class names (e.g., 'Class Name', 'Kelas', 'Name')
    - **Color column** (Optional): Hex color codes (e.g., 'Color', 'Color Code', 'Hex')
    
    If no color column is detected, distinct colors will be automatically assigned.
    """)
    #Code to upload csv
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        try:
            #make sure that python can read any form of delimiter
            df = pd.read_csv(uploaded_file, sep=None, engine="python")
            
            #Auto-detect columns
            auto_id, auto_name, auto_color = manager.auto_detect_csv_columns(df)
            
            st.markdown("### Select Columns")
            col1, col2, col3 = st.columns(3)
            #first column to select class ID's column
            with col1:
                id_col = st.selectbox(
                    "Select ID Column *", 
                    df.columns, 
                    index=df.columns.get_loc(auto_id) if auto_id in df.columns else 0
                )
            #second column to select class name's column
            with col2:
                name_col = st.selectbox(
                    "Select Class Name Column *", 
                    df.columns,
                    index=df.columns.get_loc(auto_name) if auto_name in df.columns else 0
                )
            #new column for detecting color palette column
            with col3:
                color_options = ["< No Color Column >"] + list(df.columns)
                default_color_idx = 0
                if auto_color and auto_color in df.columns:
                    default_color_idx = color_options.index(auto_color)
                
                color_col_selection = st.selectbox(
                    "Select Color Column (Optional)",
                    color_options,
                    index=default_color_idx
                )
            #After selection, load the CSV
            if st.button("📤 Load CSV Data", type="primary"):
                sync_manager_from_session()  # Sync current state
                color_col = None if color_col_selection == "< No Color Column >" else color_col_selection
                success, message = manager.process_csv_upload(df, id_col, name_col, color_col)
                if success:
                    st.session_state['ReferenceDataSource'] = False
                    # If colors were detected, finalize immediately
                    if color_col:
                        success_final, message_final = manager.finalize_csv_upload()
                        if success_final:
                            sync_session_from_manager()  # Sync back to session state
                            st.success(f"✅ {message_final}")
                        else:
                            st.error(f"❌ {message_final}")
                    else:
                        sync_session_from_manager()  # Sync back to session state
                        st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
                    
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")

    #Color assignment section (only show if no colors were auto-detected)
    sync_manager_from_session()  # Sync current state
    if manager.csv_temp_classes:
        st.markdown("---")
        st.markdown("### Adjust Color for each class")
        st.info("Color have been randomly generated. You can adjust them if needed.")
        
        color_assignments = []
        temp_classes = manager.csv_temp_classes
        
        for i, class_data in enumerate(temp_classes):
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                st.write(f"**ID: {class_data['ID']}**")
            with col2:
                st.write(f"**{class_data['Class Name']}**")
            with col3:
                color = st.color_picker(
                    f"Color", 
                    value=class_data.get('Color Code', '#2e8540'),
                    key=f"csv_color_{i}",
                    label_visibility="collapsed"
                )
                color_assignments.append(color)
        
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Finalize Scheme", type="primary", use_container_width=True):
                success, message = manager.finalize_csv_upload(color_assignments)
                if success:
                    sync_session_from_manager()  # Sync back to session state
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col2:
            if st.button("❌ Cancel Upload", use_container_width=True):
                manager.csv_temp_classes = []
                sync_session_from_manager()  # Sync back to session state
                st.rerun()

# Tab 3: Default Scheme
with tab3:
    st.markdown("#### Load Default Classification Scheme")
    st.info("Quick start with predefined RESTORE+ project land cover classes")
    
    if 'ReferenceDataSource' not in st.session_state:
        st.session_state.ReferenceDataSource = False

    default_schemes = manager.get_default_schemes()
    
    selected_scheme = st.selectbox(
        "Select a default scheme:",
        options=list(default_schemes.keys())
    )
    
    # Preview the selected scheme
    if selected_scheme:
        with st.expander("📋 Preview Classes"):
            preview_df = pd.DataFrame(default_schemes[selected_scheme])
            st.dataframe(preview_df, use_container_width=True)
    
    if st.button("📋 Load Default Scheme", type="primary", use_container_width=True):
        sync_manager_from_session()  # Sync current state
        success, message = manager.load_default_scheme(selected_scheme)
        if success:
            sync_session_from_manager()  # Sync back to session state
            st.success(f"✅ {message}")
            st.session_state['ReferenceDataSource'] = True
            st.rerun()
        else:
            st.error(f"❌ {message}")

#new function to render selected classification scheme from one of the three methods
def render_class_display():
    """
    Render the current classification scheme display.
    
    Shows all defined classes in a table format with color previews,
    edit/delete buttons, and download functionality.
    """
    st.markdown("---")
    st.markdown("#### Current Classification Scheme")

    # Sync manager state
    sync_manager_from_session()
    
    if not manager.classes:
        st.warning("⚠️ No classes defined yet. Add your first class above!")
        return

    # Display classes in a clean table format
    for idx, class_data in enumerate(manager.classes):
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 1])
        
        with col1:
            st.write(f"**{class_data['ID']}**")
        
        with col2:
            st.write(class_data['Class Name'])
        
        with col3:
            # Color preview with code
            st.markdown(
                f"""<div style='display: flex; align-items: center;'>
                    <div style='background-color: {class_data['Color Code']}; 
                                width: 40px; height: 25px; border: 1px solid #ccc; 
                                margin-right: 8px; border-radius: 3px;'></div>
                    <code>{class_data['Color Code']}</code>
                </div>""",
                unsafe_allow_html=True
            )
        
        with col4:
            if st.button("✏️", key=f"edit_{idx}", help="Edit class"):
                manager.edit_class(idx)
                sync_session_from_manager()  # Sync back to session state
                st.rerun()
        
        with col5:
            if st.button("🗑️", key=f"delete_{idx}", help="Delete class"):
                success, message = manager.delete_class(idx)
                if success:
                    sync_session_from_manager()  # Sync back to session state
                    st.success(f"✅ {message}")
                    st.rerun()

    # Download and preview section
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        csv_data = manager.get_csv_data()
        if csv_data:
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name="classification_scheme.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
    
    with col2:
        with st.expander("📋 Preview Data"):
            st.dataframe(manager.get_dataframe(), use_container_width=True)

# Render the class display
render_class_display()

def render_navigation():
    """
    Render module navigation and completion status.
    
    Provides navigation buttons to previous/next modules and displays
    completion status based on whether classes have been defined.
    """
    st.divider()
    
    # Sync manager state and store classification data for other modules
    sync_manager_from_session()
    if manager.classes:
        # Store both the formatted DataFrame and raw classes for other modules
        st.session_state['classification_df'] = manager.get_dataframe()
        st.session_state['lulc_classes_final'] = manager.classes.copy()
        
        # Also store in the format expected by Module 3
        # Convert manager classes to the format Module 3 expects
        classes_for_module3 = []
        for cls in manager.classes:
            classes_for_module3.append({
                'ID': cls.get('ID', cls.get('Class ID', '')),
                'LULC_Type': cls.get('Class Name', cls.get('Land Cover Class', '')),
                'color_palette': cls.get('Color Code', cls.get('Color Palette', cls.get('Color', '#2e8540')))
            })
        st.session_state['classes'] = classes_for_module3
    
    # Module completion check
    module_completed = manager.has_classes()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Module 1", use_container_width=True):
            st.switch_page("pages/1_Module_1_Generate_Image_Mosaic.py")
    
    with col2:
        if module_completed:
            if st.button("➡️ Go to Module 3: Training data generation", 
                        type="primary", use_container_width=True):
                st.switch_page("pages/3_Module_3_Generate_ROI.py")
        else:
            st.button("🔒 Complete Module 2 First", 
                     disabled=True, use_container_width=True,
                     help="Add at least one class to proceed")
    
    # Status indicator
    if module_completed:
        st.success(f"✅ Module completed with {manager.get_class_count()} classes")
    else:
        st.info("💡 Add at least one class to complete this module")

# Render navigation
render_navigation()