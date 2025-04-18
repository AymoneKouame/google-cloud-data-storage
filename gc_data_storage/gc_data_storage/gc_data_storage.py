"""
Author: Aymone Jeanne Kouame
Date Released: 03/26/2025
Last Updated: 04/17/2025  
"""

import pandas as pd
import os
import subprocess
from google.cloud import storage
from google.api_core import exceptions
from IPython.display import Image
import pkg_resources

class gc_data_storage:
    
    def __init__(self, bucket = os.getenv('WORKSPACE_BUCKET'), directory = ''):

        self.bucket = bucket
        self.directory = directory
        
    def error_handling(self, bucket_id):

        bucket_name = bucket_id.replace('gs://','')
        try:
            storage.Client().bucket(bucket_name).exists()
        except exceptions.Forbidden as err:
            print(f"Forbidden error for '{bucket_name}':", err)
            print(f"Please enter the correct bucket name.\n")
        except exceptions.Unauthorized as err:
            print(f"Unauthorized error for '{bucket_name}':", err)
            print(f"Please enter the correct bucket name.\n")
        except exceptions.NotFound as err:
            print(f"NotFound error for '{bucket_name}':", err)
            print(f"Please enter the correct bucket name.\n")
        except ValueError as err:
            print(f"ValueError error for '{bucket_name}':", err)
            print(f"Please enter the correct bucket name.\n")
        except FileNotFoundError as err:
            print(f"FileNotFoundError error for '{bucket_name}':", err)
            print(f"Please enter the correct bucket name and/or filename.")            
    
    def README(self):
        
        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ README: How to use gc_data_storage?~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
gc_data_storage lets you easily move data between your development environment (e.g. Jupyter Notebook) and your Google Cloud Workspace bucket. 
It integrates the command line tool gsutil.

  * Use `save_data_to_bucket(data, filename)` to save data from your development environment to the bucket.

  * Use `read_data_to_bucket(filename)` to read data from the bucket into your development environment, with the option to keep a copy in the disk.

  * Use `copy_from_bucket_to_bucket(origin_filename, destination_bucket)` to copy data between different directories within the same bucket or between two different buckets owned by the user.

  * Use `list_saved_data()` to obtain a list of data saved in the bucket or the disk.

  * Use `delete_saved_data(directory, filename)` to delete data saved in the bucket or the disk. The default = 'bucket'.
  For the disk, `bucket_or_disk = 'disk'`. For deletions, the filename and directory where the file is located are mandatory.
  Please USE this function WITH CAUTION.
  
gc_data_storage was originally written to be used within the All of Us Researcher Workbench environment but can be used in other Google Cloud Environments.

    ```
    # Example code
    from gc_data_storage import gc_data_storage as gs

    ## initialize (when initializing,  use the default All of US Researcher workbench bucket or input your own.
    gs = gs()

    ## list data in the bucket root directory 
    gs.list_saved_data()
    ```
