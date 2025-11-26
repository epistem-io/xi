<!------------------------------------------------------------------------------------
    This document serves as a tags for connecting MS Visio Module Workflow with python codes 
    in this project.
    Add user journey tags and based on hf_compatible branch on 26 nov 2025
-------------------------------------------------------------------------------------> 

# Module 1: Cloudless Image Mosaic
   ## User Journey 1.1: Pre-requisites check
      └── pages 
            └── 1_Module_1_Generate_Image_Mosaic.py
                  └── uploaded_file = st.file_uploader("Unggah shapefile dalam berkas .zip", type=["zip"]) (Line 139 - 194)
   ## System Response 1.1: Area of Interest Definition
      └── src/epistemx                      
            └── shapefile_utils.py
                  ├── class shapefile_validator
                  │      ├── def validate_and_fix_geometry
                  │      ├── def _fix_crs
                  │      ├── def _clean_geometries
                  │      ├── def _validate_points
                  │      ├── def _validate_polygons
                  │      ├── def _is_valid_coordinate
                  │      ├── def _count_vertices
                  │      └── def _final_validation
                  └── class EE_converter
                         ├── def __init__
                         ├── def log  
                         ├── def convert_aoi_gdf        
                         └── def convert_roi_gdf        



   ## User Journey 1.2: Search Criteria Definition
      └── pages 
            └── 1_Module_1_Generate_Image_Mosaic.py
                  └── Line 176 - 265
                        ├── date_mode = st.radio
                        ├── selected_sensor_name = st.selectbox()
                        └── cloud_cover = st.slider
   ## System Response 1.2: Search and Filter Imagery
      └── src/epistemx                    
            └── module_1.py
                  ├── class Reflectance_Data
                  │      ├── OPTICAL_DATASETS
                  │      ├── THERMAL_DATASETS      
                  │      ├── def __init_
                  │      ├── def mask_landsat_sr
                  │      ├── def rename_landsat_bands
                  │      ├── def apply_scale_factors 
                  │      ├── def get_optical_data
                  │      │      └── def parse_year_or_date  
                  │      └── def get_thermal_bands
                  │             ├── def parse_year_or_date
                  │             └── def rename_thermal_band      
                  ├── class Reflectance_Stats
                  │      ├── def __init_
                  │      ├── def get_collection_statistics
                  │      └── def print_collection_report       



   ## User Journey 1.3: Image Mosaic and Download
      └── pages 
            └── 1_Module_1_Generate_Image_Mosaic.py
                  └── Line 269 - 771
                        ├── if st.button("Generate Image Mosaic", type="primary")
                        └── if st.session_state.composite is not None and st.session_state.aoi is not None:   
   
   ## System Response 1.3: Imagery Download
      ├── pages/                     
            └── 1_Module_1_Generate_Image_Mosaic.py
                        └── line 389 - 443(if st.button("Start Export to Google Drive", type="primary"))



# Module 2: Classification Scheme Definition

   ## User Journey 2.1: Choosing classification scheme
      ├── pages/                     
            └── 2_Module_2_Classification_scheme.py
                  └── tab1, tab2, tab3 = st.tabs(["➕ Input Manual", "📤 Unggah CSV", "📋 Skema Bawaan"])            

   ## System Response 2.1a: Upload Classification Scheme
      ├── src/epistemx                    
            └── module_2.py
                  └── Class LULCSchemeClass
                         ├──  def process_csv_upload
                         ├──  def finalize_csv_upload
                         ├──  def _generate_random_color
                         ├──  def _generate_distinct_colors
                         └──  def auto_detect_csv_columns
   
   ## System Response 2.1b: Manual Scheme Definition
      ├── src/epistemx                     
      │     └── module_2.py
      │           └── Class LULC_Scheme_Manager:
      │                  ├──  def validate_class_input
      │                  ├──  def add_class
      │                  ├──  def _reset_edit_mode
      │                  ├──  def _sort_and_update_next_id
      │                  ├──  def edit_class
      │                  ├──  def delete_class
      │                  └──  def cancel_edit
      └── pages/                     
            └── 2_Module_2_Classification_scheme.py
                        └── def render_manual_input_form

   ## System Response 2.1c: Template Classification Scheme
      └── src/epistemx                      
            └── module_2.py
                  └── Class LULC_Scheme_Manager:
                         ├──  def load_default_scheme
                         └──  def get_default_scheme

   ## System Response 2.2: Download classification scheme
      ├── src/epistemx                      
      │      └── module_2.py
      │            └── Class LULC_Scheme_Manager:
      │                   └──  def get_csv_data  
      └── pages/    
             └── 2_Module_2_Classification_scheme.py
                         └── st.download_button (line 265 - 285)

