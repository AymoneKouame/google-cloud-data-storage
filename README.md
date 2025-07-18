# GCP Data Storage Manager Documentation

## Overview

The `GCPDataStorage` class is a comprehensive Python utility for managing data storage between local environments and Google Cloud Storage (GCS) buckets. It provides a unified interface for saving, reading, and managing various data types including DataFrames, plots, images, and generic files.

**Author:** Aymone Jeanne Kouame  
**Date:** 2025-07-18  
**Version:** 1.0

## Features

- **Universal GCP Compatibility**: Works across all GCP environments including All of Us Researcher Workbench, Google Colab, Vertex AI Workbench, and local development
- **Auto-detection**: Automatically detects bucket names and project IDs from environment variables
- **Multi-format Support**: Handles DataFrames, plots, images, Excel workbooks, and generic files
- **Robust Error Handling**: Comprehensive logging and error management
- **Flexible Path Management**: Supports both relative and absolute GCS paths
- **Batch Operations**: Copy, list, and delete operations for file management

## Complete Workflow Example

```python
# Initialize storage manager
storage = GCPDataStorage(bucket_name='my-analysis-bucket', directory='experiments')

# Save analysis results
results_df = pd.DataFrame({'metric': ['accuracy', 'precision'], 'value': [0.95, 0.87]})
storage.save_data_to_bucket(results_df, 'results.csv')

# Save visualization
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('Analysis Results')
storage.save_data_to_bucket(plt.gcf(), 'analysis_plot.png', dpi=300)

# Create multi-sheet Excel report
raw_data_df = pd.DataFrame({'race': ['Asian', 'White'], 'count': [1523, 5899]})
metadata_df = pd.DataFrame({'metric': ['size', 'has'], 'value': [500, 's5f5hh']})
sheets = {
    'Summary': results_df,
    'Raw Data': raw_data_df,
    'Metadata': metadata_df
}
storage.save_data_to_bucket(sheets, 'comprehensive_report.xlsx')

# List all files
files = storage.list_files('*')
print(f"Total files: {len(files)}")

# Read data back
loaded_df = storage.read_data_from_bucket('results.csv')
print(loaded_df.head())

```

## Installation and Dependencies

```python
# Required dependencies
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
```

## Quick Start

### Basic Initialization

```python
# Auto-detect bucket from environment variables
storage = GCPDataStorage()

# Specify bucket explicitly
storage = GCPDataStorage(bucket_name='my-bucket')

# With custom directory and project
storage = GCPDataStorage(
    bucket_name='my-bucket',
    directory='data/experiments',
    project_id='my-project'
)
```

### Environment Auto-Detection

The class automatically detects configuration from these environment variables:

**Bucket Detection:**
- `WORKSPACE_BUCKET`
- `GCS_BUCKET`
- `GOOGLE_CLOUD_BUCKET`
- `BUCKET_NAME`

**Project Detection:**
- `GOOGLE_CLOUD_PROJECT`
- `GCP_PROJECT`
- `PROJECT_ID`

## API Reference

### Constructor

```python
GCPDataStorage(bucket_name=None, directory='', project_id=None)
```

**Parameters:**
- `bucket_name` (str, optional): GCS bucket name. Auto-detected if None
- `directory` (str, optional): Default directory within bucket
- `project_id` (str, optional): GCP project ID. Auto-detected if None

### Core Methods

#### save_data_to_bucket()

Save various data types to GCS bucket.

```python
save_data_to_bucket(
    data,
    filename,
    bucket_name=None,
    directory=None,
    index=True,
    dpi='figure',
    **kwargs
) -> bool
```

**Parameters:**
- `data`: Data to save (DataFrame, plot, string, bytes, etc.)
- `filename` (str): Target filename
- `bucket_name` (str, optional): Override default bucket
- `directory` (str, optional): Override default directory
- `index` (bool): Include index for DataFrames (default: True)
- `dpi` (str/int): DPI for plot saves (default: 'figure')
- `**kwargs`: Additional arguments for save functions

**Returns:** `bool` - True if successful

**Examples:**
```python
# Save DataFrame
success = storage.save_data_to_bucket(df, 'data.csv')

# Save multiple DataFrames as Excel workbook with multiple sheets.
success = storage.save_data_to_bucket(data= {'sheet1': df1, "sheet2":df2}, filename = 'data_workbook.xlsx')

# Save plot with custom DPI
success = storage.save_data_to_bucket(plt.gcf(), 'plot.png', dpi=300)

# Save to specific directory
success = storage.save_data_to_bucket(df, 'results.xlsx', directory='experiments')

# Save with custom parameters
success = storage.save_data_to_bucket(df, 'data.csv', index=False, encoding='utf-8')
```

#### read_data_from_bucket()

Read data from GCS bucket.

```python
read_data_from_bucket(
    filename,
    bucket_name=None,
    directory=None,
    save_copy_locally=False,
    local_only=False,
    **kwargs
) -> Any
```

