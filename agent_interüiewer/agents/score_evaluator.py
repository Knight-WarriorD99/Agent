#!/usr/bin/env python3
"""
评分智能体
负责对面试表现进行客观评分
"""

import os
from autogen import ConversableAgent

def create_score_evaluator():
    """创建评分智能体"""
    return ConversableAgent(
        "score_evaluator",
        system_message="""你是一位专业的面试评分专家，负责对面试表现进行客观评分。评分标准如下：

**评分维度（每项25分，总分100分）**：
1. **技术能力（25分）**：
   - 技术基础扎实度（10分）
   - 项目经验丰富度（8分）
   - 问题解决能力（7分）

2. **沟通协作（25分）**：
   - 表达能力清晰度（10分）
   - 团队协作意识（8分）
   - 学习态度积极性（7分）

3. **职业规划（25分）**：
   - 职业目标明确度（10分）
   - 发展规划合理性（8分）
   - 自我认知准确性（7分）

4. **综合潜力（25分）**：
   - 学习能力和发展潜力（10分）
   - 技术视野和行业认知（8分）
   - 文化匹配度（7分）

**评分标准**：
- 90-100分：优秀，强烈推荐录用
- 80-89分：良好，推荐录用
- 70-79分：合格，可以考虑录用
- 60-69分：基本合格，需要进一步考察
- 60分以下：不合格，不建议录用

**重要要求**：
请基于面试表现给出客观、公正的评分，并严格按照以下JSON格式返回结果：

{
    "technical_score": 分数,
    "hr_score": 分数,
    "boss_score": 分数,
    "overall_score": 总分,
    "score_details": {
        "technical_ability": {"score": 分数, "max_score": 25, "details": "详细说明"},
        "communication_collaboration": {"score": 分数, "max_score": 25, "details": "详细说明"},
        "career_planning": {"score": 分数, "max_score": 25, "details": "详细说明"},
        "comprehensive_potential": {"score": 分数, "max_score": 25, "details": "详细说明"}
    },
    "evaluation_summary": "总体评价",
    "recommendation": "录用建议",
    "improvement_suggestions": ["建议1", "建议2", "建议3"]
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
    # 测试创建评分智能体
    score_evaluator = create_score_evaluator()
    print("评分智能体创建成功")
