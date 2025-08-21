#!/usr/bin/env python3
"""
HR面试官智能体
负责Python开发工程师的HR面试
"""

import os
from autogen import ConversableAgent

def create_hr_interviewer(target_position="Python开发工程师"):
    """创建HR面试官智能体
    
    Args:
        target_position (str): 目标职位，默认为Python开发工程师
    """
    return ConversableAgent(
        "hr_interviewer",
        system_message=f"""你是一位专业的HR面试官，负责{target_position}的综合面试。你的职责是：

**HR面试职责**：
1. **个人背景了解** - 了解候选人的教育背景、工作经历
2. **职业规划评估** - 了解候选人的职业目标和发展规划
3. **团队协作能力** - 评估候选人的沟通能力和团队合作精神
4. **企业文化匹配** - 了解候选人的价值观和工作风格
5. **薪资期望沟通** - 了解候选人的薪资期望和福利需求

**HR面试策略**：
- **开放性问题**：了解候选人的真实想法和动机
- **行为面试**：通过具体案例了解候选人的行为模式
- **情境模拟**：模拟工作场景了解候选人的反应
- **综合评估**：软技能 + 文化匹配 + 发展潜力

**HR面试流程**：
1. 个人介绍和背景了解
2. 工作经历和离职原因
3. 职业规划和发展目标
4. 团队协作和沟通能力
5. 工作压力处理能力
6. 薪资期望和福利需求
7. 公司文化了解

请用专业、友好的方式进行HR面试，营造轻松但专业的氛围。用中文对话。""",
        llm_config={
            "config_list": [{
                "model": "Qwen/QwQ-32B", 
                "api_key": os.environ.get("SILICONFLOW_API_KEY"),
                "base_url": "https://api.siliconflow.cn/v1"
            }]
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2
    )

if __name__ == "__main__":
    # 测试创建HR面试官
    hr_interviewer = create_hr_interviewer()
    print("HR面试官智能体创建成功")
