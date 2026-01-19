import os

def merge_all_txt_data(input_dir, output_file):
    """
    合并指定目录下所有的 txt 文件并去重。
    """
    seen_lines = set()
    output_filename = os.path.basename(output_file)
    files_processed = 0
    
    print(f"--- 开始合并任务 ---")
    
    # 获取所有txt文件
    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt') and f != output_filename]
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in txt_files:
            file_path = os.path.join(input_dir, filename)
            print(f"正在处理: {filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        clean_line = line.strip()
                        # 去重逻辑：只有非空且没见到过的行才写入
                        if clean_line and clean_line not in seen_lines:
                            outfile.write(clean_line + '\n')
                            seen_lines.add(clean_line)
                files_processed += 1
            except Exception as e:
                print(f"  ! 处理 {filename} 时遇到错误: {e}")

    print(f"\n[任务完成]")
    print(f"成功合并文件数: {files_processed}")
    print(f"去重后总条数: {len(seen_lines)}")
    print(f"最终数据集路径: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    back_folder = r"c:\Users\Administrator\Desktop\ebuy\back"
    merged_file = os.path.join(back_folder, "merged_doccano_dataset.txt")
    
    if not os.path.exists(back_folder):
        os.makedirs(back_folder)
        
    merge_all_txt_data(back_folder, merged_file)
