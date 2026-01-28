import json
import os

def convert_txt_to_doccano_jsonl(input_path, output_path):
    """
    将纯文本文件转换为 Doccano 兼容的 JSONL 格式 (unlabeled)。
    每行文本将作为一个独立的标注任务。
    """
    if not os.path.exists(input_path):
        print(f"错误: 找不到输入文件 {input_path}")
        return

    print(f"--- 图正在转换格式 ---")
    print(f"源文件: {input_path}")
    
    valid_count = 0
    
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        
        # 读取并在内存中去重（虽然之前脚本做过，这里再保险一次）
        lines = [line.strip() for line in f_in if line.strip()]
        
        for idx, text in enumerate(lines):
            # 构造 Doccano 标准格式字典
            # new.txt 格式: {"id": 1, "text": "...", "Comments": [], "label": []}
            entry = {
                "id": idx + 1,  # ID 从 1 开始
                "text": text,
                "Comments": [],
                "label": [input]     # 初始为空，等待人工标注
            }
            
            # 写入 JSONL (每行一个 JSON 对象)
            f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            valid_count += 1

    print(f"转换完成！")
    print(f"生成条目: {valid_count}")
    print(f"输出文件: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    # 使用上一战生成的精炼文件作为输入 source
    source_file = r"c:\Users\Administrator\Desktop\ebuy\back\doccano_refined_final.txt"
    # 生成可直接导入 Doccano 的 jsonl 文件
    target_file = r"c:\Users\Administrator\Desktop\ebuy\back\doccano_import_ready.jsonl"
    
    convert_txt_to_doccano_jsonl(source_file, target_file)
