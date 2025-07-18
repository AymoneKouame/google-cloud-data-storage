"""
Improved GCP Data Storage Manager
Author: Aymone Jeanne Kouame
Date: 2025-07-18
"""

import pandas as pd
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Union, Any
from google.cloud import storage
from google.api_core import exceptions
from IPython.display import Image, display
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GCPDataStorage:
    """
    A comprehensive class for managing data storage between local environment 
    and Google Cloud Storage buckets.
    
    Works in any GCP environment including:
    - All of Us Researcher Workbench
    - Google Colab
    - Vertex AI Workbench
    - Local development with GCP credentials
    - Any GCP Compute instance
    """
    
    def __init__(self, bucket_name: Optional[str] = None, directory: str = '', 
                 project_id: Optional[str] = None):
        """
        Initialize the GCP Data Storage manager.
        
        Args:
            bucket_name: GCS bucket name. If None, attempts to auto-detect from environment
            directory: Default directory within bucket
            project_id: GCP project ID. If None, attempts to auto-detect
        """
        self.bucket_name = self._resolve_bucket_name(bucket_name)
        self.directory = directory.strip('/')
        self.project_id = self._resolve_project_id(project_id)
        
        # Initialize storage client
        try:
            self.client = storage.Client(project=self.project_id)
        except Exception as e:
            logger.warning(f"Could not initialize storage client: {e}")
            self.client = None
            
        logger.info(f"Initialized GCPDataStorage:")
        logger.info(f"  - Bucket: {self.bucket_name}")
        logger.info(f"  - Directory: {self.directory}")
        logger.info(f"  - Project: {self.project_id}")
    
    def _resolve_bucket_name(self, bucket_name: Optional[str]) -> str:
        """Auto-detect bucket name from environment if not provided."""
        if bucket_name:
            return bucket_name.replace('gs://', '')
        
        # Try common environment variables
        env_vars = [
            'WORKSPACE_BUCKET',
            'GCS_BUCKET',
            'GOOGLE_CLOUD_BUCKET',
            'BUCKET_NAME'
        ]
        
        for var in env_vars:
            bucket = os.getenv(var)
            if bucket:
                return bucket.replace('gs://', '')
        
        # Try to get from gcloud config
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'storage/bucket'],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        raise ValueError(
            "No bucket name provided and could not auto-detect from environment. "
            "Please provide bucket_name parameter or set WORKSPACE_BUCKET environment variable."
        )
    
    def _resolve_project_id(self, project_id: Optional[str]) -> Optional[str]:
        """Auto-detect project ID from environment if not provided."""
        if project_id:
            return project_id
        
        # Try environment variables
        env_vars = ['GOOGLE_CLOUD_PROJECT', 'GCP_PROJECT', 'PROJECT_ID']
        for var in env_vars:
            project = os.getenv(var)
            if project:
                return project
        
        # Try to get from gcloud config
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return None
    
    def _validate_bucket_access(self, bucket_name: str) -> bool:
        """Validate that the bucket exists and is accessible."""
        try:
            if self.client:
                bucket = self.client.bucket(bucket_name)
                bucket.exists()
                return True
            else:
                # Fallback to gcloud command
                result = subprocess.run(
                    ['gcloud', 'storage', 'ls', f'gs://{bucket_name}'],
                    capture_output=True, text=True
                )
                return result.returncode == 0
        except exceptions.Forbidden:
            logger.error(f"Access denied to bucket '{bucket_name}'. Check permissions.")
            return False
        except exceptions.NotFound:
            logger.error(f"Bucket '{bucket_name}' not found.")
            return False
        except Exception as e:
            logger.error(f"Error validating bucket access: {e}")
            return False
    
    def _construct_gcs_path(self, filename: str, bucket_name: Optional[str] = None, 
                           directory: Optional[str] = None) -> str:
        """Construct a full GCS path."""
        bucket = bucket_name or self.bucket_name
        dir_path = directory if directory is not None else self.directory
        
        if filename.startswith('gs://'):
            return filename
        
        # Clean up path components
        bucket = bucket.replace('gs://', '')
        dir_path = dir_path.strip('/')
        filename = filename.strip('/')
        
        if dir_path:
            return f'gs://{bucket}/{dir_path}/{filename}'
        else:
            return f'gs://{bucket}/{filename}'
    
    def save_data_to_bucket(self, data: Any, filename: str, 
                           bucket_name: Optional[str] = None,
                           directory: Optional[str] = None,
                           index: bool = True, dpi: Union[str, int] = 'figure',
                           **kwargs) -> bool:
        """
        Save data to GCS bucket with support for various data types.
        
        Args:
            data: Data to save (DataFrame, plot, etc.)
            filename: Target filename
            bucket_name: Override default bucket
            directory: Override default directory
            index: Whether to include index for DataFrames
            dpi: DPI for plot saves
            **kwargs: Additional arguments passed to save functions
            
        Returns:
            bool: True if successful, False otherwise
        """
        gcs_path = self._construct_gcs_path(filename, bucket_name, directory)
        
        if not self._validate_bucket_access(gcs_path.split('/')[2]):
            return False
        
        logger.info(f"Saving data to: {gcs_path}")
        
        try:
            file_ext = Path(filename).suffix.lower()
            
            # Handle DataFrames
            if isinstance(data, pd.DataFrame):
                return self._save_dataframe(data, gcs_path, file_ext, index, **kwargs)

            # Handle Excel workbooks (Multiple DataFrames)
            if isinstance(data, dict):
                return self._save_excel_workbook(data, gcs_path, index, **kwargs)
                
            # Handle matplotlib figures
            elif hasattr(data, 'savefig'):
                return self._save_plot(data, gcs_path, file_ext, dpi)
            
            # Handle other file types
            else:
                return self._save_file(data, gcs_path, filename)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def _save_dataframe(self, df: pd.DataFrame, gcs_path: str, file_ext: str, 
                       index: bool, **kwargs) -> bool:
        """Save DataFrame to GCS."""
        save_functions = {
            '.csv': lambda d, p: d.to_csv(p, index=index, **kwargs),
            '.tsv': lambda d, p: d.to_csv(p, sep='\t', index=index, **kwargs),
            '.xlsx': lambda d, p: d.to_excel(p, index=index, **kwargs),
            '.parquet': lambda d, p: d.to_parquet(p, index=index, **kwargs),
            '.json': lambda d, p: d.to_json(p, **kwargs)
        }
        
        if file_ext in save_functions:
            save_functions[file_ext](df, gcs_path)
            logger.info(f"DataFrame saved successfully")
            return True
        else:
            logger.error(f"Unsupported DataFrame format: {file_ext}")
            return False
    
    def _save_plot(self, plot, gcs_path: str, file_ext: str, dpi: Union[str, int]) -> bool:
        """Save plot to GCS."""
        plot_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.svg', '.eps', '.tiff'}
        
        if file_ext not in plot_extensions:
            logger.error(f"Unsupported plot format: {file_ext}")
            return False
        
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            plot.savefig(tmp_file.name, dpi=dpi, bbox_inches='tight')
            result = subprocess.run(
                ['gcloud', 'storage', 'cp', tmp_file.name, gcs_path],
                capture_output=True, text=True
            )
            os.unlink(tmp_file.name)
            
            if result.returncode == 0:
                logger.info("Plot saved successfully")
                return True
            else:
                logger.error(f"Error saving plot: {result.stderr}")
                return False
    
    def _save_file(self, data: Any, gcs_path: str, filename: str) -> bool:
        """Save generic file to GCS."""
        if isinstance(data, (str, bytes)):
            # Handle string or bytes data
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
                if isinstance(data, str):
                    tmp_file.write(data.encode('utf-8'))
                else:
                    tmp_file.write(data)
                tmp_file.flush()
                
                result = subprocess.run(
                    ['gcloud', 'storage', 'cp', tmp_file.name, gcs_path],
                    capture_output=True, text=True
                )
                os.unlink(tmp_file.name)
                
                if result.returncode == 0:
                    logger.info("File saved successfully")
                    return True
                else:
                    logger.error(f"Error saving file: {result.stderr}")
                    return False
        else:
            # Assume it's already a file on disk
            result = subprocess.run(
                ['gcloud', 'storage', 'cp', filename, gcs_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info("File copied successfully")
                return True
            else:
                logger.error(f"Error copying file: {result.stderr}")
                return False
    
    def _save_excel_workbook(self, sheets_dict: Dict[str, pd.DataFrame], filename:str, 
                           bucket_name: Optional[str] = None,
                           directory: Optional[str] = None,
                           index: bool = True, **kwargs) -> bool:
        """
        Save multiple DataFrames as Excel workbook with multiple sheets.
        
        Args:
            filename: Excel filename
            sheets_dict: Dictionary of {sheet_name: DataFrame}
            bucket_name: Override default bucket
            directory: Override default directory
            index: Whether to include index
            **kwargs: Additional arguments for to_excel
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        gcs_path = self._construct_gcs_path(filename, bucket_name, directory)
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                    for sheet_name, df in sheets_dict.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=index, **kwargs)
                
                result = subprocess.run(
                    ['gcloud', 'storage', 'cp', tmp_file.name, gcs_path],
                    capture_output=True, text=True
                )
                os.unlink(tmp_file.name)
                
                if result.returncode == 0:
                    logger.info(f"Excel workbook saved to: {gcs_path}")
                    return True
                else:
                    logger.error(f"Error saving Excel workbook: {result.stderr}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating Excel workbook: {e}")
            return False
    
    def read_data_from_bucket(self, filename: str, 
                             bucket_name: Optional[str] = None,
                             directory: Optional[str] = None,
                             save_copy_locally: bool = False,
                             local_only: bool = False,
                             **kwargs) -> Any:
        """
        Read data from GCS bucket.
        
        Args:
            filename: File to read
            bucket_name: Override default bucket
            directory: Override default directory
            save_copy_locally: Whether to save a local copy
            local_only: Only download, don't load into memory
            **kwargs: Additional arguments for read functions
            
        Returns:
            Loaded data or None if error
        """
        gcs_path = self._construct_gcs_path(filename, bucket_name, directory)
        
        if not self._validate_bucket_access(gcs_path.split('/')[2]):
            return None
        
        logger.info(f"Reading data from: {gcs_path}")
        
        try:
            file_ext = Path(filename).suffix.lower()
            
            # Handle different file types
            if file_ext in {'.csv', '.tsv', '.xlsx', '.parquet', '.json'}:
                return self._read_dataframe(gcs_path, file_ext, save_copy_locally, local_only, **kwargs)
            
            elif file_ext in {'.png', '.jpg', '.jpeg', '.pdf', '.svg'}:
                return self._read_image(gcs_path, filename, save_copy_locally)
            
            else:
                return self._read_generic_file(gcs_path, filename, save_copy_locally, local_only)
                
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return None
    
    def _read_dataframe(self, gcs_path: str, file_ext: str, save_copy_locally: bool, 
                       local_only: bool, **kwargs) -> Optional[pd.DataFrame]:
        """Read DataFrame from GCS."""
        if local_only:
            # Just download the file
            local_filename = Path(gcs_path).name
            result = subprocess.run(
                ['gcloud', 'storage', 'cp', gcs_path, local_filename],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"File downloaded to: {local_filename}")
            return None
        
        # Read functions
        read_functions = {
            '.csv': lambda p: pd.read_csv(p, **kwargs),
            '.tsv': lambda p: pd.read_csv(p, sep='\t', **kwargs),
            '.xlsx': lambda p: pd.read_excel(p, **kwargs),
            '.parquet': lambda p: pd.read_parquet(p, **kwargs),
            '.json': lambda p: pd.read_json(p, **kwargs)
        }
        
        if file_ext in read_functions:
            df = read_functions[file_ext](gcs_path)
            
            if save_copy_locally:
                local_filename = Path(gcs_path).name
                result = subprocess.run(
                    ['gcloud', 'storage', 'cp', gcs_path, local_filename],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    logger.info(f"Copy saved locally: {local_filename}")
            
            return df
        
        return None
    
    def _read_image(self, gcs_path: str, filename: str, save_copy_locally: bool):
        """Read image from GCS."""
        local_filename = Path(filename).name
        
        result = subprocess.run(
            ['gcloud', 'storage', 'cp', gcs_path, local_filename],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            if save_copy_locally:
                logger.info(f"Image saved locally: {local_filename}")
                return Image(local_filename)
            else:
                # Display image and clean up
                img = Image(local_filename)
                display(img)
                os.unlink(local_filename)
                return img
        
        return None
    
    def _read_generic_file(self, gcs_path: str, filename: str, save_copy_locally: bool, local_only: bool):
        """Read generic file from GCS."""
        local_filename = Path(filename).name
        
        result = subprocess.run(
            ['gcloud', 'storage', 'cp', gcs_path, local_filename],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            if save_copy_locally or local_only:
                logger.info(f"File downloaded to: {local_filename}")
                return local_filename
            else:
                # Read content and clean up
                with open(local_filename, 'rb') as f:
                    content = f.read()
                os.unlink(local_filename)
                return content
        
        return None
    
    def copy_between_buckets(self, source_path: str, destination_path: str) -> bool:
        """
        Copy data between GCS locations.
        
        Args:
            source_path: Source GCS path (can be relative or absolute)
            destination_path: Destination GCS path (can be relative or absolute)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not source_path.startswith('gs://'):
            source_path = self._construct_gcs_path(source_path)
        
        if not destination_path.startswith('gs://'):
            destination_path = self._construct_gcs_path(destination_path)
        
        logger.info(f"Copying from {source_path} to {destination_path}")
        
        try:
            result = subprocess.run(
                ['gcloud', 'storage', 'cp', source_path, destination_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info("Copy completed successfully")
                return True
            else:
                logger.error(f"Copy failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error during copy: {e}")
            return False
    
    def list_files(self, pattern: str = '*', bucket_name: Optional[str] = None,
                   directory: Optional[str] = None, recursive: bool = False) -> list:
        """
        List files in GCS bucket.
        
        Args:
            pattern: File pattern to match
            bucket_name: Override default bucket
            directory: Override default directory
            recursive: Whether to search recursively
            
        Returns:
            list: List of file paths
        """
        bucket = bucket_name or self.bucket_name
        dir_path = directory if directory is not None else self.directory
        
        if recursive and pattern == '*':
            search_path = f'gs://{bucket}/**'
        else:
            search_path = self._construct_gcs_path(pattern, bucket, dir_path)
        
        logger.info(f"Listing files in: {search_path}")
        
        try:
            result = subprocess.run(
                ['gcloud', 'storage', 'ls', search_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                logger.info(f"Found {len(files)} files")
                return files
            else:
                logger.error(f"List failed: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def delete_file(self, filename: str, bucket_name: Optional[str] = None,
                    directory: Optional[str] = None, confirm: bool = True) -> bool:
        """
        Delete file from GCS bucket.
        
        Args:
            filename: File to delete
            bucket_name: Override default bucket
            directory: Override default directory
            confirm: Whether to ask for confirmation
            
        Returns:
            bool: True if successful, False otherwise
        """
        gcs_path = self._construct_gcs_path(filename, bucket_name, directory)
        
        if confirm:
            response = input(f"Are you sure you want to delete '{gcs_path}'? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Deletion cancelled")
                return False
        
        logger.info(f"Deleting: {gcs_path}")
        
        try:
            result = subprocess.run(
                ['gcloud', 'storage', 'rm', gcs_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info("File deleted successfully")
                return True
            else:
                logger.error(f"Deletion failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, filename: str, partial_string: Optional[bool] = False
                      , bucket_name: Optional[str] = None, directory: Optional[str] = None) -> Optional[Dict]:
        """
        Get information about a file in GCS.
        
        Args:
            filename: File to get info for
            bucket_name: Override default bucket
            directory: Override default directory
            
        Returns:
            dict: File information or None if not found
        """
        
        if partial_string == True:
            gcs_path =  self._construct_gcs_path('*'+filename+'*', bucket_name, '**')
        else:
            gcs_path = self._construct_gcs_path(filename, bucket_name, directory)
        
        
        try:
            result = subprocess.run(
                ['gcloud', 'storage', 'ls', '-L', gcs_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Parse the output to extract file info
                lines = result.stdout.strip().split('\n')
                info = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
                return info
            else:
                logger.error(f"File info failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    def print_help(self):
        """Print comprehensive help documentation."""
        help_text = """
        GCP Data Storage Manager - Help Documentation
        ==========================================
        
        This class provides easy data management between your local environment and Google Cloud Storage.
        
        INITIALIZATION:
        --------------
        # Auto-detect bucket from environment
        storage = GCPDataStorage()
        
        # Specify bucket explicitly
        storage = GCPDataStorage(bucket_name='my-bucket', directory='data')
        
        SAVING DATA:
        -----------
        # Save DataFrame
        storage.save_data_to_bucket(df, 'my_data.csv')
        
        # Save plot
        storage.save_data_to_bucket(plt.gcf(), 'my_plot.png')
        
        # Save Excel workbook with multiple sheets
        sheets = {'sheet1': df1, 'sheet2': df2}
        storage.save_excel_workbook('workbook.xlsx', sheets)
        
        READING DATA:
        ------------
        # Read DataFrame
        df = storage.read_data_from_bucket('my_data.csv')
        
        # Read and save local copy
        df = storage.read_data_from_bucket('my_data.csv', save_copy_locally=True)
        
        # Just download file
        storage.read_data_from_bucket('my_data.csv', local_only=True)
        
        FILE MANAGEMENT:
        ---------------
        # List files
        files = storage.list_files('*.csv')
        
        # Copy between locations
        storage.copy_between_buckets('source.csv', 'destination.csv')
        
        # Delete file
        storage.delete_file('old_file.csv')
        
        # Get file info (full or partial filename)
        info = storage.get_file_info('my_file.csv')
        info = storage.get_file_info('file', partial_string = True)
        
        SUPPORTED FORMATS:
        -----------------
        DataFrames: .csv, .tsv, .xlsx, .parquet, .json
        Images: .png, .jpg, .jpeg, .pdf, .svg, .eps, .tiff
        Other: Any file type (generic binary handling)
        
        ENVIRONMENT COMPATIBILITY:
        -------------------------
        - All of Us Researcher Workbench
        - Google Colab
        - Vertex AI Workbench
        - Local development with GCP credentials
        - Any GCP Compute instance
        """
        print(help_text)