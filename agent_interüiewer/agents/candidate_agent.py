#!/usr/bin/env python3
"""
候选人智能体
模拟面试者的回答
"""

import os
from autogen import ConversableAgent

def get_default_candidate_info():
    """获取默认候选人信息"""
    return {
        "name": "林义超",
        "age": "26岁",
        "education": "计算机科学本科",
        "experience_years": "3年",
        "current_position": "算法工程师",
        "target_position": "大模型算法工程师",
        "technical_skills": [
            "Python（熟练）", "JavaScript（基础）", "SQL",
            "Django", "Flask", "FastAPI",
            "MySQL", "PostgreSQL", "Redis",
            "Docker", "Git", "Linux", "Jenkins",
            "阿里云基础使用",
            "Prompt Engineering", "LoRA微调", "分布式训练（DeepSpeed/Megatron-LM）",
            "FAISS/Chroma/Milvus向量库", "Elastic-search", "HNSW",
            "ReAct框架", "工具编排（API/数据库集成）", "记忆机制（短期/长期记忆）",
            "模型量化（INT8/GPTQ）", "LLM推理加速", "微服务架构（Docker）"
        ],
        "key_projects": [
            "电商后端系统（1年）- Django + MySQL，日均处理订单3000+",
            "数据分析API平台（半年）- FastAPI构建RESTful API",
            "大模型算法优化与应用（半年）- LoRA技术微调大模型",
            "智能Agent对话机器人（半年）- LangChain、OpenAI API、RAG技术",
            "LLaMA3 预训练与领域微调（半年）- 使用LLaMA3预训练模型"
        ],
        "career_goals": "希望在技术深度和广度上进一步提升，学习微服务架构、云原生技术，成长为技术专家",
        "salary_expectation": "根据市场行情和公司规模确定"
    }

def create_candidate_agent(candidate_info=None):
    """创建面试者智能体（AI自动回答）
    
    Args:
        candidate_info (dict): 候选人信息字典，包含以下字段：
            - name: 候选人姓名
            - age: 年龄
            - education: 教育背景
            - experience_years: 工作经验年数
            - current_position: 当前职位
            - target_position: 目标职位
            - technical_skills: 技术技能列表
            - key_projects: 关键项目列表
            - career_goals: 职业目标
            - salary_expectation: 薪资期望
    """
    
    # 获取默认候选人信息
    default_info = get_default_candidate_info()
    
    # 合并用户提供的信息和默认信息
    if candidate_info:
        default_info.update(candidate_info)
    
    # 构建技术技能字符串
    skills_text = ""
    for skill in default_info['technical_skills']:
        skills_text += f"- {skill}\n"
    
    # 构建项目经验字符串
    projects_text = ""
    for i, project in enumerate(default_info['key_projects'], 1):
        projects_text += f"{i}. **{project}**\n"
    
    # 构建系统消息
    system_message = f"""你是{default_info['name']}，一位有{default_info['experience_years']}经验的算法工程师，正在参加面试。

**个人背景**：
- 年龄：{default_info['age']}，{default_info['education']}
- 工作经验：{default_info['experience_years']}Python后端开发经验
- 期望职位：{default_info['target_position']}

**技术技能**：
{skills_text}

**项目经验**：
{projects_text}

**面试表现特点**：
- 技术基础扎实，有实际项目经验
- 主动分享技术细节和解决方案
- 对新技术有学习热情
- 诚实回答，不夸大能力
- 展现良好的沟通能力和学习态度
- 对职业发展有明确规划

**职业规划**：{default_info['career_goals']}

请用自然、专业的方式回答面试官的问题，展现出{default_info['experience_years']}经验工程师的技术水平和职业素养。用中文回答，保持自信和诚实。"""

    return ConversableAgent(
        "candidate",
        system_message=system_message,
        llm_config={
            "config_list": [{
                "model": "Qwen/QwQ-32B", 
                "api_key": os.environ.get("SILICONFLOW_API_KEY"),
                "base_url": "https://api.siliconflow.cn/v1"
            }]
        },
        human_input_mode="NEVER",  # AI自动回答
        max_consecutive_auto_reply=2
    )

if __name__ == "__main__":
    # 测试创建候选人智能体
    candidate = create_candidate_agent()
    print("候选人智能体创建成功")
    
    # 测试自定义候选人信息
    custom_info = {
        "name": "张三",
        "age": "28岁",
        "experience_years": "5年",
        "target_position": "高级算法工程师"
    }
    custom_candidate = create_candidate_agent(custom_info)
    print("自定义候选人智能体创建成功")
