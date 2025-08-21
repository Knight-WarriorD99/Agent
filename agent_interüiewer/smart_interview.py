#!/usr/bin/env python3
"""
智能面试系统 - 三角色面试
面试官、HR和面试者（用户）的智能面试体验
"""

import os
import asyncio
import json
from datetime import datetime

# 导入分离的智能体
from agents import (
    create_technical_interviewer,
    create_hr_interviewer,
    create_boss_interviewer,
    create_candidate_agent,
    create_score_evaluator,
    create_info_extractor,
    generate_offer_letter,
    should_generate_offer
)

# 加载环境变量（请在运行环境或 .env 中配置 API 密钥）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 从环境变量读取 API Key（不要在源码中硬编码密钥）
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not SILICONFLOW_API_KEY:
    print("警告: 未检测到 SILICONFLOW_API_KEY，请在环境变量或 .env 中配置")
if not OPENAI_API_KEY:
    print("警告: 未检测到 OPENAI_API_KEY，请在环境变量或 .env 中配置")

class ThreeRoleInterviewSystem:
    """三角色面试系统"""
    
    def __init__(self):
        self.interviewer = None  # 技术面试官
        self.hr = None          # HR面试官
        self.user = None        # 用户（面试者）
        self.boss = None        # Boss面试官
        self.technical_interview_result = None  # 技术面试结果
        self.hr_interview_result = None         # HR面试结果
        self.boss_interview_result = None       # Boss面试结果
        self.interview_scores = {               # 面试评分
            "technical_score": 0,
            "hr_score": 0,
            "boss_score": 0,
            "overall_score": 0
        }
        self.offer_letter = None                # Offer通知信
    
    async def conduct_technical_interview(self):
        """进行技术面试"""
        print("\n第一阶段：技术面试")
        print("=" * 50)
        print("面试官：技术面试官")
        print("内容：技术能力、项目经验、问题解决能力")
        print("=" * 50)
        
        try:
            # 技术面试官发起对话
            result = self.interviewer.initiate_chat(
                self.user,
                message="你好！我是今天的技术面试官，很高兴见到你。我们接下来会进行技术面试，主要了解你的技术背景、项目经验，以及解决技术问题的能力。首先，请你简单介绍一下自己的技术背景，包括你掌握的主要技术栈、最有代表性的一个项目，以及你在技术学习方面的规划。请放松，我们就像技术交流一样聊聊。",
                max_turns=6
            )
            
            # 保存技术面试结果
            self.technical_interview_result = result
            
            print("\n技术面试完成")
            
        except Exception as e:
            print(f"❌ 技术面试出错: {str(e)}")
    
    async def conduct_hr_interview(self):
        """进行HR面试"""
        print("\n第二阶段：HR面试")
        print("=" * 50)
        print("面试官：HR面试官")
        print("内容：个人背景、职业规划、团队协作、薪资期望")
        print("=" * 50)
        
        try:
            # HR面试官发起对话
            result = self.hr.initiate_chat(
                self.user,
                message="你好！我是今天的HR面试官，很高兴见到你。刚才的技术面试已经完成，现在我们来进行HR面试，主要了解你的个人背景、职业规划，以及对我们公司的了解。首先，请你介绍一下你的教育背景和工作经历、职业规划和发展目标，以及你对我们公司和这个职位的了解。请放松，我们聊聊你的职业发展。",
                max_turns=6
            )
            
            # 保存HR面试结果
            self.hr_interview_result = result
            
            print("\nHR面试完成")
            
        except Exception as e:
            print(f"❌ HR面试出错: {str(e)}")
    
    async def conduct_boss_interview(self):
        """进行Boss面试"""
        print("\n第三阶段：Boss面试")
        print("=" * 50)
        print("面试官：技术总监/CTO")
        print("内容：综合评估、战略匹配、发展潜力、最终决策")
        print("=" * 50)
        
        try:
            # 构建基于前面面试结果的开场白
            boss_message = "你好！我是公司的技术总监，很高兴见到你。"
            
            # 基于技术面试结果添加针对性内容
            if self.technical_interview_result:
                boss_message += "刚才的技术面试我已经了解了你的技术背景和项目经验。"
            
            # 基于HR面试结果添加针对性内容  
            if self.hr_interview_result:
                boss_message += "HR面试也让我了解了你的职业规划和个人发展目标。"
            
            boss_message += """现在我想和你聊聊技术战略和团队发展方面的话题。基于你刚才的表现，我想了解：

1. 你对技术发展趋势的看法，特别是与我们公司技术栈相关的领域
2. 在技术团队中，你倾向于什么样的协作方式
3. 你的长期技术发展规划是什么
4. 你对加入我们技术团队有什么想法和期望
5. 基于你刚才的表现，你认为自己最大的技术优势是什么，还有哪些方面需要提升

请放松，我们就像技术同行一样交流。"""

            # Boss面试官发起对话
            result = self.boss.initiate_chat(
                self.user,
                message=boss_message,
                max_turns=4
            )
            
            # 保存Boss面试结果
            self.boss_interview_result = result
            
            print("\nBoss面试完成")
            
        except Exception as e:
            print(f"❌ Boss面试出错: {str(e)}")
    
    async def generate_interview_scores(self):
        """生成面试评分（基于Boss智能体的评估）"""
        try:
            print("\n正在生成面试评分...")
            
            # 创建评分智能体
            score_agent = create_score_evaluator()
            
            # 构建对话内容摘要
            conversation_summary = ""
            
            # 添加技术面试内容
            if self.technical_interview_result:
                conversation_summary += "技术面试内容：已了解候选人的技术背景和项目经验\n"
            
            # 添加HR面试内容
            if self.hr_interview_result:
                conversation_summary += "HR面试内容：已了解候选人的个人背景和职业规划\n"
            
            # 添加Boss面试内容
            if self.boss_interview_result:
                conversation_summary += "Boss面试内容：已了解候选人的综合能力和发展潜力\n"
            
            # 构建评分评估内容
            evaluation_content = f"""
基于三轮面试的表现，请对候选人进行评分：

**面试对话内容摘要**：
{conversation_summary}

**技术面试表现**：{self.technical_interview_result.summary if self.technical_interview_result else "技术面试已完成"}
**HR面试表现**：{self.hr_interview_result.summary if self.hr_interview_result else "HR面试已完成"}
**Boss面试表现**：{self.boss_interview_result.summary if self.boss_interview_result else "Boss面试已完成"}

请基于以上面试表现，按照评分标准给出详细评分，包括：
1. 技术能力评分（25分）
2. 沟通协作评分（25分）
3. 职业规划评分（25分）
4. 综合潜力评分（25分）
5. 总分（100分）
6. 评分理由和建议

请以JSON格式返回评分结果，格式如下：
{{
    "technical_score": 分数,
    "hr_score": 分数,
    "boss_score": 分数,
    "overall_score": 总分,
    "score_details": {{
        "technical_ability": {{"score": 分数, "max_score": 25, "details": "详细说明"}},
        "communication_collaboration": {{"score": 分数, "max_score": 25, "details": "详细说明"}},
        "career_planning": {{"score": 分数, "max_score": 25, "details": "详细说明"}},
        "comprehensive_potential": {{"score": 分数, "max_score": 25, "details": "详细说明"}}
    }},
    "evaluation_summary": "总体评价",
    "recommendation": "录用建议",
    "improvement_suggestions": ["建议1", "建议2", "建议3"]
}}
"""
            
            # 获取评分结果
            score_result = score_agent.generate_reply(
                messages=[{"role": "user", "content": evaluation_content}]
            )
            
            # 尝试解析评分结果
            try:
                import json
                # 提取JSON内容（可能包含在回复文本中）
                response_text = score_result.content if hasattr(score_result, 'content') else str(score_result)
                
                # 尝试找到JSON部分
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    parsed_scores = json.loads(json_str)
                    
                    # 验证评分格式
                    required_keys = ['technical_score', 'hr_score', 'boss_score', 'overall_score', 
                                   'score_details', 'evaluation_summary', 'recommendation', 'improvement_suggestions']
                    
                    if all(key in parsed_scores for key in required_keys):
                        self.interview_scores = parsed_scores
                        print(f"✅ 成功解析评分结果：总分 {self.interview_scores['overall_score']}/100")
                    else:
                        raise ValueError("评分结果格式不完整")
                else:
                    raise ValueError("未找到有效的JSON格式")
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"⚠️ 解析评分结果失败: {e}")
                print("使用默认评分...")
                
                # 使用默认评分
                self.interview_scores = {
                    "technical_score": 75,
                    "hr_score": 75,
                    "boss_score": 75,
                    "overall_score": 75,
                    "score_details": {
                        "technical_ability": {
                            "score": 18,
                            "max_score": 25,
                            "details": "评分解析失败，使用默认评分"
                        },
                        "communication_collaboration": {
                            "score": 18,
                            "max_score": 25,
                            "details": "评分解析失败，使用默认评分"
                        },
                        "career_planning": {
                            "score": 18,
                            "max_score": 25,
                            "details": "评分解析失败，使用默认评分"
                        },
                        "comprehensive_potential": {
                            "score": 18,
                            "max_score": 25,
                            "details": "评分解析失败，使用默认评分"
                        }
                    },
                    "evaluation_summary": "评分解析失败，需要人工评估",
                    "recommendation": "需要进一步评估",
                    "improvement_suggestions": ["建议重新进行评分", "检查对话内容质量"]
                }
            
            print(f"面试评分完成：总分 {self.interview_scores['overall_score']}/100")
            
        except Exception as e:
            print(f"❌ 评分生成失败: {str(e)}")
            # 设置默认评分
            self.interview_scores = {
                "technical_score": 75,
                "hr_score": 75,
                "boss_score": 75,
                "overall_score": 75,
                "score_details": {},
                "evaluation_summary": "评分生成失败，使用默认评分",
                "recommendation": "需要进一步评估",
                "improvement_suggestions": []
            }
    
    async def extract_candidate_info(self):
        """从面试对话中提取候选人信息"""
        try:
            # 创建信息提取智能体
            info_extractor = create_info_extractor()
            
            # 构建对话内容摘要
            conversation_summary = ""
            
            # 添加技术面试内容
            if self.technical_interview_result:
                conversation_summary += "技术面试内容：已了解候选人的技术背景和项目经验\n"
            
            # 添加HR面试内容
            if self.hr_interview_result:
                conversation_summary += "HR面试内容：已了解候选人的个人背景和职业规划\n"
            
            # 添加Boss面试内容
            if self.boss_interview_result:
                conversation_summary += "Boss面试内容：已了解候选人的综合能力和发展潜力\n"
            
            # 获取候选人信息
            candidate_info_result = info_extractor.generate_reply(
                messages=[{"role": "user", "content": f"请从以下面试对话中提取候选人信息：\n{conversation_summary}"}]
            )
            
            # 尝试解析候选人信息
            try:
                import json
                # 提取JSON内容
                response_text = candidate_info_result.content if hasattr(candidate_info_result, 'content') else str(candidate_info_result)
                
                # 尝试找到JSON部分
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    parsed_info = json.loads(json_str)
                    
                    # 验证信息格式
                    required_keys = ['name', 'age', 'education', 'experience_years', 'current_position', 
                                   'target_position', 'technical_skills', 'key_projects', 'career_goals', 'salary_expectation']
                    
                    if all(key in parsed_info for key in required_keys):
                        # 检查提取的名字是否有效，避免LLM幻觉
                        extracted_name = parsed_info.get('name')
                        
                        # 保存原始重要信息，避免被覆盖
                        original_position = self.candidate_info.get('target_position', '')
                        original_skills = self.candidate_info.get('technical_skills', [])
                        original_projects = self.candidate_info.get('key_projects', [])
                        
                        if extracted_name and extracted_name != "未知" and extracted_name != "候选人":
                            # 更新候选人信息，但保留原始重要信息
                            temp_parsed_info = parsed_info.copy()
                            temp_parsed_info.pop('name', None)  # 移除提取的名字
                            temp_parsed_info.pop('target_position', None)  # 移除提取的职位
                            temp_parsed_info.pop('technical_skills', None)  # 移除提取的技能
                            temp_parsed_info.pop('key_projects', None)  # 移除提取的项目
                            self.candidate_info.update(temp_parsed_info)
                            print(f"✅ 成功提取候选人信息（保留原始重要信息：{self.candidate_info.get('name', '未知')} - {original_position}）")
                        else:
                            # 提取的名字无效，只更新其他信息，保留原始重要信息
                            temp_parsed_info = parsed_info.copy()
                            temp_parsed_info.pop('name', None)
                            temp_parsed_info.pop('target_position', None)  # 移除提取的职位
                            temp_parsed_info.pop('technical_skills', None)  # 移除提取的技能
                            temp_parsed_info.pop('key_projects', None)  # 移除提取的项目
                            self.candidate_info.update(temp_parsed_info)
                            print(f"⚠️ 提取的候选人名字无效或未知，保留原始重要信息: {self.candidate_info.get('name', '未知')} - {original_position}")
                        
                        # 确保重要信息不被覆盖
                        if original_position and original_position != "未知":
                            self.candidate_info['target_position'] = original_position
                        if original_skills:
                            self.candidate_info['technical_skills'] = original_skills
                        if original_projects:
                            self.candidate_info['key_projects'] = original_projects
                    else:
                        raise ValueError("候选人信息格式不完整")
                else:
                    raise ValueError("未找到有效的JSON格式")
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"⚠️ 解析候选人信息失败: {e}")
                print("保留原始候选人信息...")
            
            # 智能职位推断逻辑
            candidate_skills = self.candidate_info.get("technical_skills", [])
            candidate_projects = self.candidate_info.get("key_projects", [])
            
            # 保存原始职位信息
            original_position = self.candidate_info.get('target_position', '')
            
            # 如果已有明确的职位信息且不是"未知"，则保留
            if original_position and original_position != "未知":
                print(f"✅ 保留原始职位信息: {original_position}")
                # 确保职位信息不被覆盖
                self.candidate_info['target_position'] = original_position
            else:
                # 只有在确实没有职位信息时才进行智能推断
                inferred_position = self._infer_position_from_skills_and_projects(candidate_skills, candidate_projects)
                self.candidate_info['target_position'] = inferred_position
                print(f"✅ 智能推断职位: {inferred_position}")
            
            print("候选人信息提取完成")
            
        except Exception as e:
            print(f"❌ 候选人信息提取失败: {str(e)}")
            print("保留原始候选人信息...")
    
    def _infer_position_from_skills_and_projects(self, skills, projects):
        """根据技能和项目经验智能推断职位
        
        Args:
            skills (list): 技能列表
            projects (list): 项目经验列表
            
        Returns:
            str: 推断的职位名称
        """
        # 定义技能分类和权重
        skill_categories = {
            "ai_ml": {
                "keywords": ["大模型", "LLM", "LoRA", "微调", "深度学习", "机器学习", "AI", "人工智能", "NLP", "自然语言处理", "计算机视觉", "推荐算法", "向量数据库", "FAISS", "Milvus", "LangChain", "RAG", "Prompt Engineering", "Transformer", "BERT", "GPT", "强化学习", "知识图谱"],
                "positions": ["大模型算法工程师", "机器学习工程师", "AI工程师", "算法工程师", "NLP工程师"],
                "weight": 1.5
            },
            "data_science": {
                "keywords": ["数据分析", "数据挖掘", "数据可视化", "统计建模", "数据科学", "BI", "Tableau", "PowerBI", "数据建模"],
                "positions": ["数据科学家", "数据分析师", "数据工程师"],
                "weight": 1.3
            },
            "backend_dev": {
                "keywords": ["Django", "Flask", "FastAPI", "MySQL", "PostgreSQL", "Redis", "Docker", "微服务", "高并发", "API", "后端", "Spring Boot", "Node.js", "Go", "微服务架构", "分布式系统", "Saga", "TCC", "Seata"],
                "positions": ["Python开发工程师", "后端开发工程师", "云原生后端工程师", "系统工程师"],
                "weight": 1.0
            },
            "frontend_dev": {
                "keywords": ["React", "Vue", "Angular", "JavaScript", "TypeScript", "前端", "UI/UX", "Web开发", "移动端", "小程序", "HTML", "CSS"],
                "positions": ["前端开发工程师", "UI/UX工程师", "全栈开发工程师"],
                "weight": 0.8
            },
            "data_engineering": {
                "keywords": ["数据工程", "ETL", "数据仓库", "Spark", "Hadoop", "Kafka", "数据湖", "数据管道", "数据治理", "数据平台"],
                "positions": ["数据工程师", "数据平台工程师", "大数据工程师"],
                "weight": 1.2
            },
            "cloud_devops": {
                "keywords": ["Kubernetes", "AWS", "Azure", "GCP", "云原生", "DevOps", "CI/CD", "Jenkins", "GitLab", "监控", "日志", "容器化", "阿里云", "腾讯云"],
                "positions": ["DevOps工程师", "云原生工程师", "运维工程师"],
                "weight": 1.1
            },
            "mobile_dev": {
                "keywords": ["Android", "iOS", "移动开发", "React Native", "Flutter", "移动端"],
                "positions": ["移动开发工程师", "Android开发工程师", "iOS开发工程师"],
                "weight": 0.9
            }
        }
        
        # 计算每个类别的得分
        category_scores = {}
        for category, config in skill_categories.items():
            score = 0
            for skill in skills:
                for keyword in config["keywords"]:
                    if keyword in skill:
                        score += 1
                        break  # 每个技能只计算一次
            
            # 考虑项目经验
            for project in projects:
                for keyword in config["keywords"]:
                    if keyword in project:
                        score += 0.5  # 项目经验权重较低
                        break
            
            category_scores[category] = score * config["weight"]
        
        # 找出得分最高的类别
        if category_scores:
            # 打印调试信息
            print("=== 职位推断调试信息 ===")
            for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"{category}: {score}")
            
            top_category = max(category_scores.items(), key=lambda x: x[1])
            if top_category[1] > 0:
                # 根据得分选择具体职位
                category_config = skill_categories[top_category[0]]
                positions = category_config["positions"]
                
                # 特殊处理：如果候选人明确有大模型相关技能和项目，优先考虑AI/ML职位
                ai_ml_indicators = [
                    any("大模型" in skill for skill in skills),
                    any("LLM" in skill for skill in skills),
                    any("LoRA" in skill for skill in skills),
                    any("大模型" in project for project in projects),
                    any("LLM" in project for project in projects),
                    any("LoRA" in project for project in projects)
                ]
                
                if any(ai_ml_indicators) and top_category[0] in ["ai_ml", "backend_dev"]:
                    print("检测到大模型相关技能/项目，优先考虑AI/ML职位")
                    if any("大模型" in skill or "LLM" in skill for skill in skills):
                        return "大模型算法工程师"
                    elif any("机器学习" in skill or "深度学习" in skill for skill in skills):
                        return "机器学习工程师"
                    else:
                        return "AI工程师"
                
                # 根据技能特点选择最合适的职位
                if top_category[0] == "ai_ml":
                    # AI/ML类别，进一步细分
                    if any("大模型" in skill or "LLM" in skill for skill in skills):
                        return "大模型算法工程师"
                    elif any("机器学习" in skill or "深度学习" in skill for skill in skills):
                        return "机器学习工程师"
                    else:
                        return "AI工程师"
                elif top_category[0] == "backend_dev":
                    # 后端开发类别
                    if any("云原生" in skill or "微服务" in skill for skill in skills):
                        return "云原生后端工程师"
                    else:
                        return "Python开发工程师"
                else:
                    # 其他类别返回第一个职位
                    return positions[0]
        
        # 如果没有匹配到任何类别，返回默认职位
        return "Python开发工程师"
    
    async def generate_offer_if_qualified(self):
        """如果候选人分数>=60，生成offer通知信"""
        try:
            overall_score = self.interview_scores.get("overall_score", 0)
            
            if not should_generate_offer(overall_score):
                print(f"\n候选人总分{overall_score}分，未达到发放offer标准（>=60分）")
                return
            
            print(f"\n候选人总分{overall_score}分，达到发放offer标准，正在生成offer通知信...")
            
            # 构建面试数据
            interview_data = {
                "interview_scores": self.interview_scores,
                "candidate_profile": self.candidate_info
            }
            
            # 生成offer通知信
            self.offer_letter = generate_offer_letter(interview_data)
            
            print("✅ Offer通知信生成完成！")
            print("\n" + "=" * 80)
            print("OFFER通知信")
            print("=" * 80)
            print(self.offer_letter)
            print("=" * 80)
            
            # 保存offer到文件
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 获取候选人名字
            candidate_name = self.candidate_info.get('name', f"候选人_{current_time}")
            
            # 创建候选人文件夹（如果不存在）
            candidate_folder = f"data/interview_results/60plus/{candidate_name}"
            if not os.path.exists(candidate_folder):
                os.makedirs(candidate_folder)
            
            offer_filename = f"{candidate_folder}/offer_letter_{current_time}.txt"
            
            with open(offer_filename, 'w', encoding='utf-8') as f:
                f.write(self.offer_letter)
            
            print(f"\nOffer通知信已保存到: {offer_filename}")
            
        except Exception as e:
            print(f"❌ 生成offer通知信失败: {str(e)}")
    
    async def generate_interview_summary(self):
        """生成面试总结"""
        print("\n面试总结报告")
        print("=" * 60)
        print("三轮面试已完成")
        
        # 显示评分结果
        print(f"\n📊 面试评分结果：")
        print(f"技术面试：{self.interview_scores['technical_score']}/100")
        print(f"HR面试：{self.interview_scores['hr_score']}/100")
        print(f"Boss面试：{self.interview_scores['boss_score']}/100")
        print(f"总分：{self.interview_scores['overall_score']}/100")
        print(f"最终建议：{self.interview_scores.get('recommendation', '需要进一步评估')}")
        
        print("\n面试内容回顾：")
        print("技术面试：")
        print("  - 技术能力评估")
        print("  - 项目经验探讨")
        print("  - 问题解决能力测试")
        print("  - 技术发展趋势讨论")
        
        print("\nHR面试：")
        print("  - 个人背景了解")
        print("  - 职业规划评估")
        print("  - 团队协作能力")
        print("  - 企业文化匹配")
        print("  - 薪资期望沟通")
        
        print("\nBoss面试：")
        print("  - 综合能力评估")
        print("  - 技术战略匹配")
        print("  - 团队融入能力")
        print("  - 发展潜力评估")
        print("  - 最终录用决策")
        
        print("\n后续建议：")
        print("  - 等待面试结果通知")
        print("  - 可继续使用career_agent工具进行技能评估")
        print("  - 制定个人发展计划")
    
    async def save_interview_results(self):
        """保存面试结果到JSON文件"""
        try:
            # 获取当前时间
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 提取面试对话内容
            technical_conversation = []
            hr_conversation = []
            boss_conversation = []
            
            # 提取技术面试对话内容
            if self.technical_interview_result:
                try:
                    # 尝试从对话结果中提取消息
                    if hasattr(self.technical_interview_result, 'messages'):
                        for msg in self.technical_interview_result.messages:
                            technical_conversation.append({
                                "role": msg.get("role", "unknown"),
                                "content": msg.get("content", ""),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    elif hasattr(self.technical_interview_result, 'chat_history'):
                        for msg in self.technical_interview_result.chat_history:
                            technical_conversation.append({
                                "role": getattr(msg, 'role', 'unknown'),
                                "content": getattr(msg, 'content', ''),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    else:
                        # 如果无法提取具体对话，至少保存面试完成信息
                        technical_conversation.append({
                            "role": "system",
                            "content": "技术面试已完成，对话内容已记录",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"提取技术面试对话失败: {e}")
                    technical_conversation.append({
                        "role": "system",
                        "content": "技术面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # 提取HR面试对话内容
            if self.hr_interview_result:
                try:
                    if hasattr(self.hr_interview_result, 'messages'):
                        for msg in self.hr_interview_result.messages:
                            hr_conversation.append({
                                "role": msg.get("role", "unknown"),
                                "content": msg.get("content", ""),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    elif hasattr(self.hr_interview_result, 'chat_history'):
                        for msg in self.hr_interview_result.chat_history:
                            hr_conversation.append({
                                "role": getattr(msg, 'role', 'unknown'),
                                "content": getattr(msg, 'content', ''),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    else:
                        hr_conversation.append({
                            "role": "system",
                            "content": "HR面试已完成，对话内容已记录",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"提取HR面试对话失败: {e}")
                    hr_conversation.append({
                        "role": "system",
                        "content": "HR面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # 提取Boss面试对话内容
            if self.boss_interview_result:
                try:
                    if hasattr(self.boss_interview_result, 'messages'):
                        for msg in self.boss_interview_result.messages:
                            boss_conversation.append({
                                "role": msg.get("role", "unknown"),
                                "content": msg.get("content", ""),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    elif hasattr(self.boss_interview_result, 'chat_history'):
                        for msg in self.boss_interview_result.chat_history:
                            boss_conversation.append({
                                "role": getattr(msg, 'role', 'unknown'),
                                "content": getattr(msg, 'content', ''),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                    else:
                        boss_conversation.append({
                            "role": "system",
                            "content": "Boss面试已完成，对话内容已记录",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"提取Boss面试对话失败: {e}")
                    boss_conversation.append({
                        "role": "system",
                        "content": "Boss面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # 创建面试结果数据
            interview_results = {
                "interview_info": {
                    "candidate_name": getattr(self, 'candidate_info', {}).get('name', '候选人'),
                    "position": getattr(self, 'candidate_info', {}).get('target_position', '应聘职位'),
                    "interview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "interview_id": f"INT_{current_time}",
                    "total_score": self.interview_scores["overall_score"]
                },
                "interview_scores": self.interview_scores,
                "interview_rounds": {
                    "technical_interview": {
                        "interviewer": "技术面试官",
                        "focus_areas": [
                            "技术能力评估",
                            "项目经验探讨", 
                            "问题解决能力测试",
                            "技术发展趋势讨论"
                        ],
                        "status": "completed",
                        "score": self.interview_scores["technical_score"],
                        "conversation": technical_conversation,
                        "summary": "技术面试已完成，评估了候选人的技术能力、项目经验和问题解决能力"
                    },
                    "hr_interview": {
                        "interviewer": "HR面试官",
                        "focus_areas": [
                            "个人背景了解",
                            "职业规划评估",
                            "团队协作能力",
                            "企业文化匹配",
                            "薪资期望沟通"
                        ],
                        "status": "completed",
                        "score": self.interview_scores["hr_score"],
                        "conversation": hr_conversation,
                        "summary": "HR面试已完成，了解了候选人的个人背景、职业规划和团队协作能力"
                    },
                    "boss_interview": {
                        "interviewer": "技术总监/CTO",
                        "focus_areas": [
                            "综合能力评估",
                            "技术战略匹配",
                            "团队融入能力",
                            "发展潜力评估",
                            "最终录用决策"
                        ],
                        "status": "completed",
                        "score": self.interview_scores["boss_score"],
                        "conversation": boss_conversation,
                        "summary": "Boss面试已完成，基于前两轮面试结果进行综合评估和最终决策"
                    }
                },
                "interview_flow": {
                    "total_rounds": 3,
                    "interview_sequence": [
                        "技术面试 → HR面试 → Boss面试"
                    ],
                    "boss_evaluation_basis": [
                        "基于技术面试的技术能力评估",
                        "基于HR面试的沟通协作能力评估", 
                        "综合两轮面试的学习能力和发展潜力评估"
                    ]
                },
                "candidate_profile": getattr(self, 'candidate_info', {
                    "name": "候选人",
                    "age": "未知",
                    "education": "未知",
                    "experience_years": "未知",
                    "current_position": "未知",
                    "target_position": "未知",
                    "technical_skills": [],
                    "key_projects": [],
                    "career_goals": "未知",
                    "salary_expectation": "未知"
                }),
                "interview_summary": {
                    "total_rounds": 3,
                    "interview_duration": "约30-45分钟",
                    "overall_assessment": self.interview_scores.get("evaluation_summary", "候选人整体表现良好"),
                    "boss_final_evaluation": "基于前两轮面试结果，Boss进行了综合评估和最终决策",
                    "final_recommendation": self.interview_scores.get("recommendation", "需要进一步评估"),
                    "improvement_suggestions": self.interview_scores.get("improvement_suggestions", []),
                    "recommendations": [
                        "等待面试结果通知",
                        "可继续使用career_agent工具进行技能评估",
                        "制定个人发展计划"
                    ]
                }
            }
            
            # 获取候选人名字
            candidate_name = self.candidate_info.get('name', f"候选人_{current_time}")
            
            # 根据分数确定保存文件夹
            overall_score = self.interview_scores["overall_score"]
            if overall_score >= 60:
                base_folder = "data/interview_results/60plus"
            else:
                base_folder = "data/interview_results/below60"
            
            # 创建以候选人名字命名的文件夹
            candidate_folder = f"{base_folder}/{candidate_name}"
            if not os.path.exists(candidate_folder):
                os.makedirs(candidate_folder)
                print(f"创建候选人文件夹: {candidate_folder}")
            
            # 保存到JSON文件
            filename = f"{candidate_folder}/interview_results_{current_time}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(interview_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n面试结果已保存到: {filename}")
            print(f"总分: {overall_score}/100")
            print(f"保存位置: {candidate_folder}/")
            print("文件包含完整的面试对话内容和评分详情")
            
        except Exception as e:
            print(f"❌ 保存面试结果失败: {str(e)}")
    
    async def conduct_full_interview(self):
        """进行完整面试流程"""
        print("智能面试系统 - 三角色面试")
        print("=" * 60)
        print("面试流程：技术面试 → HR面试 → Boss面试")
        print("角色：技术面试官 + HR面试官 + Boss面试官 + 面试者")
        print("=" * 60)
                
        # 从candidate_agent.py动态获取默认候选人信息
        from agents.candidate_agent import get_default_candidate_info, create_candidate_agent
        
        # 获取默认候选人信息
        candidate_info = get_default_candidate_info()
        
        # 获取候选人职位信息
        target_position = candidate_info.get('target_position', 'Python开发工程师')
        
        # 创建智能体
        self.interviewer = create_technical_interviewer(target_position)
        self.hr = create_hr_interviewer(target_position)
        self.boss = create_boss_interviewer()
        self.user = create_candidate_agent(candidate_info)
        
        # 保存候选人信息供后续使用
        self.candidate_info = candidate_info
        
        print("\n面试开始...")
        print("注意：现在是AI智能体自动对话演示。")
        print("-" * 60)
        
        try:
            # 第一阶段：技术面试
            await self.conduct_technical_interview()
            
            print("\n" + "=" * 60)
            print("技术面试结束，准备进入HR面试...")
            print("=" * 60)
            
            # 第二阶段：HR面试
            await self.conduct_hr_interview()
            
            print("\n" + "=" * 60)
            print("HR面试结束，准备进入Boss面试...")
            print("=" * 60)
            
            # 第三阶段：Boss面试
            await self.conduct_boss_interview()
            
            # 生成评分
            await self.generate_interview_scores()

            # 提取候选人信息
            await self.extract_candidate_info()
            
            # 生成总结
            await self.generate_interview_summary()
            
            # 保存面试结果
            await self.save_interview_results()
            
            # 生成offer通知信（如果分数>=60）
            await self.generate_offer_if_qualified()
            
        except Exception as e:
            print(f"❌ 面试过程中出现错误: {str(e)}")

async def main():
    """主函数"""
    print("欢迎参加智能面试系统")
    print("=" * 50)
    print("AI智能体自动演示三轮面试：")
    print("1. 技术面试 - 技术面试官 vs 面试者")
    print("2. HR面试 - HR面试官 vs 面试者")
    print("3. Boss面试 - 技术总监 vs 面试者")
    print("\n面试者：AI智能体（模拟真实候选人）")
    print("演示完整的面试对话流程！")
    print("=" * 50)
    
    input("按回车键开始面试...")
    
    interview_system = ThreeRoleInterviewSystem()
    await interview_system.conduct_full_interview()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n面试被中断")
    except Exception as e:
        print(f"\n系统错误: {str(e)}")
        print("请检查API密钥和网络连接")
