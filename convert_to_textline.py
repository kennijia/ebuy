import os
import sys

def process_text_to_textline(input_path, output_path):
    """
    将文本文件转换为 doccano 的 Textline 格式：
    1. 合并由于换行符断开的自然段
    2. 每一行代表一个独立的标注文档
    3. 去除多余空行
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        processed_paragraphs = []
        current_paragraph = []
        seen_paragraphs = set()  # 用于记录已出现的段落

        for line in lines:
            stripped = line.strip()
            if stripped:
                current_paragraph.append(stripped)
            else:
                if current_paragraph:
                    full_para = "".join(current_paragraph)
                    if full_para not in seen_paragraphs:
                        processed_paragraphs.append(full_para)
                        seen_paragraphs.add(full_para)
                    current_paragraph = []

        if current_paragraph:
            full_para = "".join(current_paragraph)
            if full_para not in seen_paragraphs:
                processed_paragraphs.append(full_para)
                seen_paragraphs.add(full_para)

        with open(output_path, 'w', encoding='utf-8') as f:
            for para in processed_paragraphs:
                f.write(para + '\n')
        
        print(f"成功转换: {input_path} -> {output_path}")
        print(f"总计生成: {len(processed_paragraphs)} 条标注数据")

    except Exception as e:
        print(f"处理文件 {input_path} 时出错: {e}")

if __name__ == "__main__":
    # 你可以在这里修改输入和输出文件名
    input_file = "back/data1_17.txt"
    output_file = "back/doccano_ready.txt"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    process_text_to_textline(input_file, output_file)
