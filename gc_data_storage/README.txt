Functions in the 'gc-data-storage' package.
- save_data_to_bucket()
- read_data_from_bucket()
- list_files()
- delete_file()
- copy_between_buckets()
- copy_between_buckets()

Using the package

```
pip install gc-data-storage
from gc-data-storage import GCPDataStorage
gs = GCPDataStorage()

gs.list_files()

```

For detailed information, including examples, see https://github.com/AymoneKouame/google-could-data-storage/.