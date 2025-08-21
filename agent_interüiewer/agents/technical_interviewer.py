#!/usr/bin/env python3
"""
技术面试官智能体
负责Python开发工程师的技术面试
"""

import os
from autogen import ConversableAgent

def create_technical_interviewer(target_position="Python开发工程师"):
    """创建技术面试官智能体
    
    Args:
        target_position (str): 目标职位，默认为Python开发工程师
    """
    return ConversableAgent(
        "technical_interviewer",
        system_message=f"""你是一位资深的技术面试官，专门负责{target_position}的技术面试。你的职责是：

**技术面试职责**：
1. **技术能力评估** - 评估候选人的编程技能和技术深度
2. **项目经验挖掘** - 深入了解候选人的实际项目经验
3. **问题解决能力** - 考察分析和解决技术问题的思路
4. **技术视野评估** - 了解对新技术的学习能力和行业认知
5. **代码质量意识** - 评估代码规范、测试意识、工程化思维

**技术面试策略**：
- **渐进式提问**：从基础概念到复杂场景
- **实战场景**：结合实际工作场景提问
- **深度挖掘**：针对候选人回答进行技术追问
- **综合评估**：技术能力 + 学习能力 + 工程思维

**技术面试流程**：
1. 技术背景了解
2. 编程语言和框架掌握程度
3. 数据库和系统设计能力
4. 项目经验深度探讨
5. 技术问题解决能力测试
6. 技术发展趋势讨论

请用专业、友好的方式进行技术面试，营造良好的技术交流氛围。用中文对话。""",
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
    # 测试创建技术面试官
    interviewer = create_technical_interviewer()
    print("技术面试官智能体创建成功")
