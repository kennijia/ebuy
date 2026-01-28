import json
import os

def convert_json_to_doccano_jsonl(input_file, output_file):
    """
    将 old.json 中的数据转换为 Doccano 标准的 JSONL 格式。
    
    old.json 格式示例:
    {"text": "...", "label": {"OBJ": {"水库": [[1, 2]]}, "ORG": {...}}}
    
    目标 new.jsonl 格式:
    {"id": 1, "text": "...", "Comments": [], "label": [[1, 2, "OBJ"], ...]}
    """
    if not os.path.exists(input_file):
        print(f"错误：找不到输入文件 {input_file}")
        return

    print(f"正在读取: {input_file} ...")
    
    processed_count = 0
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for idx, line in enumerate(f_in):
            line = line.strip()
            if not line:
                continue
            
            try:
                # 解析原始 JSON 行
                data = json.loads(line)
                
                # 开始构造新对象
                new_entry = {
                    "id": idx + 1,
                    "text": data.get("text", ""),
                    "Comments": [],
                    "label": []
                }
                
                # 转换 label 格式
                # old 格式: "label": {"OBJ": {"水库": [[11, 13]], "闸坝": [[14, 16]]}}
                # new 格式: "label": [[11, 13, "OBJ"], [14, 16, "OBJ"]]
                
                raw_labels = data.get("label", {})
                
                # 检查 raw_labels 是否为字典格式（如附件所示）
                if isinstance(raw_labels, dict):
                    for label_type, entity_dict in raw_labels.items():
                        # entity_dict 可能是 {"水库": [[11, 13]], ...}
                        if isinstance(entity_dict, dict):
                            for entity_text, positions in entity_dict.items():
                                # positions 是一个列表的列表，例如 [[11, 13], [30, 32]]
                                for pos in positions:
                                    if len(pos) >= 2:
                                        # Doccano label 格式 [start, end, label_name]
                                        start, end = pos[0], pos[1]
                                        new_entry["label"].append([start, end, label_type])
                
                # 写入文件
                f_out.write(json.dumps(new_entry, ensure_ascii=False) + "\n")
                processed_count += 1
                
            except json.JSONDecodeError:
                print(f"无法解析第 {idx+1} 行: {line[:50]}...")
            except Exception as e:
                print(f"处理第 {idx+1} 行时发生错误: {e}")

    print(f"转换完成！")
    print(f"共生成 {processed_count} 条数据")
    print(f"输出文件: {output_file}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Administrator\Desktop\ebuy\back"
    old_json = os.path.join(base_dir, "old.json") # 注意用户附件文件名是 old.json
    new_jsonl = os.path.join(base_dir, "final_doccano_labeled.jsonl")
    
    convert_json_to_doccano_jsonl(old_json, new_jsonl)
