import re
import os

def refine_for_doccano(input_path, output_path):
    """
    将混乱的法规文本精炼为 Doccano 友好的事实语料格式
    """
    if not os.path.exists(input_path):
        print("未找到原始合并文件。")
        return

    unique_sentences = set()
    
    # 匹配第X条、第X章、附件、以及条款编号如 (一)、1. 等
    noise_patterns = [
        re.compile(r'^第[一二三四五六七八九十百]+[条章]\s*'),
        re.compile(r'^\([一二三四五六七八九十]\)\s*'),
        re.compile(r'^\d+[\.、]\s*'),
        re.compile(r'^附[：:]|^附件[：:]'),
        re.compile(r'（\d{4}年.*）|〔\d{4}〕\d+号')
    ]

    print(f"--- 正在精炼语料库 ---")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_path, 'w', encoding='utf-8') as out:
        for line in lines:
            # 丢弃文件注释和网页噪音
            if line.startswith('//') or '来源：' in line or '字号：' in line:
                continue
            
            text = line.strip()
            if not text: continue

            # 移除条文编号
            for p in noise_patterns:
                text = p.sub('', text)

            # 按照句号、分号切分，使其接近样本中的“短事实”风格
            segments = re.split(r'[。；;]', text)
            
            for s in segments:
                s = s.strip()
                # 过滤掉太短的无意义片段
                if len(s) < 12: continue
                
                # 去重并写入
                if s not in unique_sentences:
                    out.write(s + '。\n')
                    unique_sentences.add(s)

    print(f"数据精炼完成！")
    print(f"保留高质量事实语料: {len(unique_sentences)} 条")
    print(f"输出文件: {output_path}")

if __name__ == "__main__":
    base_dir = r"c:\Users\Administrator\Desktop\ebuy\back"
    src = os.path.join(base_dir, "merged_doccano_dataset.txt")
    dst = os.path.join(base_dir, "doccano_refined_final.txt")
    
    refine_for_doccano(src, dst)
