<!------------------------------------------------------------------------------------
    This document serves as a tags for connecting Quarto Technical Documentation with python codes 
    in this project
-------------------------------------------------------------------------------------> 

xi
pyproject.toml				# Python project dependencies tracking
Dockerfile					# Docker for reproducibility
.dockerignore
.gitignore
LICENSE						
README.md
├── tests					# For testing routine (not yet developed)	
├── docs
	├── repo_structure.md	       # Repository navigation structure
├── src/epistemx				  # Contain functions of backend
	├── __init__.py                      
	├── helpers.py            # Helper functions shared by multiple modules
	├── input_utils.py        # Validate the uploaded input file
	├── data_acquisition.py   # Module 1: Acquisition of Near-Cloud-Free Satellite Imagery
	├── classification_scheme.py           # Module 2: LULC Classification scheme
	├── sample_data.py        # Module 3: Sample Data Generation
	├── sample_data_quality.py           # Module 4: Sample Data Quality Analysis
	├── predictor.py           # Module 5: Predictor Introduction 
	├── classification.py           # Module 6: LULC Map Generation
	├── accuracy.py           # Module 7: Thematic Accuracy Assessment
	├── post_classification.py           # Module 8: Post Classification Analysis	
├── data
	├── aoi_sample.zip         		# Test shapefiles/CSV for AOI/training (small files)
├── notebooks
	└── module_implementation.ipynb  # Exploratory analysis for developers