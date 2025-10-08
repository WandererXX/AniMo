data_dir = './data'
import os
import zipfile
import os
import shutil

def unzip_file(zip_path, extract_to):
    """Extracts the contents of a zip file to a specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def cleanup_directory(extract_to):
    """Removes the specified directory and its contents."""
    shutil.rmtree(extract_to)

zipname_ls = [fn for fn in os.listdir(data_dir) if fn.endswith('.zip')]
# idx = zipname_ls.index('Standard_Donkey_Juvenile.ovl.zip')
# zipname_ls = zipname_ls[idx:]

from tqdm import tqdm
from utils.preprocess import convert_json_2_npy

# cleanup_directory(os.path.join(data_dir, 'extracted'))

for zipname in zipname_ls:
    zippath = os.path.join(data_dir, zipname)
    print('zippath:', zippath)
    unzip_file(zippath, os.path.join(data_dir, 'extracted'))

    
    data_processed_dir = './data_processed/'
    os.makedirs(data_processed_dir, exist_ok=True)
    
    try:
        ls_all = os.listdir(os.path.join(data_dir, 'extracted'))
    except Exception:
        continue
    
    for fn in tqdm(ls_all):
        p = os.path.join(os.path.join(data_dir, 'extracted') ,fn)
        try:
            convert_json_2_npy(p, os.path.join(data_processed_dir, os.path.basename(p)+ '.npy'))
        except Exception:
            # try:
            #     cleanup_directory(os.path.join(data_dir, 'extracted'))
            # except Exception:
            #     pass
            pass

    try:
        cleanup_directory(os.path.join(data_dir, 'extracted'))
    except Exception:
        pass

