import os
import shutil

org_folder_path = "./해서/"
mv_folder_path = "./combine_dataset/"

# new create folder
os.makedirs(mv_folder_path, exist_ok=True)

sub_folder_list = [f for f in os.listdir(org_folder_path)
                  if os.path.isdir(os.path.join(org_folder_path, f))]

# print(sub_folder_list)
for sub_folder in sub_folder_list:
    new_folder = sub_folder[3:]

    mv_dst_folder = os.path.join(mv_folder_path, new_folder)
    os.makedirs(mv_dst_folder, exist_ok=True)

    scr_folder = os.path.join(org_folder_path, sub_folder)
        
    # subfolder image data get
    files_list = [f for f in os.listdir(scr_folder)]

    for file in files_list :
        scr_json_path = os.path.join(scr_folder, file)
        dst_json_path = os.path.join(mv_dst_folder, file)
        shutil.move(scr_json_path, dst_json_path)

    print(f"{sub_folder} moved")
        

print("Data Moved...")