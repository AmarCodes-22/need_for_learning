import os
from pathlib import Path
import shutil
import random
from natsort import natsorted
import cv2 as cv

#* Setting up paths
current_working_dir = os.getcwd()
main_project_path = str(Path(current_working_dir).parents[2])
side_project_path = os.path.join(main_project_path, 
                                'side_projects',
                                'image_classification',
                                'stock_cars')
data_dumps_path = os.path.join(main_project_path, 'side_projects', 'data_dumps')
project_data_path = os.path.join(side_project_path,'new_data')
project_data_shutil_path = os.path.join(side_project_path,'data_shutil')
project_data_dump_path = os.path.join(data_dumps_path, 'ImageClassification', 'StockCarShops')

paths = {
    'main_project': main_project_path,
    'side_project': side_project_path,
    'data_dumps': data_dumps_path,
    'project_data': project_data_path,
    'project_data_dump': project_data_dump_path,
    'project_data_shutil': project_data_shutil_path
}

#* Setting up the files in the datadump
files = []
for file_name in os.listdir(paths['project_data_dump']):
    files.append(file_name)

files = natsorted(files)

#* Class names
class_names = ['gallardo', 'gto', 'clio', 'audi_a4', 'cobalt', 'supra', 'elise', 'audi_a3', 
               'sl500', 'is_300', 'monaro', 'audi_tt', 'db9', 'murcielago', 'clk500', 'rx7', 
               'ford_gt', 'viper', 'mercedes_benz', 'corvette', 'turbo', 'golf_gti', 'carrera_gt', 'cts', 
               'mustang_gt', 'eclipse', 'carrera', 'cayman', 'evolution', 'wrx', 'punto', 'rx8']


for dirpath, dirnames, filenames in os.walk(paths['project_data']):
    print('There are {} directories, {} files in {}'.format(len(dirnames), len(filenames), dirpath))

print(files)

#     class_names = dirnames
#     break

# print(class_names)

#* Done only once(Temporary show for using shutil)
# for i, file_name in enumerate(files):
#     src_path = os.path.join(paths['project_data_dump'], file_name)
#     dirname = os.path.join(paths['project_data_shutil'], class_names[i//25])
#     if not os.path.exists(paths['project_data_shutil']):
#         os.system(f'mkdir {project_data_shutil_path}')
#     if not os.path.exists(dirname):
#         os.system(f'mkdir {dirname}')
#     dst_path = os.path.join(dirname, file_name)
#     shutil.copy(src_path, dst_path)

#* Cropping the data to contain only the game screen
#* Done only once
# for dirpath, dirnames, filenames in os.walk(paths['project_data'])
#     if len(filenames) > 0:
#         for filename in filenames:
#             filepath = os.path.join(dirpath, filename)
#             img = cv.imread(filepath)
#             img = img[175:525, 325:950]
#             cv.imwrite(filepath, img)

#* Creating the train and test directories in each of the class folders
#* Done once only
# for dirpath, dirnames, filenames in os.walk(paths['project_data']):
#     if len(filenames) > 0:
#         train_dir_path = os.path.join(dirpath, 'train')
#         test_dir_path = os.path.join(dirpath, 'test')
#         if not os.path.exists(train_dir_path):
#             os.system('mkdir {}'.format(train_dir_path))
#         if not os.path.exists(test_dir_path):
#             os.system('mkdir {}'.format(test_dir_path))
#         test_files = random.sample(filenames, 5)
#         for file in filenames:
#             src_path = os.path.join(dirpath, file)
#             if file in test_files:
#                 dst_path = os.path.join(test_dir_path, file)
#                 os.system('mv {} {}'.format(src_path, dst_path))
#             else:
#                 dst_path = os.path.join(train_dir_path, file)
#                 os.system('mv {} {}'.format(src_path, dst_path))

# for dirpath, dirnames, filenames in os.walk(paths['project_data']):
#     print('There are {} directories, {} files in {}'.format(len(dirnames), len(filenames), dirpath))
