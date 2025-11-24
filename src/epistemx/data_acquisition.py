import ee
from datetime import datetime
import logging
from .ee_config import ensure_ee_initialized

# Do not initialize Earth Engine at import time. Initialize when an instance is created.

#Configure root for global functions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Module 1: Near Cloud Free Acquisition
## System Response 1.2: Search and Filter Imagery
class Reflectance_Data:
    """Class for fetching and pre-processing Landsat image collection from Google Earth Engine API."""
    #Define the optical datasets. The band reflectances used is from Collection 2 Surface Reflectancce Data
    OPTICAL_DATASETS = {
        'L1_RAW': {
            'collection': 'LANDSAT/LM01/C02/T1',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_raw',
            'sensor': 'L1',
            'description': 'Landsat 1 Multispectral Scanner Raw Collection'
        },
        'L2_RAW': {
            'collection': 'LANDSAT/LM02/C02/T1',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_raw',
            'sensor': 'L2',
            'description': 'Landsat 2 Multispectral Scanner Raw Collection'            
        },
        'L3_RAW':{
            'collection': 'LANDSAT/LM03/C02/T1',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_raw',
            'sensor': 'L3',
            'description': 'Landsat 3 Multispectral Scanner Raw Collection'
        },
        'L4_SR': {
            'collection': 'LANDSAT/LT04/C02/T1_L2',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_sr',
            'sensor': 'L4',
            'description': 'Landsat 4 Thematic Mapper Surface Reflectance Collection',           
        },
        'L5_SR': {
            'collection': 'LANDSAT/LT05/C02/T1_L2',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_sr',
            'sensor': 'L5',
            'description': 'Landsat 5 Thematic Mapper Surface Reflectance Collection',
        },
        'L7_SR': {
            'collection': 'LANDSAT/LE07/C02/T1_L2', 
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_sr',
            'sensor': 'L7',
            'description': 'Landsat 7 Enhance Thematic Mapper + Surface Reflectance'
        },
        'L8_SR': {
            'collection': 'LANDSAT/LC08/C02/T1_L2',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_sr',
            'sensor': 'L8',
            'description': 'Landsat 8 Operational Land Imager Surface Reflectance'
        },
        'L9_SR': {
            'collection': 'LANDSAT/LC09/C02/T1_L2',
            'cloud_property': 'CLOUD_COVER_LAND', 
            'type': 'landsat_sr',
            'sensor': 'L9',
            'description': 'Landsat 9 Operational Land Imager-2 Surface Reflectance'
        }
    }
    #Define the thermal datasets. The thermal bands used is from Collection 2 Top-of-atmosphere data 
    #The TOA data provide consistent result and contain minimum missing pixel data
    #Note: Landsat 1-3 MSS sensors did not have thermal bands, so they are not included
    THERMAL_DATASETS = {
        'L4_TOA': {
            'collection': 'LANDSAT/LT04/C02/T1_TOA',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_toa',
            'sensor': 'L4',
            'description': 'Landsat 4 Top-of-atmosphere reflectance',            
        },
        'L5_TOA': {
            'collection': 'LANDSAT/LT05/C02/T1_TOA',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_toa',
            'sensor': 'L5',
            'description': 'Landsat 5 Top-of-atmosphere reflectance',
        },
        'L7_TOA': {
            'collection': 'LANDSAT/LE07/C02/T1_TOA',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_toa',
            'sensor': 'L7',
            'description': 'Landsat 7 Top-of-atmosphere reflectance',
        },
        'L8_TOA': {
            'collection': 'LANDSAT/LC08/C02/T1_TOA',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_toa',
            'sensor': 'L8',
            'description': 'Landsat 8 Top-of-atmosphere reflectance'  
        },
        'L9_TOA': {
            'collection': 'LANDSAT/LC09/C02/T1_TOA',
            'cloud_property': 'CLOUD_COVER_LAND',
            'type': 'landsat_toa',
            'sensor': 'L9',
            'description': 'Landsat 9 Top-of-atmosphere reflectance'      
        }
    }
    #Initialize the class
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the ReflectanceData object and set up a class-specific logger.
        Ensure Earth Engine is initialized lazily (avoids import-time failures).
        """
        # Ensure Earth Engine is initialized when first used (raises helpful error if not)
        ensure_ee_initialized()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        self.logger.info("ReflectanceData initialized.")
    
    def has_thermal_capability(self, optical_data):
        """
        Check if a given optical dataset has corresponding thermal bands.
        
        Parameters
        ----------
        optical_data : str
            Optical dataset code (e.g., 'L8_SR', 'L1_RAW')
            
        Returns
        -------
        bool
            True if thermal bands are available, False otherwise
        """
        # Landsat 1-3 MSS sensors did not have thermal bands
        if optical_data in ['L1_RAW', 'L2_RAW', 'L3_RAW']:
            return False
        
        # Check if corresponding thermal dataset exists
        thermal_data = optical_data.replace('_SR', '_TOA')
        return thermal_data in self.THERMAL_DATASETS
    #Function to mask clouds, shadow, and cirrus. Using QA Bands
    def mask_landsat_sr(self, image,cloud_conf_thresh=2, shadow_conf_thresh=2, cirrus_conf_thresh=2):
            """
            Mask clouds, shadows and cirrus for Landsat Collection 2 SR using QA_PIXEL band.
                
            Parameters:
            -----------
            image : ee.Image: Landsat SR image
            cloud_conf_thresh : int. Cloud confidence threshold (0=None, 1=Low, 2=Med, 3=High)
            shadow_conf_thresh : int. Shadow confidence threshold (0=None, 1=Low, 2=Med, 3=High)
            cirrus_conf_thresh : int. Cirrus confidence threshold (0=None, 1=Low, 2=Med, 3=High)

            Returns:
            --------
            ee.Image : Masked image (ee.)

            References
            --------
            https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands 

            Example
            --------
            >>> get_landsat = Reflectance_Data()
            #Implementation on image collection
            >>> collection = (collection.map(lambda img: get_landsat.mask_landsat_sr(img))
            #Implementatio on Image
            >>> masked_image = get_landsat.mask_landsat_sr(image)
            """
            qa = image.select('QA_PIXEL')
            #Deterministic bits
            #fyi, (bit 3 is set to 1) and so on
            cloud_bit = 1 << 3
            shadow_bit = 1 << 4
            cirrus_bit = 1 << 2
            
            cloud_mask = qa.bitwiseAnd(cloud_bit).eq(0)
            shadow_mask = qa.bitwiseAnd(shadow_bit).eq(0)
            cirrus_mask = qa.bitwiseAnd(cirrus_bit).eq(0)
            #Confidence bits ---
            cloud_conf = qa.rightShift(8).bitwiseAnd(3)     # Bits 8–9
            shadow_conf = qa.rightShift(10).bitwiseAnd(3)   # Bits 10–11
            cirrus_conf = qa.rightShift(14).bitwiseAnd(3)   # Bits 14–15
            #Keep pixels below thresholds
            conf_mask = (cloud_conf.lt(cloud_conf_thresh)
                        .And(shadow_conf.lt(shadow_conf_thresh))
                        .And(cirrus_conf.lt(cirrus_conf_thresh)))
            #Final mask
            final_mask = cloud_mask.And(shadow_mask).And(cirrus_mask).And(conf_mask)
            return image.updateMask(final_mask).copyProperties(image, image.propertyNames())
    #Functions to rename Landsat bands 
    def rename_landsat_bands(self, image, sensor_type):
        """
        Standardize Landsat Surface Reflectance (SR) band names based on sensor type. From 'SR_B*' or 'B*' to 'NIR', 'GREEN', etc.

        Parameters
        ----------
        image : ee.Image. Landsat SR image
        sensor_type : str. Sensor type ('L5', 'L7', 'L8', 'L9')

        Returns
        -------
        ee.Image : Image with standardized band names

        Example
        --------

        """
        if sensor_type in ['L4','L5', 'L7']:
            # Landsat 5/7 SR bands
            return image.select(
                ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7'], 
                ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2']
            )
        elif sensor_type in ['L1', 'L2', 'L3']:
            return image.select(
                ['B4', 'B5', 'B6', 'B7'],
                ['GREEN', 'RED', 'NIR1', 'NIR2']
            )
        elif sensor_type in ['L8', 'L9']:
            # Landsat 8/9 SR bands
            return image.select(
                ['SR_B1','SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'], 
                ['AEROSOL','BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2']
            )
        else:
            raise ValueError(f"Unsupported sensor type for SR data: {sensor_type}")
    #function to implement Landsat Collection 2 Tier 1 SR scale factor
    def apply_scale_factors(self, image):
        """
        Apply Landsat collection 2 scalling factors using the following formula: Digital Number (DN) * scale_factor + offset.
        Allowing the user to get the data back to its original floating point value, a scale factor and offset.

        Parameters
        ----------
        image : ee.Image (Landsat SR image) with DN value
        sensor_type : str. Sensor type ('L4', 'L5', 'L7', 'L8', 'L9')

        Returns
        -------
        ee.Image : Image with floating point, corresponding to surface reflectance value
        """        
        optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
        #thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
        return image.addBands(optical_bands, None, True)
    #Function to retrive Landsat multispectral bands
    def get_optical_data(self, aoi, start_date, end_date, optical_data='L8_SR',
                        cloud_cover=30,
                        verbose=True, compute_detailed_stats=True):
        """
        Get optical image collection for Landsat 1-9 SR data with detailed information logging.

        Parameters
        ----------
        aoi :  ee.FeatureCollection. Area of interest.
        start_date : str. Start date in format 'YYYY-MM-DD' or year.
        end_date : str. End date in format 'YYYY-MM-DD' or year.
        optical_data : str. Dataset type: i.e 'L5_SR', 'L7_SR', 'L8_SR', 'L9_SR'.
        cloud_cover : int. Maximum cloud cover percentage on land (default: 30).
        verbose : bool. Print detailed information about the collection (default: True).
        compute_detailed_stats : bool
            If True, compute detailed statistics 
            If False, return only basic information (default: True).

        Returns
        -------
        tuple : (ee.ImageCollection, dict)
            Filtered and preprocessed image collection with statistics.
        """
        #Helper function so that the user only input year or specific date range
        def parse_year_or_date(date_input, is_start=True):
            if isinstance(date_input, int):  # User gave integer year like 2024
                return f"{date_input}-01-01" if is_start else f"{date_input}-12-31"
            elif isinstance(date_input, str):
                if len(date_input) == 4 and date_input.isdigit():
                    return f"{date_input}-01-01" if is_start else f"{date_input}-12-31"
                else:
                    return date_input  # Already full date
            else:
                raise ValueError("Date must be either YYYY or YYYY-MM-DD format")
        # Parse inputs (handles both year and full date)
        start_date = parse_year_or_date(start_date, is_start=True)
        end_date   = parse_year_or_date(end_date, is_start=False)

        if optical_data not in self.OPTICAL_DATASETS:
            raise ValueError(f"optical_data must be one of: {list(self.OPTICAL_DATASETS.keys())}")

        config = self.OPTICAL_DATASETS[optical_data]

        #Use verbose to import detailed logging information
        if verbose:
            self.logger.info(f"Starting data fetch for {config['description']}")
            self.logger.info(f"Date range: {start_date} to {end_date}")
            self.logger.info(f"Cloud cover threshold: {cloud_cover}%")
            if not compute_detailed_stats:
                self.logger.info("detailed statistics will not be computed")

        #Initial collection
        initial_collection = (ee.ImageCollection(config['collection'])
                            .filterBounds(aoi)
                            .filterDate(start_date, end_date))
        #Compute cloud within the area of interest (produce additional processing time)
        '''
        def add_aoi_cloud(img):
            qa = img.select('QA_PIXEL')
            cloud_mask = qa.bitwiseAnd(1 << 3).Or(qa.bitwiseAnd(1<<4))
            total = ee.Number(cloud_mask.reduceRegion(
                reducer=ee.Reducer.count(), geometry=aoi, scale=30, maxPixels=1e9
            ).values().get(0))
            cloudy = ee.Number(cloud_mask.reduceRegion(
                reducer=ee.Reducer.sum(), geometry=aoi, scale=30, maxPixels=1e9
            ).values().get(0))
            cloud_perc = cloudy.divide(total).multiply(100)
            return img.set({'CLOUDY_PERC_AOI': cloud_perc})
        
        #Apply the AOI cloud percentage to the image collection
        initial_collection = initial_collection.map(add_aoi_cloud)
        '''
        #initial_stats = self.get_collection_statistics(initial_collection, compute_detailed_stats)
        stats_object = Reflectance_Stats()
        initial_stats = stats_object.get_collection_statistics(initial_collection, compute_detailed_stats)
        if verbose and compute_detailed_stats and initial_stats.get('total_images', 0) > 0:
            self.logger.info(f"Initial collection (before cloud filtering): {initial_stats['total_images']} images")
            self.logger.info(f"Date range of available images: {initial_stats['date_range']}")

        #Collection after cloud cover filter
        collection = initial_collection.filter(ee.Filter.lt(config['cloud_property'], cloud_cover))
        filtered_stats = stats_object.get_collection_statistics(collection, compute_detailed_stats)
        #Computing image statistics
        if verbose and compute_detailed_stats:
            if filtered_stats.get('total_images', 0) > 0:
                self.logger.info(f"After cloud filtering (<{cloud_cover}%): {filtered_stats['total_images']} images")
                self.logger.info(f"Cloud cover of selected images: "
                                f"{filtered_stats['cloud_cover']['min']:.1f}% - "
                                f"{filtered_stats['cloud_cover']['max']:.1f}%")
                self.logger.info(f"Average cloud cover: {filtered_stats['cloud_cover']['mean']:.1f}%")
                if len(filtered_stats['individual_dates']) <= 20:
                    self.logger.info(f"Image dates: {', '.join(filtered_stats['individual_dates'])}")
                else:
                    self.logger.info(f"Images span from {min(filtered_stats['individual_dates'])} "
                                    f"to {max(filtered_stats['individual_dates'])}")

                if filtered_stats['path_row_tiles']:
                    path_row_str = ', '.join([f"{p}/{r}" for p, r in filtered_stats['path_row_tiles'][:10]])
                    if len(filtered_stats['path_row_tiles']) > 10:
                        path_row_str += f" ... (+{len(filtered_stats['path_row_tiles']) - 10} more)"
                    self.logger.info(f"Path/Row tiles: {path_row_str}")
            else:
                self.logger.warning(f"No images found matching criteria (cloud cover < {cloud_cover}%)")
                if initial_stats.get('total_images', 0) > 0:
                    self.logger.info(f"Consider increasing cloud cover threshold, or expand the year of acqusition "
                                    f"Available range: {initial_stats['cloud_cover']['min']:.1f}% - "
                                    f"{initial_stats['cloud_cover']['max']:.1f}%")
        elif verbose:
            self.logger.info("Filtered collection created (use compute_detailed_stats=True for more information)")

        #Apply masking and band renaming to image collection after filtering
        collection = (collection
                    .map(lambda img: self.mask_landsat_sr(img))
                    .map(lambda img: self.apply_scale_factors(img))
                    .map(lambda img: self.rename_landsat_bands(img, config['sensor'])))

        #Return results
        return collection, {
            'dataset': config['description'],
            'sensor': config['sensor'],
            'date_range_requested': f"{start_date} to {end_date}",
            'cloud_cover_threshold': cloud_cover,
            'initial_collection': initial_stats,
            'filtered_collection': filtered_stats,
            'detailed_stats_computed': compute_detailed_stats
        }
    #TOA-based Thermal Bands
    def get_thermal_bands(self, aoi, start_date, end_date, thermal_data = 'L8_TOA', cloud_cover=30,
                        verbose=True, compute_detailed_stats=True):
        """
        Get the thermal bands from landsat TOA data
    
        Parameters
        ----------
        aoi :  ee.FeatureCollection. Area of interest.
        start_date : str. Start date in format 'YYYY-MM-DD' or year.
        end_date : str. End date in format 'YYYY-MM-DD' or year.
        optical_data : str. Dataset type: 'L5_SR', 'L7_SR', 'L8_SR', 'L9_SR'.
        cloud_cover : int. Maximum cloud cover percentage on land (default: 30).
        verbose : bool. Print detailed information about the collection (default: True).
        compute_detailed_stats : bool
            If True, compute detailed statistics 
            If False, return only basic information (default: True).
            
        Returns
        -------
        tuple : (ee.ImageCollection, dict)
            Filtered and preprocessed image collection with statistics.
        """
        #Helper function to parse the date so that the user can only input the year
        def parse_year_or_date(date_input, is_start=True):
            if isinstance(date_input, int):  # User gave integer year like 2024
                return f"{date_input}-01-01" if is_start else f"{date_input}-12-31"
            elif isinstance(date_input, str):
                if len(date_input) == 4 and date_input.isdigit():
                    return f"{date_input}-01-01" if is_start else f"{date_input}-12-31"
                else:
                    return date_input  # Already full date
            else:
                raise ValueError("Date must be either YYYY or YYYY-MM-DD format")
        # Parse inputs (handles both year and full date)
        start_date = parse_year_or_date(start_date, is_start=True)
        end_date   = parse_year_or_date(end_date, is_start=False)
        #Helper function to rename the bands
        def rename_thermal_band(img):
            sensor = config['sensor']
            thermal_band_map = {
                'L4': ['B6'],
                'L5': ['B6'],
                'L7': ['B6_VCID_2'],
                'L8': ['B10'],
                'L9': ['B10']
            }
            band_names = thermal_band_map.get(sensor, [])
            if len(band_names) == 1:
                return img.select(band_names).rename(['THERMAL'])
            else:
                return img
        #The core function for thermal bnd
        if thermal_data not in self.THERMAL_DATASETS:
                raise ValueError(f"thermal_data must be one of: {list(self.THERMAL_DATASETS.keys())}")

        config = self.THERMAL_DATASETS[thermal_data]

        #Decide which thermal band to select
        sensor = config['sensor']
        if sensor in ['L4', 'L5']:
            thermal_band = 'B6'
        elif sensor == 'L7':
            thermal_band = 'B6_VCID_2'
        elif sensor in ['L8', 'L9']:
            thermal_band = 'B10'
        else:
            raise ValueError(f"Unsupported sensor type: {sensor}")
        stats = Reflectance_Stats()
        #Logging
        if verbose:
            self.logger.info(f"Starting thermal data fetch for {config['description']}")
            self.logger.info(f"Date range: {start_date} to {end_date}")
            self.logger.info(f"Cloud cover threshold: {cloud_cover}%")
            if not compute_detailed_stats:
                self.logger.info("Fast mode enabled - detailed statistics will not be computed")
        #Initial collection
        initial_collection = (ee.ImageCollection(config['collection'])
                            .filterBounds(aoi)
                            .filterDate(start_date, end_date))
        initial_stats = stats.get_collection_statistics(initial_collection, compute_detailed_stats)

        if verbose and compute_detailed_stats and initial_stats.get('total_images', 0) > 0:
            self.logger.info(f"Initial collection (before cloud filtering): {initial_stats['total_images']} images")
            self.logger.info(f"Date range of available images: {initial_stats['date_range']}")
        #Apply cloud cover filter
        collection = initial_collection.filter(ee.Filter.lt(config['cloud_property'], cloud_cover))
        filtered_stats = stats.get_collection_statistics(collection, compute_detailed_stats)
        if verbose and compute_detailed_stats:
            if filtered_stats.get('total_images', 0) > 0:
                self.logger.info(f"After cloud filtering (<{cloud_cover}%): {filtered_stats['total_images']} images")
                self.logger.info(f"Cloud cover range: {filtered_stats['cloud_cover']['min']:.1f}% - {filtered_stats['cloud_cover']['max']:.1f}%")
                self.logger.info(f"Average cloud cover: {filtered_stats['cloud_cover']['mean']:.1f}%")
            else:
                self.logger.warning(f"No images found matching criteria (cloud cover < {cloud_cover}%)")
        elif verbose:
            self.logger.info("Filtered collection created (use compute_detailed_stats=True for detailed info)")
        
        #Apply masking (QA-based)
        collection = collection.map(lambda img: self.mask_landsat_sr(img))
        collection = collection.select(thermal_band)
        collection = collection.map(rename_thermal_band)

        #Return collection and stats
        return collection, {
            'dataset': config['description'],
            'sensor': sensor,
            'thermal_band': thermal_band,
            'date_range_requested': f"{start_date} to {end_date}",
            'cloud_cover_threshold': cloud_cover,
            'initial_collection': initial_stats,
            'filtered_collection': filtered_stats,
            'detailed_stats_computed': compute_detailed_stats
        }
class Reflectance_Stats:
    """
    Class for fetching image collection statistics
    """
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the ReflectanceStats object and set up a class-specific logger.
        Ensure Earth Engine is initialized lazily (avoids import-time failures).
        """
        # Ensure Earth Engine is initialized when first used (raises helpful error if not)
        ensure_ee_initialized()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

        self.logger.info("Reflectance Stats initialized.")
    def get_collection_statistics(self, collection, compute_stats=True, print_report=False):
        """
        Get comprehensive statistics about an image collection.
        """
        #Get the number of image used 
        try:
            size = collection.size()
            if compute_stats:
                total_images = size.getInfo() #Client side operation, produce number of image collection
                if total_images > 0:
                    #Get the cloud cover percentage, and image aqcusition date
                    cloud_values = collection.aggregate_array('CLOUD_COVER_LAND').getInfo()
                    dates = collection.aggregate_array('system:time_start').getInfo()
                    dates_readable = [datetime.fromtimestamp(d/1000).strftime('%Y-%m-%d') for d in dates]
                    date_range = f"{min(dates_readable)} to {max(dates_readable)}"
                    #add lines to identify collection ID
                    scene_id = collection.aggregate_array('system:index').getInfo()
                    date_range = f"{min(dates_readable)} to {max(dates_readable)}"
                    #Get information regarding image's WRS path and row
                    try:
                        first_img = collection.first()
                        has_path_row = first_img.propertyNames().contains('WRS_PATH').getInfo()
                        if has_path_row:
                            paths = collection.aggregate_array('WRS_PATH').getInfo()
                            rows = collection.aggregate_array('WRS_ROW').getInfo()
                            path_rows = list(set(zip(paths, rows)))
                            path_rows.sort()
                        else:
                            path_rows = []
                    except Exception:
                        path_rows = []
                    #Image collections information 
                    stats = {
                        'total_images': total_images,
                        'date_range': date_range,
                        'cloud_cover': {
                            'min': min(cloud_values) if cloud_values else None,
                            'max': max(cloud_values) if cloud_values else None,
                            'mean': sum(cloud_values) / len(cloud_values) if cloud_values else None,
                            'values': cloud_values
                        },
                        'path_row_tiles': path_rows,
                        'unique_tiles': len(path_rows),
                        'individual_dates': dates_readable,
                        'Scene_ids': scene_id
                    }
                    if print_report:
                        self.print_collection_report(stats)
                    #if total_images <= 20:
                    #    self.logger.info(f"Scene IDs:{', '.join(scene_id)}")
                    #else:
                    #    self.logger.info(f"Scene IDs (first 10): {', '.join(scene_id[:10])}")
                else:
                    stats = {
                        'total_images': 0,
                        'date_range': "No images found",
                        'cloud_cover': {'min': None, 'max': None, 'mean': None, 'values': []},
                        'path_row_tiles': [],
                        'unique_tiles': 0,
                        'individual_dates': [],
                        'Scene_ids':[]
                    }
                    if print_report:
                        print("="*60)
                        print("           LANDSAT COLLECTION REPORT")
                        print("="*60)
                        print("No images found matching the specified criteria.")
                        print("="*60)
            else:
                stats = {
                    'total_images': 'computed_on_demand',
                    'size_object': size,
                    'collection_object': collection,
                    'computed': False
                }
            return stats

        except Exception as e:
            self.logger.error(f"Error getting collection statistics: {str(e)}")
            return {'error': str(e)} 
    def print_collection_report(self, stats):
        """
        Print a formatted report of collection statistics.
        
        Parameters
        ----------
        stats : dict
            Statistics dictionary from get_collection_statistics
        """
        print("="*60)
        print("           Landsat Data Collection Retrival Report")
        print("="*60)
        #Basic Information
        print(f"Total Images Found: {stats['total_images']}")
        print(f"Date Range: {stats['date_range']}")
        print(f"Unique WRS Tiles: {stats['unique_tiles']}")
        print()
        #Cloud Cover Statistics
        print("Scene Cloud Cover Statistics:")
        print("-" * 30)
        if stats['cloud_cover']['mean'] is not None:
            print(f"Average Cloud Cover: {stats['cloud_cover']['mean']:.1f}%")
            print(f"Minimum Cloud Cover: {stats['cloud_cover']['min']:.1f}%")
            print(f"Maximum Cloud Cover: {stats['cloud_cover']['max']:.1f}%")
        else:
            print("No cloud cover data available")
        print()
        #WRS Path/Row Information
        if stats['path_row_tiles']:
            print("WRS Path/Row Tiles:")
            print("-" * 30)
            if len(stats['path_row_tiles']) <= 10:
                for path, row in stats['path_row_tiles']:
                    print(f"Path {path:03d}/Row {row:03d}")
            else:
                # Show first 8 tiles
                for path, row in stats['path_row_tiles'][:8]:
                    print(f"Path {path:03d}/Row {row:03d}")
                print(f"... and {len(stats['path_row_tiles']) - 8} more tiles")
            print()
        #Available Dates
        if stats['individual_dates']:
            print("Available Acqusition Date:")
            print("-" * 30)
            if len(stats['individual_dates']) <= 20:
                # Group dates by month for better readability
                dates_by_month = {}
                for date in sorted(stats['individual_dates']):
                    month_key = date[:7]  # YYYY-MM
                    if month_key not in dates_by_month:
                        dates_by_month[month_key] = []
                    dates_by_month[month_key].append(date[8:])  # Just the day
                
                for month, days in dates_by_month.items():
                    print(f"{month}: {', '.join(days)}")
            else:
                print(f"Date range: {min(stats['individual_dates'])} to {max(stats['individual_dates'])}")
                print(f"({len(stats['individual_dates'])} total acquisition dates)")
            print()
        # Sample Scene IDs
        if stats['Scene_ids']:
            print("Scene IDs (first 10):")
            print("-" * 30)
            if len(stats['Scene_ids']) <= 10:
                for scene_id in stats['Scene_ids']:
                    print(f"• {scene_id}")
            else:
                for scene_id in stats['Scene_ids'][:10]:
                    print(f"• {scene_id}")
                print(f"... and {len(stats['Scene_ids']) - 10} more scenes")
            print()
        
        print("="*60)

class final_Image:
    """
    Class for combining image collections to get the final images.
    Supports single-date mosaics and time series compositing.
    """
    
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the final_Image object and set up a class-specific logger.
        """
        ensure_ee_initialized()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        self.logger.info("final_Image initialized.")
    
    def get_single_date_image(self, collection, aoi, target_date=None, mosaic=True):
        """
        Get a single-date image from collection, either by mosaicking multiple scenes
        or selecting the closest date if target_date is specified.
        
        Parameters
        ----------
        collection : ee.ImageCollection
            Filtered image collection from Reflectance_Data
        aoi : ee.Geometry or ee.FeatureCollection
            Area of interest for clipping
        target_date : str, optional
            Target date in 'YYYY-MM-DD' format. If None, uses the first available date
        mosaic : bool
            If True, mosaic multiple scenes from the same date (default: True)
            
        Returns
        -------
        ee.Image
            Single image clipped to AOI
            
        Example
        -------
        >>> data_fetcher = Reflectance_Data()
        >>> collection, stats = data_fetcher.get_optical_data(aoi, 2020, 2020, 'L8_SR')
        >>> image_processor = final_Image()
        >>> single_image = image_processor.get_single_date_image(collection, aoi, '2020-06-15')
        """
        if isinstance(aoi, ee.FeatureCollection):
            geometry = aoi.geometry()
        else:
            geometry = aoi
            
        if target_date:
            # Filter to specific date
            filtered = collection.filterDate(target_date, 
                                            ee.Date(target_date).advance(1, 'day'))
            size = filtered.size().getInfo()
            
            if size == 0:
                self.logger.warning(f"No images found for date {target_date}")
                # Find closest date
                all_dates = collection.aggregate_array('system:time_start').getInfo()
                if not all_dates:
                    raise ValueError("Collection is empty")
                    
                target_ms = ee.Date(target_date).millis().getInfo()
                closest_date = min(all_dates, key=lambda x: abs(x - target_ms))
                closest_str = datetime.fromtimestamp(closest_date/1000).strftime('%Y-%m-%d')
                self.logger.info(f"Using closest available date: {closest_str}")
                
                filtered = collection.filterDate(closest_str, 
                                                ee.Date(closest_str).advance(1, 'day'))
            else:
                self.logger.info(f"Found {size} scene(s) for date {target_date}")
        else:
            # Use first available date
            first_date = ee.Date(collection.first().get('system:time_start'))
            next_day = first_date.advance(1, 'day')
            filtered = collection.filterDate(first_date, next_day)
            date_str = datetime.fromtimestamp(first_date.millis().getInfo()/1000).strftime('%Y-%m-%d')
            self.logger.info(f"Using first available date: {date_str}")
        
        # Create final image
        if mosaic:
            image = filtered.mosaic()
            self.logger.info("Created mosaic from multiple scenes")
        else:
            image = filtered.first()
            self.logger.info("Selected first scene")
        
        # Clip to AOI
        clipped = image.clip(geometry)
        
        # Preserve metadata from first image
        first_img = filtered.first()
        clipped = clipped.copyProperties(first_img, first_img.propertyNames())
        
        return clipped
    
    def get_temporal_composite(self, collection, aoi, reducer='median', 
                              clip_output=True, add_band_stats=False):
        """
        Create a temporal composite from image collection using specified reducer.
        
        Parameters
        ----------
        collection : ee.ImageCollection
            Filtered image collection from Reflectance_Data
        aoi : ee.Geometry or ee.FeatureCollection
            Area of interest for clipping
        reducer : str or ee.Reducer
            Reduction method: 'median', 'mean', 'min', 'max', 'percentile_XX'
            (default: 'median')
        clip_output : bool
            Whether to clip the output to AOI (default: True)
        add_band_stats : bool
            If True, add additional bands with stdDev and count (default: False)
            
        Returns
        -------
        ee.Image
            Composite image
            
        Example
        -------
        >>> data_fetcher = Reflectance_Data()
        >>> collection, stats = data_fetcher.get_optical_data(aoi, 2020, 2020, 'L8_SR')
        >>> image_processor = final_Image()
        >>> composite = image_processor.get_temporal_composite(collection, aoi, reducer='median')
        """
        if isinstance(aoi, ee.FeatureCollection):
            geometry = aoi.geometry()
        else:
            geometry = aoi
        
        # Get reducer
        if isinstance(reducer, str):
            reducer_lower = reducer.lower()
            if reducer_lower == 'median':
                ee_reducer = ee.Reducer.median()
            elif reducer_lower == 'mean':
                ee_reducer = ee.Reducer.mean()
            elif reducer_lower == 'min':
                ee_reducer = ee.Reducer.min()
            elif reducer_lower == 'max':
                ee_reducer = ee.Reducer.max()
            elif reducer_lower.startswith('percentile_'):
                percentile = int(reducer_lower.split('_')[1])
                ee_reducer = ee.Reducer.percentile([percentile])
            else:
                raise ValueError(f"Unsupported reducer: {reducer}")
        else:
            ee_reducer = reducer
        
        # Check collection size
        size = collection.size().getInfo()
        if size == 0:
            raise ValueError("Collection is empty, cannot create composite")
        
        self.logger.info(f"Creating {reducer} composite from {size} images")
        
        # Create composite
        if add_band_stats:
            # Combine multiple reducers
            composite = collection.reduce(ee.Reducer.median()
                                        .combine(ee.Reducer.stdDev(), '', True)
                                        .combine(ee.Reducer.count(), '', True))
        else:
            composite = collection.reduce(ee_reducer)
        
        # Clip if requested
        if clip_output:
            composite = composite.clip(geometry)
            self.logger.info("Composite clipped to AOI")
        
        # Add metadata
        first_img = collection.first()
        last_img = collection.sort('system:time_start', False).first()
        
        start_date = ee.Date(first_img.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        end_date = ee.Date(last_img.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        
        composite = composite.set({
            'composite_start_date': start_date,
            'composite_end_date': end_date,
            'composite_count': size,
            'composite_reducer': str(reducer)
        })
        
        self.logger.info(f"Composite created from {start_date} to {end_date}")
        
        return composite