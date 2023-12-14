import os
import shutil
import random
import json

org_folder_path = "./combine_dataset/"
train_folder_path = "./hansa_dataset/train/"
val_folder_path = "./hansa_dataset/val/"
test_folder_path = "./hansa_dataset/test/"

# new create folder
os.makedirs(train_folder_path, exist_ok=True)
os.makedirs(val_folder_path, exist_ok=True)
os.makedirs(test_folder_path, exist_ok=True)

sub_folder_list = [f for f in os.listdir(org_folder_path)
                  if os.path.isdir(os.path.join(org_folder_path, f))]

random.seed(777)

train_ratio = 0.8 # train 9 val 1
val_ratio = 0.1

# print(sub_folder_list)
for sub_folder in sub_folder_list:
    scr_folder = os.path.join(org_folder_path, sub_folder)
    train_dst_folder = os.path.join(train_folder_path, sub_folder)
    val_dst_folder = os.path.join(val_folder_path,sub_folder)
    test_dst_folder = os.path.join(test_folder_path,sub_folder)

    os.makedirs(train_dst_folder, exist_ok=True)
    os.makedirs(val_dst_folder, exist_ok=True)
    os.makedirs(test_dst_folder, exist_ok=True)
        
    # subfolder image data get
    json_files_list = [f for f in os.listdir(scr_folder) if
                        f.lower().endswith(('.json'))]

    random.shuffle(json_files_list)

    # train 80%
    num_train = int(len(json_files_list) * train_ratio)
    train_files = json_files_list[:num_train]

    for file in train_files :
        try:
            scr_json_path = os.path.join(scr_folder, file)
            dst_json_path = os.path.join(train_dst_folder, file)
            

            img_name = file.replace("json","jpg")
            scr_path = os.path.join(scr_folder, img_name)
            dst_path = os.path.join(train_dst_folder, img_name)
            shutil.copy(scr_path, dst_path)
            shutil.copy(scr_json_path, dst_json_path)

        except Exception as e:
            print(e)

    # val 10%
    num_val = int(len(json_files_list) * val_ratio) + num_train
    val_files = json_files_list[num_train:num_val]

    for file in val_files :
        try:
            scr_json_path = os.path.join(scr_folder, file)
            dst_json_path = os.path.join(val_dst_folder, file)
            
            img_name = file.replace("json","jpg")
            scr_path = os.path.join(scr_folder, img_name)
            dst_path = os.path.join(val_dst_folder, img_name)
            shutil.copy(scr_path, dst_path)
            shutil.copy(scr_json_path, dst_json_path)

        except Exception as e:
            print(e)

    # test 10%
    test_files = json_files_list[num_val:]
    for file in test_files:
        try:
            scr_json_path = os.path.join(scr_folder, file)
            dst_json_path = os.path.join(test_dst_folder, file)
            
            
            img_name = file.replace("json","jpg")
            scr_path = os.path.join(scr_folder, img_name)
            dst_path = os.path.join(test_dst_folder, img_name)

            shutil.copy(scr_path, dst_path)
            shutil.copy(scr_json_path, dst_json_path)

        except Exception as e:
            print(e)

    print(f"{sub_folder} Copied")
        

print("Data Copied...")