**Parameters:**
- `filename` (str): File to read
- `bucket_name` (str, optional): Override default bucket
- `directory` (str, optional): Override default directory
- `save_copy_locally` (bool): Save a local copy (default: False)
- `local_only` (bool): Only download, don't load into memory (default: False)
- `**kwargs`: Additional arguments for read functions

**Returns:** Loaded data or None if error

**Examples:**
```python
# Read DataFrame
df = storage.read_data_from_bucket('data.csv')

# Read and save local copy
df = storage.read_data_from_bucket('data.csv', save_copy_locally=True)

# Just download file
storage.read_data_from_bucket('data.csv', local_only=True)

# Read with custom parameters
df = storage.read_data_from_bucket('data.csv', sep=';', encoding='utf-8')
```

### File Management Methods

#### list_files()

List files in GCS bucket.

```python
list_files(
    pattern='*',
    bucket_name=None,
    directory=None,
    recursive=False
) -> list
```

**Example:**
```python
# List all CSV files
csv_files = storage.list_files('*.csv')

# List files recursively
all_files = storage.list_files('*', recursive=True)

# List files in specific directory
files = storage.list_files('data_*', directory='experiments')
```

#### copy_between_buckets()

Copy data between GCS locations.

```python
copy_between_buckets(source_path, destination_path) -> bool
```

**Example:**
```python
# Copy within same bucket
storage.copy_between_buckets('old_data.csv', 'backup/old_data.csv')

# Copy between buckets
storage.copy_between_buckets(
    'gs://source-bucket/data.csv',
    'gs://dest-bucket/data.csv'
)
```

#### delete_file()

Delete file from GCS bucket.

```python
delete_file(
    filename,
    bucket_name=None,
    directory=None,
    confirm=True
) -> bool
```

**Example:**
```python
# Delete with confirmation
storage.delete_file('old_file.csv')

# Delete without confirmation
storage.delete_file('temp_file.csv', confirm=False)
```

#### get_file_info()

Get information about a file in GCS.

```python
get_file_info(
    filename,
    partial_string=False,
    bucket_name=None,
    directory=None
) -> Optional[Dict]
```

**Example:**
```python
# Get info for exact filename
info = storage.get_file_info('data.csv')

# Search with partial filename
info = storage.get_file_info('experiment', partial_string=True)
```

## Supported File Formats

### DataFrames
- **CSV** (`.csv`): Standard comma-separated values
- **TSV** (`.tsv`): Tab-separated values
- **Excel** (`.xlsx`): Microsoft Excel format
- **Parquet** (`.parquet`): Columnar storage format
- **JSON** (`.json`): JavaScript Object Notation

### Images and Plots
- **PNG** (`.png`): Portable Network Graphics
- **JPEG** (`.jpg`, `.jpeg`): Joint Photographic Experts Group
- **PDF** (`.pdf`): Portable Document Format
- **SVG** (`.svg`): Scalable Vector Graphics
- **EPS** (`.eps`): Encapsulated PostScript
- **TIFF** (`.tiff`): Tagged Image File Format

### Generic Files
- Any file type supported through binary handling

### Error Handling Best Practices

```python
# Always check return values
if storage.save_data_to_bucket(df, 'important_data.csv'):
    print("Data saved successfully")
else:
    print("Failed to save data")

# Handle None returns from read operations
data = storage.read_data_from_bucket('data.csv')
if data is not None:
    print(f"Loaded {len(data)} rows")
else:
    print("Failed to load data")
```

## Environment-Specific Usage

### All of Us Researcher Workbench
```python
# Usually auto-detects from WORKSPACE_BUCKET
storage = GCPDataStorage()
```

### Google Colab
```python
# May need to authenticate first
from google.colab import auth
auth.authenticate_user()
storage = GCPDataStorage(bucket_name='your-bucket')
```

### Local Development
```python
# Ensure gcloud is configured
# gcloud auth application-default login
storage = GCPDataStorage(bucket_name='your-bucket', project_id='your-project')
```

## Troubleshooting

### Common Issues

1. **Bucket Access Denied**
   - Ensure proper IAM permissions
   - Check bucket name spelling
   - Verify authentication

2. **Auto-detection Failures**
   - Set environment variables explicitly
   - Pass parameters to constructor

3. **File Format Errors**
   - Check file extensions
   - Verify data types match expected formats

4. **Network Issues**
   - Check internet connectivity
   - Verify GCS endpoint accessibility

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
storage = GCPDataStorage()
```

## Security Considerations

- Never hardcode credentials in code
- Use IAM roles and service accounts
- Implement least-privilege access
- Monitor bucket access logs
- Use encryption for sensitive data

## Performance Tips

- Use Parquet format for large DataFrames
- Batch operations when possible
- Consider data compression
- Use appropriate file formats for your use case
- Monitor storage costs and usage

## Contributing

This tool is designed for extensibility. To add new file format support:

1. Add format detection logic in save/read methods
2. Implement format-specific handlers
3. Update supported formats documentation
4. Add appropriate error handling

## License

This code is provided as-is for educational and research purposes. Please ensure compliance with your organization's policies when using in production environments.
