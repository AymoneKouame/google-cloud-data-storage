#SET UP FOR gc_data_storage - updated 4/18/2025

from setuptools import setup, find_packages

setup(
    name='gc_data_storage',
    version='2.1.0',
    author='Aymone Jeanne Kouame',
    author_email='aymone.jk@gmail.com',
    description= "Python utility for data storage in Google Cloud Environments.",
    long_description= """
gc_data_storage lets you easily move data between your development environment (e.g. Jupyter Notebook) and your Google Cloud Workspace bucket. 
It integrates 'gcloud storage' command line tool (please install and use version 1.1.0 to use 'gsutil'.).

 * Save data from your development environment to the bucket.

 * Read data from the bucket into your development environment, with the option to keep a copy in the persistent disk.

 * Copy data between different directories within the bucket or between two different buckets owned by the user.

 * Obtain a list of data saved in the bucket or the persistent disk.

 * Delete data saved in the bucket or the persistent disk.

gc_data_storage was originally written to be used within the All of Us Researcher Workbench environment but can be used in other Google Cloud Environments.

```
#install the package if not already done
##pip install gc-data-storage 

#import and initialize
## When initializing,  use the default AllofUS Researcher workbench bucket or input your own
from gc_data_storage import gc_data_storage as gs
gs = gs()

#list data in the bucket root directory 
gs.list_saved_data()
```

More information, including examples, at https://github.com/AymoneKouame/google-cloud-data-storage.""",

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