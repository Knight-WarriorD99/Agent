#!/usr/bin/env python3
"""
信息提取智能体
负责从面试对话中提取候选人信息
"""

import os
from autogen import ConversableAgent

def create_info_extractor():
    """创建信息提取智能体"""
    return ConversableAgent(
        "info_extractor",
        system_message="""你是一位专业的信息提取专家，负责从面试对话中提取候选人的基本信息。

请从面试对话中提取以下信息：
1. 候选人姓名
2. 年龄
3. 教育背景
4. 工作经验年限
5. 当前职位
6. 应聘职位
7. 技术技能列表
8. 主要项目经验
9. 职业规划
10. 薪资期望

如果某项信息在对话中没有明确提到，请标记为"未知"。

**重要要求**：
请严格按照以下JSON格式返回提取的信息：

{
    "name": "候选人姓名",
    "age": "年龄",
    "education": "教育背景",
    "experience_years": "工作经验年限",
    "current_position": "当前职位",
    "target_position": "应聘职位",
    "technical_skills": ["技能1", "技能2", "技能3"],
    "key_projects": [
        {
            "name": "项目名称",
            "duration": "项目时长",
            "tech_stack": "技术栈",
            "responsibilities": "职责描述",
            "achievements": "项目成果"
        }
    ],
    "career_goals": "职业规划",
    "salary_expectation": "薪资期望"
}

请确保返回的是有效的JSON格式，不要包含其他文字说明。""",
        llm_config={
            "config_list": [{
                "model": "Qwen/QwQ-32B", 
                "api_key": os.environ.get("SILICONFLOW_API_KEY"),
                "base_url": "https://api.siliconflow.cn/v1"
            }]
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1
    )

if __name__ == "__main__":
    # 测试创建信息提取智能体
    info_extractor = create_info_extractor()
    print("信息提取智能体创建成功")