# Module 3: Generate Region of Interest
  ## System Response 3.1 Prerequisite Check
      └── src/epistemx                      
            └── module_3.py
                  └── Class input_check
                         └──  def validateVariable   

  ## System Response 3.2 ROI Upload and content Verification
      └── src/epistemx                      
            └── module_3.py
                  └── Class input_check
                         ├──  def LoadTrainData
                         ├──  def SetClassField
                         ├──  def ValidClass
                         ├──  def CheckSufficiency
                         ├──  def FilterTrainAoi
                         ├──  def TrainDataRaw
                         ├──  def generate_report
                         ├──  def get_valid_training_data
  ## System Response 3.3 On-screen Sampling 
      └── src/epistemx                      
            └── module_3.py 
                  └── Class LULCSamplingTool          
                         ├──  def __init__
                         ├──  def  LoadAoiFromEe
                         ├──  def  CreateMap
                         ├──  def  CheckSufficiency
                         ├──  def  AddCrosshairCursor
                         ├──  def  AddAoiLayer
                         ├──  def  IsPointInAoi
                         ├──  def  _HandleMove
                         ├──  def  _HandleClick
                         ├──  def  RemovePoint
                         ├──  def  ToggleEditMode
                         ├──  def  CreateUi
                         ├──  def  OnClassSelect
                         ├──  def  SaveTrainingData
                         ├──  def  UpdateTrainDataSampling
                         ├──  def  ClearData
                         ├──  def  UpdateStatistics
                         ├──  def  UpdateTableDisplay
                         ├──  def  ExportToShapefile
                         └──  def  Display
                         
# Module 4: Region of Interest Separability Analysis

   ## System Response 4.1 Separability Analysis
      └── src/epistemx                      
            └── module_4.py
                  └── Class sample_quality
                         ├──  def get_display_property
                         ├──  def class_renaming
                         ├──  def add_class_names
                         ├──  def sample_stats
                         ├──  def get_sample_stats_df
                         ├──  def extract_spectral_values
                         ├──  def sample_pixel_stats
                         ├──  def get_sample_pixel_stats_df
                         ├──  def check_class_separability
                         │        ├──  def _jeffries_matusita_distance
                         │        └──  def transform_divergence                     
                         ├──  def get_separability_df
                         ├──  def lowest_separability
                         ├──  def separability_level
                         ├──  def sum_separability
                         └──  def print_analysis_summary

   ## System Response 4.2 Sample Visualization
      └── src/epistemx                    
            └── module_4_part2.py
                  └── Class spectral_plotter
                         ├──  def plot_histogram
                         ├──  def plot_boxplot
                         ├──  def interactive_scatter_plot
                         ├──  def static_scatter_plot  
                         │      └──  def add_elipse
                         └──  def scatter_plot_3d                       

# Module 5: Covariates Definition

# Module 6: Land Cover Classification
   ## System Response 6.1 Prerequisites Check
      ├── pages/                     
            └── 4_Module_6_Classification and LULC Creation.py
                    ├── with col1: (composite check: line 38 - 54)
                    └── with col2: (training data check: line 57 - 81)


   ## System Response 6.2 Classification
      └── src/epistemx                   
            └── module_6.py
                  ├── Class FeatureExtraction
                  │      ├──  def stratified_split
                  │      └──  def random_split                            
                  └── Class Generate_LULC:
                         ├── def hard_classification
                         └── def soft_classification

   ## System Response 6.3 Model Evaluation
      └── src/epistemx                      
           └── module_6.py
                 └── Class Generate_LULC:
                        ├── def get_feature_importance
                        └── def evaluate_model    

# Module 7: Thematic Accuracy Assessment
   ## System Response 7.1 Prerequisite check
      └── pages/                     
            └── 5_Module_7_Thematic_Accuracy.py
                    └── line 34-40 (classification check)

   ## System Response 7.2 Ground Reference Verification
      └── pages/                     
            └── 5_Module_7_Thematic_Accuracy.py
                    └── line 50-106 (shapefile verification)

   ## System Response 7.3 Thematic Accuracy Assessment
      └── src/epistemx                   
            └── module_7.py
                  ├── Class Accuracy_Assessment
                  ├── def _calculate_accuracy_confidence_interval
                  └── def thematic_assessment  

# Module 8: 