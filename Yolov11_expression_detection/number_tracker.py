import os

def count_files_recursive(folder_path):
    if not os.path.exists(folder_path):
        return 0
        
    total_files = 0
    # os.walk quét qua mọi ngóc ngách của thư mục
    for root, dirs, files in os.walk(folder_path):
        total_files += len(files)
        
    return total_files

# Sử dụng
folder = "Yolov11_expression_detection"
print(f"Tổng số file (gồm cả thư mục con): {count_files_recursive(folder)}")