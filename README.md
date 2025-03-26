# gc_data_storage: Repository for package aou_data_storage

## Functions in the aou_data_storage package.
### `save_data_to_bucket()`
Function to copy data from the persistent disk into the Workspace Bucket. It supports dataframes, plots and more. The inputs are as follows:

**INPUTS**
  - 'data' (required): an object; the dataframe or plot to be saved. To save a file (e.g. .py, .text), use 'df = None'.
     - For dataframes, the currently supported extensions: .csv, .tsv, .xlsx, .parquet. 
     - For plots, the currently supported extensions: .png, .jpeg, .bmp, .tiff, .pdf, .emf. Function can be used for other files but they need to be saved to the persistent disk first.
  - 'filename' (required): a string; the name of the file to save data, including file extension, in the bucket.
  - 'from_directory' (default = 'data/shared'): a string; the bucket directory where you wish to save the data.
  - 'index' (default = True): boolean; For dataframes, should the dataframe index be saved?
  - 'dpi' (default = 'figure'): float or 'figure; For plots, what resolution? Floats should be in dots per inch. If 'figure', it will use the figure's dpi value.

**OUTPUT**: A confirmation and location in the bucket where the data was saved.

### `read_data_from_bucket()`
Function to copy data from the Workspace Bucket into the persistent disk. It supports dataframes, plots and more. The inputs are as follows:

**INPUTS**
  - 'filename' (required): A string; the name of the file in the bucket, including file extension.
     - For dataframes, the currently supported extensions: .csv, .tsv, lsx, .parquet
     - For plots, the currently supported extensions: .png, .jpeg, .bmp, .tiff, .pdf, .emf. Function can be used for other files but they will just be saved to the persistent disk.
  - 'to_directory' (default = 'data/shared'): A string; the bucket directory where your data was saved.
  - 'keep_copy_in_pd' (default = True): boolean; if True, the file will be saved on the persistent disk as well. Otherwise, it will only be returned as a dataframe. There will be no copy in the persistent disk. For non-supported extensions 'keep_copy_in_pd' has no effect. The file will be copied in the persistent disk regardless.

**OUTPUT**: A pandas dataframe or a plot image.

### `list_saved_data()`
Function to list data saved in the workspace bucket or in the persistent disk. The inputs are as follows:

**INPUTS**
  - 'in_bucket' (default = True): boolean; list data in the bucket or the persistent disk? Any value other than 'True', will list data in the persistent disk.
  - 'in_directory' (default = 'data/shared' for the bucket and current notebook directory for the persistent disk): which directory to use?
  - 'pattern' (default = '*') which pattern to use for the files to be listed?

**OUTPUT**: List of files in the specified bucket or persistent disk location.

### `copy_from_bucket_to_bucket()`
Function to copy data saved from Bucket to the same bucket or another bucket. If the buckets are different, the user must be owner of both workspaces.

**INPUTS**
  - 'origin_filename': the name of the file (with extension) to be copied from the original bucket to the destination bucket. 
     - name should have the format 'gs//bucketid/dir1/dir2'
     - Can be any data type (e.g dataframe, plot, text file, code file, etc.)
  - origin_bucket_directory: full name of the directory where data is located       
  - destination_bucket_directory: full name of the directory where the user wants to copy 'data'.
  - destination_filename (Default = origin_filename). The name of the file in the destination bucket.

**OUTPUT**: A confirmation and location of the data copied.


## Using `aou_data_storage` 

### How to install the package?
!pip install aou_data_storage

### Saving data - examples
import aou_data_storage as ds

#### Saving a dataframe to the Google Cloud bucket
Saving 'df' as 'example.csv' in the bucket. By default, it will be saved with index under the 'data/shared' directory.

```ds.save_data_to_bucket(data =df, filename = 'example.csv')```

Saving 'df' as 'example.csv' in the bucket without index under subfolder 'user1' in the 'data/shared' directory.

```ds.save_data_to_bucket(data = df, filename = 'example.tsv', to_directory= 'data/shared/user1', index = False)```

#### Saving a plot to the Google Cloud bucket
Saving 'plot1' as 'plot1.jpeg' in the bucket. By default, it will be saved with index under the 'data/shared' directory.

```ds.save_data_to_bucket(data = plot1, filename = 'plot1.jpeg')```

#### Saving other data types to the Google Cloud bucket
Saving 'fake_file.text' under a subfolder 'user1' in the 'data/shared' directory.

```ds.save_data_to_bucket(data = None, filename = 'fake_file.txt', to_directory= 'data/shared/user1')```


### Reading data - examples

Reading data from the bucket as a dataframe. By default, it will be read from 'data/shared' directory and a copy will be kept in the persistent disk.

```df1 = read_data_from_bucket('example.csv')```

```plot1 = read_data_from_bucket('plot1.jpeg')```

Reading data saved under the 'data/shared/aymone' directory. We do not want a copy in the persistent sisk

```df2 = read_data_from_bucket('example.tsv', from_directory = 'data/shared/user1', keep_copy_in_pd=False)```


### Listing data - examples

List all the files in the bucket 'data/shared' directory. This is the default.

```list_saved_data()```

List all the csv files in the bucket directory 'data/shared/user1'.

```list_saved_data(in_directory='data/shared/user1', pattern = '*csv')```

List all the files in the persistent disk.

```list_saved_data(in_bucket= False)```

### Copy data from bucket to bucket - examples
Copy data from bucket 1 to bucket 2. 'bucket_id' has the format 'gs//bucketid'

```ds.copy_from_bucket_to_bucket(origin_filename = 'example.csv'
                           , origin_bucket_directory = f"{bucket1_id}/data/shared"
                           , destination_bucket_directory = f"{bucket2_id}/data/shared")```
