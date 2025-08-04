import json
from copy import deepcopy

def volc_chat(input):
    import os
    from volcenginesdkarkruntime import Ark
    client = Ark(api_key="a2f4ef33-06da-4062-a808-f5a2287c54e5")
    completion = client.chat.completions.create(
        # 将 <Model> 替换为 Model ID（或者Endpoint ID）
        model="deepseek-v3-241226", 
        # model="deepseek-r1-distill-qwen-32b-250120",
        messages=[
            # {"role": "system", "content": "你是"},
            {"role": "user", "content": input}
        ]
    )
    return completion.choices[0].message.content


# import pandas as pd
# file1_path = "/root/pku/llm/read_answer/重点客户预期销额-全量.parquet"
# data1 = pd.read_parquet(file1_path)
# data1.rename(columns=lambda x: x.replace(" ", ""), inplace=True)
# print(data1.columns)


# 讨价还价博弈
# 让两个模型进行自由多轮互相对话
def argue():
    history = []
    total_turn = 5
    current_turn = 0
    left_turn = total_turn - current_turn
    guidance_4_1 = '''
    你是玩家甲，另有一个玩家乙与你进行讨论。现在你们要分配一张100%概率的“彩票券”，分配按照以下规则。
    1、分配比例决定了每个玩家赢得奖品的概率.例如，甲如果获得40%的彩票券，就有40%的概率赢得奖品，60%的概率一无所获；而乙则完全相反，有60%的概率赢得奖品，40%的概率一无所获。这样一个分配记作60-40。
    2、甲和乙有4轮对话轮次达成协议。如果在规定时间内未能达成协议，那么所有玩家都将一无所获。因此，只有在双方就彩票券的分配达成了协议，并且该玩家在随后的抽奖中中奖时，玩家才能获得相应的奖品.否则，他将得不到任何奖励。
    3、如果你获得奖品，那么奖品价值为20美元。
    4、在游戏开始后，你们奖品的价值会被告诉对方。
    5、如果双方达成一致，则从甲开始先后仅输出最终的分配策略xx-xx，如果某个回合中先后输出符合格式的策略一致，则该策略为最终分配比例。
    从你开始，给出下一轮次与乙讨价还价的对话语句，限制100词以内。下面是到目前为止的总对话历史。
    '''
    guidance_4_2 = '''
    你是玩家甲，另有一个玩家乙与你进行讨论。现在你们要分配一张100%概率的“彩票券”，分配按照以下规则。
    1、分配比例决定了每个玩家赢得奖品的概率.例如，甲如果获得40%的彩票券，就有40%的概率赢得奖品，60%的概率一无所获；而乙则完全相反，有60%的概率赢得奖品，40%的概率一无所获。这样一个分配记作60-40。
    2、甲和乙有4轮对话轮次达成协议。如果在规定时间内未能达成协议，那么所有玩家都将一无所获。因此，只有在双方就彩票券的分配达成了协议，并且该玩家在随后的抽奖中中奖时，玩家才能获得相应的奖品.否则，他将得不到任何奖励。
    3、如果你获得奖品，那么奖品价值为20美元。
    4、在游戏开始后，你们奖品的价值会被告诉对方。
    5、如果双方达成一致，则从甲开始先后仅输出最终的分配策略xx-xx，如果某个回合中先后输出符合格式的策略一致，则该策略为最终分配比例。
    甲刚刚给出了最新一轮对话中他的发言。请给出本轮次乙与甲讨价还价的对话语句，限制100词以内。
    '''
    for i in range(total_turn):
        prompt1 = guidance_4_1+'''注意：到目前为止一共进行了'''+str(current_turn)+'''轮次，还有'''+str(left_turn)+'''轮次对话机会。'''
        for word in history:
            prompt1 += word
        prompt1 += '''甲：'''
        response1 = volc_chat(prompt1)
        history.append('甲：'+response1)
        prompt2 = guidance_4_2+'''注意：到目前为止一共进行了'''+str(current_turn)+'''轮次，还有'''+str(left_turn)+'''轮次对话机会。'''
        for word in history:
            prompt2 += word
        prompt2 += '''乙：'''
        response2 = volc_chat(prompt2)
        history.append('乙'+response2)
        print(f'{i} finished')  
    with open("/root/pku/yusen/knowledge/argue.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if isinstance(data, dict):
        new_key = f"list{len(data) + 1}"  # 自动生成新的键
        data[new_key] = history
    # 如果 data 是列表（方法 2），直接追加新的列表
    elif isinstance(data, list):
        data.append(history)
    with open("/root/pku/yusen/knowledge/argue.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def guess():
    # 泥泞的孩童
    # N人博弈模板
    # 模型思考过程是否包含在输出中会如何影响到最终的结果：理论上会影响，因为缩短了token预测序列的长度
    guidance_dust = '''
    假设你扮演一个游戏，你和若干个人中有一些人脸上有泥巴。每个人都能看见其他人脸上是否有泥巴。
    现在有一个外人告诉你们，你们这些人中至少有一个人脸上有泥巴。认为这个人是可信的。
    接下来进行若干轮次对话，每一次对话中每个人都回答'知道'或'不知道'： 要求诚实，如果你能够从历史其他人和自己给出的结果以及自己观测到他们脸上情况确定地推断出自己
    脸上是否有泥巴，则输出'知道'，如果推断不出则输出'不知道'。
    现在你观测到的结果如下(0代表有泥巴，1代表没有泥巴，2代表自己，看不到自己有没有)
    '''
    guidance_dust = '''
    假设你扮演一个游戏，你和若干个人中有一些人脸上有泥巴。每个人都能看见其他人脸上是否有泥巴。
    接下来进行若干轮次对话，每一次对话中每个人都回答'知道'或'不知道'： 要求诚实，如果你能够从历史其他人和自己给出的结果以及自己观测到他们脸上情况确定地推断出自己
    脸上是否有泥巴，则输出'知道'，如果推断不出则输出'不知道'。
    现在你观测到的结果如下(0代表有泥巴，1代表没有泥巴，2代表自己，看不到自己有没有)
    '''
    N = 7
    dust = [1,0,0,0,0,0,0]
    history = []
    turns = 5
    for turn in range(turns):
        history_record = ''
        this_turn = []
        for j in range(len(history)):
            history_record += f'turn{j}:str({history[j]})\n'
        for i in range(N):
            obs = deepcopy(dust)
            obs[i] = 2
            prompt = guidance_dust+str(obs)+f''' 
                目前是第{turn}轮次，所有人历史对话为
                '''+history_record+'''
                你的输出应该严格为'知道'或'不知道',要求诚实。不要输出额外的信息。'''
            print(prompt)
            ans = volc_chat(prompt)
            print(ans)
            this_turn.append(ans)
        history.append(this_turn)
        print(f'{turn} finished.')

    with open("/root/pku/yusen/knowledge/dust.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if isinstance(data, dict):
        new_key = f"list{len(data) + 1}"  # 自动生成新的键
        data[new_key] = history
    # 如果 data 是列表（方法 2），直接追加新的列表
    elif isinstance(data, list):
        data.append(history)
    with open("/root/pku/yusen/knowledge/dust.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# 电子邮件博弈
def email_game():
    p = 0.99
    epsilon = 0.01
    guidance_prompt1 = f'''
    你扮演一个二人博弈的角色中的甲，博弈中要尽可能最大化自己的收益。现在你和乙的收益矩阵有两个可能的分布：（对于收益分布(x,y)代表甲获得x，乙获得y—）。
    可能分布一：当你选择行动A时，若乙选择行动A则二人收益分别为（0，0），若乙选择B则收益为(-10,1);当你选择行动B时，若乙选择A则为(1,-10),若乙选择B则为(8,8)
    可能分布二：当你选择行动A时，若乙选择行动A则二人收益分别为（8，8），若乙选择B则收益为(-10,1);当你选择行动B时，若乙选择A则为(1,-10),若乙选择B则为(0,0)
    现在，你和乙都知道可能分布一的概率为{p}，可能分布二的概率为1-{p}。
    在任意一种情况下你都知道真实的分布，而乙则并不知道。
    另外，如果选择了右边矩阵，你会给乙发送一条消息.如果乙收到了消息，他会回复.如果你收到了回复，你会发送第二条消息来确认收到了乙的回复. 以此类推. 每条消息都以{epsilon}的概率独立等可能丢失。这个过程是自动进行的，你不需要做出具体的消息发送输出文本。
    现在，请充分思考后以
    'A':xxx, 'B': xxx
    的格式给出你认为的在这种场景下你的最优贝叶斯博弈策略（概率策略，分别为选择动作A的概率和选择动作B的概率）
    你的输出应严格仅包含上面格式，不要输出额外的内容。
    '''
    guidance_prompt2 = f'''
    你扮演一个二人博弈的角色中的乙，博弈中要尽可能最大化自己的收益。现在你和甲的收益矩阵有两个可能的分布：（对于收益分布(x,y)代表甲获得x，乙获得y）。
    可能分布一：当甲选择行动A时，若你选择行动A则二人收益分别为（0，0），若你选择B则收益为(-10,1);当甲选择行动B时，若你选择A则为(1,-10),若你选择B则为(8,8)
    可能分布二：当甲选择行动A时，若你选择行动A则二人收益分别为（8，8），若你选择B则收益为(-10,1);当甲选择行动B时，若你选择A则为(1,-10),若你选择B则为(0,0)
    现在，你和甲都知道可能分布一的概率为{p}，可能分布二的概率为1-{p}。
    在任意一种情况下甲都知道真实的分布，而你则并不知道。
    另外，如果选择了右边矩阵，甲会给你发送一条消息.如果你收到了消息，你会回复.如果甲收到了回复，他会发送第二条消息来确认收到了你的回复. 以此类推. 每条消息都以{epsilon}的概率独立等可能丢失。这个过程是自动进行的，你不需要做出具体的消息发送输出文本。
    现在，请充分思考后以
    'A':xxx, 'B': xxx
    的格式给出你认为的在这种场景下你的最优贝叶斯博弈策略（概率策略，分别为选择动作A的概率和选择动作B的概率）
    你的输出应严格仅包含上面格式，不要输出额外的内容。
    '''
    action1 = volc_chat(guidance_prompt1)
    action2 = volc_chat(guidance_prompt2)
    history = {'甲':action1, '乙':action2}
    with open("/root/pku/yusen/knowledge/email.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if isinstance(data, dict):
        new_key = f"list{len(data) + 1}"  # 自动生成新的键
        data[new_key] = history
    # 如果 data 是列表（方法 2），直接追加新的列表
    elif isinstance(data, list):
        data.append(history)
    with open("/root/pku/yusen/knowledge/email.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)



# 逻辑全知

# 对比大模型的信念，知识和幻觉

# 正内省公理对大模型是否成立
def znx():
    prompts = ['''
    你是否知道一年后大模型发展会有哪些进展
    ''',
    '''你是否知道2025年3月31日北京的天气''',
    '''你是否知道2023年3月31日北京的天气''',
    '''你是否知道对于不同天气的应对''',
    '''你是否知道最新的具体的关于教学大模型的进展''']
    history = []
    for prompt in prompts:
        ans = volc_chat(prompt)
        history.append({"prompt":prompt, "response":ans})
    with open("/root/pku/yusen/knowledge/znx.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if isinstance(data, dict):
        new_key = f"list{len(data) + 1}"  # 自动生成新的键
        data[new_key] = history
    # 如果 data 是列表（方法 2），直接追加新的列表
    elif isinstance(data, list):
        data.append(history)
    with open("/root/pku/yusen/knowledge/znx.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# 负内省公理
def fnx():
    prompts = ['''
    请自我审视，确认自己是否不知道一年后大模型发展会有哪些进展
    ''',
    '''你是否知道2025年3月31日北京的天气''',
    '''你是否知道自己不知道2025年3月31日北京的天气''',
    '''你是否知道自己不知道2025年3月31日美国拉马拉克县的天气''',
    '''你是否知道2025年3月31日美国拉马拉克县的天气''',
    '''你是否知道Langlands猜想''',
    '''你是否知道自己不明白Langlands猜想这个事实'''
    ]
    history = []
    for prompt in prompts:
        ans = volc_chat(prompt)
        history.append({"prompt":prompt, "response":ans})
    with open("/root/pku/yusen/knowledge/fnx.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    if isinstance(data, dict):
        new_key = f"list{len(data) + 1}"  # 自动生成新的键
        data[new_key] = history
    # 如果 data 是列表（方法 2），直接追加新的列表
    elif isinstance(data, list):
        data.append(history)
    with open("/root/pku/yusen/knowledge/fnx.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

fnx()

