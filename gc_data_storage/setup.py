#SET UP FOR GCPDataStorage - updated 7/18/2025

from setuptools import setup, find_packages

setup(
    name='gc-data-storage',
    version='3.0.0',
    author='Aymone Jeanne Kouame',
    author_email='aymone.jk@gmail.com',
    description= "for managing data storage between local environments and Google Cloud Storage (GCS) bucketss.",
    long_description= """

`gc-data-storage` provides a unified interface for saving, reading, and managing various data types including DataFrames, plots, images, and generic files.

 * Save data from your development environment to the bucket.
 * Read data from the bucket into your development environment, with the option to keep a copy in the persistent disk.
 * Copy data between different directories within the bucket or between two different buckets owned by the user.
 * Obtain a list of data saved in the bucket or the persistent disk.
 * Delete data saved in the bucket or the persistent disk.
 * Obtain information on a file, using the full path or a partial string

# Features:

 * Universal GCP Compatibility: Works across all GCP environments including All of Us Researcher Workbench, Google Colab, Vertex AI Workbench, and local development
 * Auto-detection: Automatically detects bucket names and project IDs from environment variables
 * Multi-format Support: Handles DataFrames, plots, images, Excel workbooks, and generic files
 * Robust Error Handling: Comprehensive logging and error management
 * Flexible Path Management: Supports both relative and absolute GCS paths
 * Batch Operations: Copy, list, and delete operations for file management

More information, including code examples, at https://github.com/AymoneKouame/google-cloud-data-storage.""",

    long_description_content_type="text/markdown",
    url = 'https://github.com/AymoneKouame/gc_data_storage/',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires='>=3.6',
)