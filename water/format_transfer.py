import json
import os

def transfer_format(input_file, output_file):
    """
    读取 old.txt，智能解析每行内容，保留原有的 label 并统一转换为 Doccano JSONL 格式。
    """
    if not os.path.exists(input_file):
        print(f"错误：找不到输入文件 {input_file}")
        print("请确保你已经在 back 文件夹下放入了名为 old.txt 的源文件。")
        return

    print(f"正在读取: {input_file} ...")
    
    processed_count = 0
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for i, line in enumerate(f_in):
            line = line.strip()
            if not line:
                continue
            
            # 目标结构
            new_entry = {
                "id": i + 1,
                "text": "",
                "Comments": [],
                "label": []
            }
            
            try:
                # 关键步骤：尝试将当前行作为 JSON 解析
                # 如果这一行本身就是 JSON 格式（包含 label），这里就能解包出来
                original_data = json.loads(line)
                
                # 1. 提取文本 (兼容 text/content/data 字段)
                if isinstance(original_data, dict):
                    if "text" in original_data:
                        new_entry["text"] = original_data["text"]
                    elif "content" in original_data:
                        new_entry["text"] = original_data["content"]
                    elif "data" in original_data:
                        new_entry["text"] = original_data["data"]
                    else:
                        # 字典里没找到常见文本字段，转存整个字典字符串
                        new_entry["text"] = json.dumps(original_data, ensure_ascii=False)
                    
                    # 2. 提取并保留 Label (兼容 label/labels/entities)
                    if "label" in original_data:
                        new_entry["label"] = original_data["label"]
                    elif "labels" in original_data:
                        new_entry["label"] = original_data["labels"]
                    elif "entities" in original_data:
                        new_entry["label"] = original_data["entities"]
                        
                    # 3. 保留 Comments
                    if "Comments" in original_data:
                        new_entry["Comments"] = original_data["Comments"]
                else:
                    # 如果 json.loads 出来是列表或基础类型，直接转字符串
                    new_entry["text"] = str(original_data)

            except json.JSONDecodeError:
                # 如果解析失败，说明这一行是纯文本（没有 label）
                # 这种情况下只能保留文本，label 为空
                new_entry["text"] = line
            
            # 写入结果
            f_out.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
            processed_count += 1
            
    print(f"转换完成！")
    print(f"共处理 {processed_count} 条数据")
    print(f"生成文件: {output_file}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Administrator\Desktop\ebuy\back"
    # 输入文件
    old_path = os.path.join(base_dir, "old.txt")
    # 输出文件
    new_path = os.path.join(base_dir, "new_formatted.jsonl")
    
    transfer_format(old_path, new_path)
