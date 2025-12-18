import logging
import os
import time
from openai import OpenAI

# =======================
# 基础配置
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise RuntimeError("未检测到环境变量 DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# =======================
# 读取关键词
# =======================
def read_keywords(input_file):
    logging.info(f"读取关键词文件: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            keywords = f.read().splitlines()
        logging.info(f"读取到 {len(keywords)} 个关键词")
        return keywords
    except Exception as e:
        logging.error(f"读取关键词文件失败: {e}")
        return []

# =======================
# 写入筛选结果
# =======================
def write_filtered_keywords(output_file, keywords):
    logging.info(f"将筛选后的关键词写入文件: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for kw in keywords:
                f.write(kw + '\n')
        logging.info(f"成功写入 {len(keywords)} 个关键词")
    except Exception as e:
        logging.error(f"写入文件失败: {e}")

# =======================
# 保存 / 读取进度
# =======================
def save_progress(index, progress_file="progress.txt"):
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(str(index))
    logging.info(f"进度已保存，当前索引: {index}")

def read_progress(progress_file="progress.txt"):
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            idx = int(f.read().strip())
        logging.info(f"恢复进度，从索引 {idx} 开始")
        return idx
    return 0

# =======================
# 核心：调用 DeepSeek-R1 API
# =======================
def filter_keywords(keywords, start_index=0):
    filtered = []
    batch_size = 20

    for i in range(start_index, len(keywords), batch_size):
        batch = keywords[i:i + batch_size]

        prompt = f"""
请你对以下关键词进行判断，判断其是否与计算语言学（computational linguistics）相关。

判断规则：
1. 与语言、文本、语音、语义、语法、NLP、语言模型、语料库等相关 → 相关
2. 常见缩写（如 NLP, BERT, POS, NER, ASR, TTS, LSTM, GPT） → 相关
3. 无明确学术含义的字母组合 → 不相关
4. 明显属于其他领域 → 不相关

关键词：
{", ".join(batch)}

请严格按以下格式输出（仅两行）：
相关关键词：xxx, xxx
不相关关键词：xxx, xxx
"""

        logging.info(f"处理关键词 {i+1} - {min(i+batch_size, len(keywords))}")

        try:
            response = client.chat.completions.create(
                model="deepseek-reasoner",   # DeepSeek-R1
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            content = response.choices[0].message.content.strip()
            logging.info(f"模型返回：{content}")

            # ===== 更稳健的解析 =====
            related = []
            for line in content.splitlines():
                if line.startswith("相关关键词"):
                    related = [
                        kw.strip()
                        for kw in line.split("：", 1)[1].split(",")
                        if kw.strip()
                    ]

            filtered.extend(related)
            save_progress(i + batch_size)

            time.sleep(0.5)  # 防止触发限速

        except Exception as e:
            logging.error(f"API 调用失败: {e}")
            break

    return filtered

# =======================
# 主函数
# =======================
def main(input_file, output_file):
    logging.info("程序启动")
    keywords = read_keywords(input_file)
    if not keywords:
        return

    start_index = read_progress()
    filtered = filter_keywords(keywords, start_index)
    write_filtered_keywords(output_file, filtered)
    logging.info("筛选完成")

# =======================
# 运行
# =======================
if __name__ == "__main__":
    input_file = r"E:\study\research\create_gynamic_edge\domain concepts\full_domain_concepts.txt"
    output_file = r"E:\study\research\create_gynamic_edge\domain concepts\filtered_keywords.txt"
    main(input_file, output_file)