More information, including examples, at https://github.com/AymoneKouame/google-cloud-data-storage/ .

        """)    

    def save_data_to_bucket(self
                            , data, filename
                            , bucket = None
                            , directory = None
                            , index:bool = True
                            , dpi = 'figure'):
        
        if bucket == None: bucket = self.bucket
        if directory == None: directory = self.directory
        
        self.error_handling(bucket)
        
        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Saving data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    To location =  '{bucket}/{directory}'
        """)

        full_filename = f'{bucket}/{directory}/{filename}'.replace('//','/').replace('gs:/','gs://')      
        file_ext = '.'+filename.split('.')[1].lower()

        fun_dd = {'.csv': pd.DataFrame.to_csv , '.xlsx': pd.DataFrame.to_excel, '.parquet': pd.DataFrame.to_parquet}

        df_extensions = ['.csv', '.xlsx', '.tsv', '.parquet']
        plot_extensions = ['.png', '.jpeg', '.bmp', '.tiff', '.pdf', '.emf']

        if file_ext in df_extensions:
            if file_ext == '.tsv': 
                print(f""" [Running command: "pd.DataFrame.to_csv(data, {full_filename}, sep="\t")"]\n""")
                pd.DataFrame.to_csv(data, full_filename, sep="\t")

            else: 
                print(f""" [Running command: "{fun_dd[file_ext]}(data, {full_filename}, index = {index})"]\n""")
                fun_dd[file_ext](data, full_filename, index = index)

            print(f"Dataframe saved as '{filename}' in location.")
     
        elif file_ext in plot_extensions:   
            data.savefig(filename, dpi = dpi)  
            print(f""" [Running command: "gsutil cp {filename} {full_filename}]\n""") 
            result = subprocess.run(["gsutil", "cp", filename, full_filename], capture_output=True, text=True)
            print(result.stderr, result.stdout)
  
        else:
            print(f"""
    Your file extension is NOT in {df_extensions+plot_extensions}.
    We assume it is already saved to your disk.\n""")
            print(f""" [Running command: "gsutil cp {filename} {full_filename}]\n""")
            result = subprocess.run(["gsutil", "cp", filename, full_filename], capture_output=True, text=True)
            print(result.stderr, result.stdout)


    def read_data_from_bucket(self
                              , filename
                              , bucket = None
                              , directory = None
                              , save_copy_in_disk:bool = False):
        
        if bucket == None: bucket = self.bucket
        if directory == None: directory = self.directory
            
        self.error_handling(bucket)
        
        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Reading data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    From location =  '{bucket}/{directory}'
        """)

        full_filename = f'{bucket}/{directory}/{filename}'.replace('//','/').replace('gs:/','gs://')  
        file_ext = '.'+filename.split('.')[1].lower()

        df_extensions = ['.csv', '.xlsx', '.tsv', '.parquet']
        plot_extensions = ['.png', '.jpeg', '.bmp', '.tiff', '.pdf', '.emf']

        fun_dd = {'.csv': pd.read_csv, '.xlsx': pd.read_excel, '.parquet': pd.read_parquet}

        if file_ext in df_extensions:
            if file_ext == '.tsv':
                print(f""" [Running command: "pd.read_csv({full_filename}, sep="\t")"]\n""") 
                data = pd.read_csv(full_filename, sep="\t", engine = 'pyarrow')
                
            elif file_ext == '.xlsx':
                data = fun_dd[file_ext](full_filename)

            else:
                print(f""" [Running command: "{fun_dd[file_ext]}({full_filename})"]\n""")
                data = fun_dd[file_ext](full_filename, engine = 'pyarrow')
      
        elif file_ext in plot_extensions:   
            print(f""" [Running command: "gsutil cp {full_filename} {filename}"]\n""")     
            result = subprocess.run(["gsutil", "cp", full_filename, filename], capture_output=True, text=True)
     
            data = Image(filename)
            subprocess.run(["rm", filename], capture_output=True, text=True).stdout.strip("\n")
                
        elif file_ext not in df_extensions+plot_extensions:

            print(f""" [Running command: "gsutil cp {full_filename} {filename}"]\n""") 
            result = subprocess.run(["gsutil", "cp", full_filename, filename], capture_output=True, text=True)
            data = '' 
            if result.returncode == 0: 
                print(f'''
    Your file extension is NOT in {df_extensions+plot_extensions}
    It will just be copied to the disk.''')

        if save_copy_in_disk == True:
            result = subprocess.run(["gsutil", "cp", full_filename, filename], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"'{filename}' is also in the disk.")               

        return data

    def copy_from_bucket_to_bucket(self
                                   , origin_filename
                                   , destination_bucket
                                   , origin_bucket = None
                                   , origin_directory = None
                                   , destination_directory = None
                                   , destination_filename = None
                                   ):
        
        if destination_filename == None: destination_filename = origin_filename
        if origin_bucket == None: origin_bucket = self.bucket
        if origin_directory == None: origin_directory = self.directory
        if destination_directory == None: destination_directory = self.directory
       
        self.error_handling(origin_bucket)
        self.error_handling(destination_bucket)
        
        
        origin_fullfilename = f"{origin_bucket}/{origin_directory}/{origin_filename}".replace('//','/').replace('gs:/','gs://')  
        dest_fullfilename = f"{destination_bucket}/{destination_directory}/{destination_filename}".replace('//','/').replace('gs:/','gs://')  

        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ copying data between buckets ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    From {origin_fullfilename}
    To {dest_fullfilename}
        """)

        subprocess.run(["gsutil", "cp", origin_fullfilename, dest_fullfilename])


    def list_saved_data(self
                        , bucket_or_disk = 'bucket'
                        , bucket = None
                        , directory = None
                        , pattern = '*'):
 
        if bucket == None or bucket == 'bucket': bucket = self.bucket
             
        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Listing data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """)
        
        if (bucket_or_disk.lower()  in  ['bucket','']):
            if directory == None: directory = self.directory
            self.error_handling(bucket)
            location = f"{bucket}/{directory}/{pattern}".replace('//','/').replace('gs:/','gs://')            
            print(f'In {location}')
            print(f""" [Running command: "gsutil ls {location}"]\n""") 
            subprocess.run(["gsutil", "ls", location])
               
                
        elif (bucket_or_disk.lower() in ['persistent disk','persistent_disk', 'disk']) \
                or (bucket_or_disk.lower() not in ['bucket','']) :
            if directory == None: location = pattern
            else: location = f"{directory}/{pattern}"#.replace('//*','*')
            
            print(f'In disk {location}')
            print(f""" [Running command: "os.system('ls {location}')"]\n""")  
            os.system(f'ls {location}')



    def delete_saved_data(self
                          , directory, filename
                          , bucket_or_disk = 'bucket'
                          , bucket = None):
 
        if bucket == None or bucket == 'bucket': bucket = self.bucket             
        print(f"""
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Deleting data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Please USE WITH CAUTION.
        """)
        
        if (bucket_or_disk.lower()  in  ['bucket','']):
            self.error_handling(bucket)
            location = f"{bucket}/{directory}/{filename}"           
            print(f'Deleting {location}')

            delete_answer = input('ARE YOU SURE YOU WANT TO DELETE {location} ? YES or NO')
            if delete_answer == 'YES':
                print(f""" [Running command: "gsutil rm {location}"]\n""")
                subprocess.run(["gsutil", "rm", location])
                
                
        elif (bucket_or_disk.lower() in ['persistent disk','persistent_disk', 'disk']) \
                or (bucket_or_disk.lower() not in ['bucket','']) :
            location = f"{directory}/{filename}"
            print(f'Deleting {location}')

        delete_answer = input(f'ARE YOU SURE YOU WANT TO DELETE {location} ? YES or NO')
        if delete_answer == 'YES':
            print(f""" [Running command: "os.system('rm {location}')"]\n""")
            os.system(f'rm {location}')
 
