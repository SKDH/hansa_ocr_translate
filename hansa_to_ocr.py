import xml.etree.ElementTree as et
import os
import shutil
import glob
import json

path = ["train","test","val"]

for p in path:
    annotation_file_path = f"./hansa_dataset/{p}/"
    output_label_save_path = f"./sample_hansa_dataset/{p}/labels"
    output_image_save_path = f"./sample_hansa_dataset/{p}/images"

    os.makedirs(output_image_save_path, exist_ok=True)
    os.makedirs(output_label_save_path, exist_ok=True)

    json_files = glob.glob(os.path.join(annotation_file_path,"*/*.json"))
    for json_f in json_files:

        with open(json_f, 'r', encoding="utf-8") as f:
            data_info = json.load(f)
        
            """
            {
                "Info_Name": "경암유사_01 OCR 최종 DATA", 
                "Info_Description": "한국국학진흥원에서CR용 AI 데이터", 
                "Info_Original_Title": "경암허문경공유사(敬庵許文敬公遺事)", 
                "Info_Original_Author": "허조(許稠)", 
                "Info_Original_Publication": "미상(未詳)", 
                "Info_Original_Categorize": "사부(史部)", 
                "Info_Block": "목판본", 
                "Info_Style": "해서", 
                "Info_Text_Color": "Color", 
                "Info_Distortion": "None",
                "Info_Visibility": "Middle", 
                "Info_Noise": "Middle",
                "Info_Intervention": "Middle", 
                "Info_Image_Licence": "CC BY-SA", 
                "Info_Licenced_Institution": "한국국학진흥원", 
                "Info_Institution_URL": "www.koreastudy.or.kr", 
                "Image_ID": "000000000034704_018", 
                "Image_File_name": "000000000034704_018", 
                "Info_Data_created": "2022-11-04", 
                "Image_Data_captured": "2022-07-27", 
                "Image_Width": 1809, 
                "Image_Height": 3353, 
                "Image_dpi": 300, 
                "Image_color": "Y", 
                "Image_Char_col_no": 20, 
                "Image_Char_row_no": 11, 
                "Image_Text_Coord": 
                [
                    [
                        {"bbox": [1538.5223981433082, 634.7371429272462, 121.0, 121.0, 0, 0], "type": "1", "label": "門"}, 
                        {"bbox": [1543.7237827787455, 761.8456248508323, 115.0, 112.24000000000001, 0, 1], "type": "1", "label": "副"},
            """
            try:
                file_name = data_info['Image_File_name']
                image_name = file_name + ".jpg"
                label_name = file_name + ".txt"
                org_image_path = json_f.replace(".json",".jpg")
                annotations = data_info["Image_Text_Coord"]
        
                mv_image_path = os.path.join(output_image_save_path,image_name)

                shutil.copy(org_image_path, mv_image_path)
                output_file = f"./{output_label_save_path}/gt_{label_name}"

                with open(output_file, 'w', encoding='utf-8') as output_f :
                    lines = []
                    for columns in annotations:
                        for anno in columns:
                            bbox = anno["bbox"]
                            label = anno["label"]

                            x, y, w, h, _, _ = list(map(int,bbox))
                            x1, y1 = x, y
                            x2, y2 = x+w, y
                            x3, y3 = x+w, y+h
                            x4, y4 = x, y+h

                            ocr_line = f"{x1},{y1},{x2},{y2},{x3},{y3},{x4},{y4},{label}\n"
                            lines.append(ocr_line)

                    if lines :
                        output_f.writelines(lines)

            
            except Exception as e:
                print(e)
                print(json_f)

    print(f"{p} Conversion complete ....")
