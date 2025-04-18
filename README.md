# Description
`gc_data_storage` lets you easily move data between your development environment (e.g. Jupyter Notebook) and your Google Cloud Workspace bucket. 
It integrates the command line tool gsutil.

 * Save data from your development environment to the bucket.
 * Read data from the bucket into your development environment, with the option to keep a copy in the disk.
 * Copy data between different directories within the bucket or between two different buckets owned by the user.
 * Obtain a list of data saved in the bucket or the disk.

`gc_data_storage` was originally written to be used within the All of Us Researcher Workbench environment but can be used in other Google Cloud Environments. 

 * At initialization, the default bucket used for all the functions below is the Workspace environment bucket and the default directory is the root.
 * The user can define another default bucket (format `gs//yourbucketname`) and/or another default directory to be used for all the functions below. 


# Functions in the 'gc_data_storage' package.

## `save_data_to_bucket()`
Function to copy data from the disk into the Workspace Bucket. The default bucket in the All of US Researcher Workbench). The user is free to add their own default bucket `gs//yourbucketname` upon initiating the function.
The package supports dataframes, plots and more. The inputs are as follows:

**INPUTS**
  - **'data' (required)**: an object; the dataframe or plot to be saved. To save a file (e.g. .py, .text), use 'df = None'.
     - For dataframes, the currently supported extensions: .csv, .tsv, .xlsx, .parquet. 
     - For plots, the currently supported extensions: .png, .jpeg, .bmp, .tiff, .pdf, .emf. Function can be used for other files but they need to be saved to the disk first.
  - **'filename' (required)**: a string; the name of the file to save data, including file extension, in the bucket.
  - 'bucket' (default = bucket defined at initialization): A string of format `gs//yourbucketname` defining the bucket where your data is to be saved.
  - 'directory' (default = directory defined at initialization): a string; the bucket directory where you wish to save the data.
  - 'index' (default = True): boolean; For dataframes, should the dataframe index be saved?
  - 'dpi' (default = 'figure'): float or 'figure; For plots, what resolution? Floats should be in dots per inch. If 'figure', it will use the figure's dpi value.

**OUTPUT**: A confirmation and location in the bucket where the data was saved.

## `read_data_from_bucket()`
Function to copy data from the Workspace Bucket into the disk. It supports dataframes, plots and more. The inputs are as follows:

**INPUTS**
  - **'filename' (required)**: A string; the name of the file in the bucket, including file extension.
     - For dataframes, the currently supported extensions: .csv, .tsv, lsx, .parquet
     - For plots, the currently supported extensions: .png, .jpeg, .bmp, .tiff, .pdf, .emf. Function can be used for other files but they will just be saved to the disk.
  - 'bucket' (default = bucket defined at initialization): A string of format `gs//yourbucketname` defining the bucket where the data to be read is.
  - 'directory' (default = directory defined at initialization): A string; the bucket directory where your data was saved. 
  - 'save_copy_in_disk' (default = True): boolean; if True, the file will be saved on the disk as well. Otherwise, it will only be returned as a dataframe. There will be no copy in the disk. 
For non-supported extensions 'save_copy_in_disk' has no effect. The file will be copied in the disk regardless.
    
**OUTPUT**: A pandas dataframe or a plot image.


## `copy_from_bucket_to_bucket()`
Function to copy data saved from Bucket to the same bucket or another bucket. If the buckets are different, the user must be owner of both workspaces.

**INPUTS**
  - **'origin_filename' (required)**: A string; the name of the file (with extension, for example 'example.csv') to be copied from the original bucket to the destination bucket. 
     - Can be any data type (e.g dataframe, plot, text file, script, etc.)
  - **'destination_bucket' (required)**: A string; the name of the bucket to copy the data to (format: 'gs://destination-bucket-name').
  - 'origin_bucket' (default = bucket defined at initialization): A string; the name of the bucket where the data to copy is located (format: 'gs://destination-bucket-name').
  - 'origin_directory' (default = directory defined at initialization): A string; the name of the directory within the origin bucket where the data to copy is located.
  - 'destination_directory' (default = same name as directory defined at initialization): A string; the name of the directory within the destination bucket where the data is to be copied.
  - 'destination_filename' (Default = 'origin_filename'). A string; The new name of the file in the destination bucket.

**OUTPUT**: A confirmation and location of the data copied.


## `list_saved_data()`
Function to list data saved in the workspace bucket or in the disk. The inputs are as follows:

