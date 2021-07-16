import os
import time
from pathlib import Path

side_project_dir_path = Path(__file__).parents[2]
data_dumps_path = os.path.join(side_project_dir_path, 'data_dumps', 'ImageClassification', 'StockCarShops')

print(len(os.listdir(data_dumps_path)))
for count, file_name in enumerate(os.listdir(data_dumps_path)):
    file_path = os.path.join(data_dumps_path, file_name)
    print(count, file_name, time.ctime(os.path.getctime(file_path)), sep='\n')
    print()
    if count == 5:
        break
