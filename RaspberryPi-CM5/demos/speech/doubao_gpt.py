import ast
from typing import List
from volcenginesdkarkruntime import Ark

API_KEY = '67e1719b-fc92-43b7-979d-3692135428a4'
MODEL_NAME = "doubao-1.5-pro-32k-250115"

#version=2.0

ACTION_ORDER = [
    "Dance",        # 跳舞
    "Pushups",      # 俯卧撑
    "Pee",          # 撒尿
    "Stretch",      # 伸懒腰
    "Pray",         # 祈祷
    "Chickenhead",  # 鸡头
    "Lookforfood",  # 找食物
    "Grabdownwards",# 向下抓取
    "Wave",         # 波浪
    "Beg"           # 乞讨
]

def get_model_response(client: Ark, prompt: str) -> List[int]:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    result = ast.literal_eval(completion.choices[0].message.content)
    print(f"模型返回结果: {result}, 类型: {type(result)}")
    return result

def model_output(content: str) -> str:
    """
    返回自然语言回复（如笑话、对话），不包含动作指令。
    """
    system_prompt = """
    你是一个会说话的机器狗Lulu，用自然语言风趣地回答用户问题。
    回答要求：
    1. 使用简洁的口语化表达，避免复杂术语。
    2. 如果问题涉及机器狗动作（如跳舞、握手），直接回答“我可以表演XX动作哦！”。
    3. 禁止返回任何代码、JSON或列表格式。
    4. 给你的话是语音识别的结果，可能会有识别的错别字等
    5. 当说英文时，可能有部分语音识别成中文，导致英文中穿插着中文，这时候你需要用英文回复
    """
    
    client = Ark(api_key=API_KEY)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
    )
    reply = completion.choices[0].message.content
    
    # 可选：清理全角符号（如替换中文标点为英文标点）
    reply = reply.replace("！", "!").replace("，", ",").replace("…", "...")
    
    return reply