**INPUTS**
  - 'bucket_or_disk' (default = 'bucket'): A string; list data in the bucket or the disk? Enter 'bucket' or 'disk'.
  - 'bucket' (default = bucket defined at initialization): A string of format `gs//yourbucketname` defining the bucket where the data is to list is.
  - 'directory': A string. Which directory to use? If bucket_or_disk = 'bucket', the default is directory defined at initialization. If bucket_or_disk = 'disk', the default directory is the root disk directory.
  - 'pattern' (default = '*') which pattern to use for the files to be listed?

**OUTPUT**: List of files in the specified bucket or disk location.

## `delete_saved_data()`
Function to list data saved in the workspace bucket or in the disk. The inputs are as follows:

**INPUTS**
  - **'filename' (required)**: A string; the name of the file in the bucket or disk to delete, including file extension.
  - 'bucket_or_disk' (default = 'bucket'): A string; Is the data located in the bucket or the disk? Enter 'bucket' or 'disk'.
  - 'bucket' (default = bucket defined at initialization): A string of format `gs//yourbucketname` defining the bucket where the data is to list is.
  - 'directory': A string. Which directory to use? If bucket_or_disk = 'bucket', the default is directory defined at initialization. If bucket_or_disk = 'disk', the default directory is the root disk directory.

**OUTPUT**: List of files in the specified bucket or disk location.

# Using `gc_data_storage` 

### How to install the package?
```
pip install gc_data_storage
```

## Saving data - examples

Initialization: Using the default bucket and root bucket directory in the All of Us Resercher Workbecnch
```
from gc_data_storage import gc_data_storage as gs
gs = gs()
```

OR Initialization: Using another default Google Cloud Workspace Bucket and/or directory
```
from gc_data_storage import gc_data_storage as gs
gs  = gs(bucket = 'gs://your-bucket-name', directory = 'data')
```
### Saving a dataframe to the Google Cloud bucket
Saving 'df' as 'example.csv' in the default bucket and directory.

```
gs.save_data_to_bucket(data =df, filename = 'example.csv')
```

Saving 'df' as 'example.csv' in the default bucket without index under the 'data/shared' directory.

```
gs.save_data_to_bucket(data = df, filename = 'example.tsv', directory= 'data/user1', index = False)
```

### Saving a plot to the Google Cloud bucket
Saving 'plot1' as 'plot1.jpeg' in the default bucket and directory.

```
gs.save_data_to_bucket(data = plot1, filename = 'plot1.jpeg')
```

### Saving other data types to the Google Cloud bucket
Saving 'fake_file.text' in the default bucket under the 'data/user1' directory.

```
gs.save_data_to_bucket(data = None, filename = 'fake_file.txt', directory= 'data/user1')
```


## Reading data - examples

Reading data from the bucket as a dataframe from the default bucket and directory. By default a copy will be also be saved in the disk.

```
df1 = gs.read_data_from_bucket('example.csv')
```

```
plot1 = gs.read_data_from_bucket('plot1.jpeg')
```

Reading data saved under the 'data/user1' directory. We do not want a copy in the disk

```
df2 = gs.read_data_from_bucket('example.tsv', directory = 'data/user1', keep_copy_in_disk=False)
```

## Listing data - examples

List all the files in the default bucket and directory

```
gs.list_saved_data()
```

List all the files in another bucket and directory

```
gs.list_saved_data(bucket = 'gs://other-bucket-name', directory = 'otherdirectory')
```

List all the csv files in the bucket directory 'data/user1'.

```
gs.list_saved_data(directory='data/user1', pattern = '*csv')
```

List all the files in the root disk.

```
gs.list_saved_data(bucket_or_disk = 'disk')
```

## Copy data from bucket to bucket - examples
Copy data from the default bucket and directory to another bucket. The file will be saved under the same name, in a directory with the same name as the default directory.

```
gs.copy_from_bucket_to_bucket(origin_filename = 'example.csv', destination_bucket = "gs://destination-bucket-name")
```

Copy data from the default bucket but the 'data' directory' to another bucket under the 'data2' directory. We also want to change the filename to 'example2.csv' in the destination bucket.

```
gs.copy_from_bucket_to_bucket(origin_filename = 'example.csv', origin_directory = 'data'
                             , destination_bucket = "gs://destination-bucket-name", destination_directory = 'data2', destination_filename = 'example2.csv')
```
