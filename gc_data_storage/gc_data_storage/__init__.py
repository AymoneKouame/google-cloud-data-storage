from gc_data_storage.gc_data_storage import gc_data_storage
import pkg_resources

def install_if_not_installed(modules):  
    uninstalled_packages = [p for p in modules if p not in sorted(["%s==%s" % (i.key, i.version) for i in pkg_resources.working_set])]
    uninstalled_packages_f = " ".join(uninstalled_packages)
    res = subprocess.run(['pip', 'install', '--upgrade', uninstalled_packages_f], capture_output=True)

install_if_not_installed(modules = ['pyarrow', 'openpyxl'])