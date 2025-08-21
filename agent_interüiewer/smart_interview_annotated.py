#!/usr/bin/env python3  # 指定用 Python3 解释器运行脚本
"""
智能面试系统 - 三角色面试  # 模块文档字符串：标题
面试官、HR和面试者（用户）的智能面试体验  # 模块文档字符串：说明
"""  # 模块文档字符串结束

import os  # 标准库：环境变量、路径操作
import asyncio  # 标准库：异步编程
import json  # 标准库：JSON 序列化/反序列化
from datetime import datetime  # 标准库：时间与格式化

# 导入分离的智能体  # 说明：从 agents 包导入工厂与工具函数
from agents import (  # 从 agents 包批量导入
    create_technical_interviewer,  # 工厂：创建技术面试官智能体
    create_hr_interviewer,  # 工厂：创建 HR 面试官智能体
    create_boss_interviewer,  # 工厂：创建 Boss（技术总监/CTO）面试官智能体
    create_candidate_agent,  # 工厂：创建候选人智能体
    create_score_evaluator,  # 工厂：创建评分智能体
    create_info_extractor,  # 工厂：创建信息抽取智能体
    generate_offer_letter,  # 工具：生成 Offer 通知书
    should_generate_offer  # 工具：根据分数判断是否应生成 Offer
)  # 导入结束

# 加载环境变量（请在运行环境或 .env 中配置 API 密钥）  # 安全：不要在源码中硬编码密钥
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 从环境变量读取 API Key（兼容组件使用）
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not SILICONFLOW_API_KEY:
    print("警告: 未检测到 SILICONFLOW_API_KEY，请在环境变量或 .env 中配置")
if not OPENAI_API_KEY:
    print("警告: 未检测到 OPENAI_API_KEY，请在环境变量或 .env 中配置")

class ThreeRoleInterviewSystem:  # 定义三角色面试系统类
    """三角色面试系统"""  # 类文档字符串
    
    def __init__(self):  # 构造函数
        self.interviewer = None  # 技术面试官
        self.hr = None          # HR面试官
        self.user = None        # 用户（面试者）
        self.boss = None        # Boss面试官
        self.technical_interview_result = None  # 技术面试结果
        self.hr_interview_result = None         # HR面试结果
        self.boss_interview_result = None       # Boss面试结果
        self.interview_scores = {               # 面试评分
            "technical_score": 0,  # 技术分
            "hr_score": 0,  # HR 分
            "boss_score": 0,  # Boss 分
            "overall_score": 0  # 总分
        }
        self.offer_letter = None                # Offer通知信占位
    
    async def conduct_technical_interview(self):  # 异步：进行技术面试
        """进行技术面试"""  # 方法文档
        print("\n第一阶段：技术面试")  # 阶段标题
        print("=" * 50)  # 分隔线
        print("面试官：技术面试官")  # 说明
        print("内容：技术能力、项目经验、问题解决能力")  # 面试重点
        print("=" * 50)  # 分隔线
        
        try:  # 异常保护
            # 技术面试官发起对话  # 调用面试官智能体进行多轮对话
            result = self.interviewer.initiate_chat(  # 发起聊天
                self.user,  # 面试对象：候选人智能体
                message="你好！我是今天的技术面试官，很高兴见到你。我们接下来会进行技术面试，主要了解你的技术背景、项目经验，以及解决技术问题的能力。首先，请你简单介绍一下自己的技术背景，包括你掌握的主要技术栈、最有代表性的一个项目，以及你在技术学习方面的规划。请放松，我们就像技术交流一样聊聊。",  # 开场白
                max_turns=6  # 限制对话轮次
            )
            
            # 保存技术面试结果  # 存储对话结果对象
            self.technical_interview_result = result
            
            print("\n技术面试完成")  # 提示完成
            
        except Exception as e:  # 捕获异常
            print(f"❌ 技术面试出错: {str(e)}")  # 打印错误
    
    async def conduct_hr_interview(self):  # 异步：进行 HR 面试
        """进行HR面试"""  # 方法文档
        print("\n第二阶段：HR面试")  # 标题
        print("=" * 50)  # 分隔线
        print("面试官：HR面试官")  # 说明
        print("内容：个人背景、职业规划、团队协作、薪资期望")  # 面试重点
        print("=" * 50)  # 分隔线
        
        try:  # 异常保护
            # HR面试官发起对话  # 调用 HR 智能体
            result = self.hr.initiate_chat(  # 发起聊天
                self.user,  # 面试对象
                message="你好！我是今天的HR面试官，很高兴见到你。刚才的技术面试已经完成，现在我们来进行HR面试，主要了解你的个人背景、职业规划，以及对我们公司的了解。首先，请你介绍一下你的教育背景和工作经历、职业规划和发展目标，以及你对我们公司和这个职位的了解。请放松，我们聊聊你的职业发展。",  # 开场白
                max_turns=6  # 对话轮次
            )
            
            # 保存HR面试结果  # 存储结果
            self.hr_interview_result = result
            
            print("\nHR面试完成")  # 完成提示
            
        except Exception as e:  # 异常
            print(f"❌ HR面试出错: {str(e)}")  # 错误信息
    
    async def conduct_boss_interview(self):  # 异步：进行 Boss 面试
        """进行Boss面试"""  # 文档
        print("\n第三阶段：Boss面试")  # 标题
        print("=" * 50)  # 分隔线
        print("面试官：技术总监/CTO")  # 角色
        print("内容：综合评估、战略匹配、发展潜力、最终决策")  # 面试重点
        print("=" * 50)  # 分隔线
        
        try:  # 异常保护
            # 构建基于前面面试结果的开场白  # 根据前两轮对话添加上下文
            boss_message = "你好！我是公司的技术总监，很高兴见到你。"  # 初始问候
            
            # 基于技术面试结果添加针对性内容  # 若有技术面信息，嵌入
            if self.technical_interview_result:
                boss_message += "刚才的技术面试我已经了解了你的技术背景和项目经验。"  # 拼接说明
            
            # 基于HR面试结果添加针对性内容   # 若有 HR 面信息，嵌入
            if self.hr_interview_result:
                boss_message += "HR面试也让我了解了你的职业规划和个人发展目标。"  # 拼接说明
            
            boss_message += """现在我想和你聊聊技术战略和团队发展方面的话题。基于你刚才的表现，我想了解：
 
1. 你对技术发展趋势的看法，特别是与我们公司技术栈相关的领域
2. 在技术团队中，你倾向于什么样的协作方式
3. 你的长期技术发展规划是什么
4. 你对加入我们技术团队有什么想法和期望
5. 基于你刚才的表现，你认为自己最大的技术优势是什么，还有哪些方面需要提升
 
请放松，我们就像技术同行一样交流。"""  # 多行引导问题与语气设置

            # Boss面试官发起对话  # 调用 Boss 智能体
            result = self.boss.initiate_chat(  # 发起聊天
                self.user,  # 面试对象
                message=boss_message,  # 开场内容（包含上下文）
                max_turns=4  # 对话轮数较少
            )
            
            # 保存Boss面试结果  # 存储结果
            self.boss_interview_result = result
            
            print("\nBoss面试完成")  # 完成提示
            
        except Exception as e:  # 异常
            print(f"❌ Boss面试出错: {str(e)}")  # 错误输出
    
    async def generate_interview_scores(self):  # 异步：生成面试评分
        """生成面试评分（基于Boss智能体的评估）"""  # 文档说明
        try:  # 异常保护
            print("\n正在生成面试评分...")  # 提示
            
            # 创建评分智能体  # 构建评分代理
            score_agent = create_score_evaluator()
            
            # 构建对话内容摘要  # 汇总各轮完成标记
            conversation_summary = ""
            
            # 添加技术面试内容  # 若有技术面结果则标记
            if self.technical_interview_result:
                conversation_summary += "技术面试内容：已了解候选人的技术背景和项目经验\n"
            
            # 添加HR面试内容  # 若有 HR 面结果则标记
            if self.hr_interview_result:
                conversation_summary += "HR面试内容：已了解候选人的个人背景和职业规划\n"
            
            # 添加Boss面试内容  # 若有 Boss 面结果则标记
            if self.boss_interview_result:
                conversation_summary += "Boss面试内容：已了解候选人的综合能力和发展潜力\n"
            
            # 构建评分评估内容  # 给 LLM 的完整评分指令与 JSON 模板
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
"""  # 评分提示词与返回 JSON 结构模板
            
            # 获取评分结果  # 向评分智能体发送请求
            score_result = score_agent.generate_reply(
                messages=[{"role": "user", "content": evaluation_content}]  # 以用户消息形式传入
            )
            
            # 尝试解析评分结果  # 解析 LLM 返回文本中的 JSON
            try:
                import json  # 再次导入以就近使用
                # 提取JSON内容（可能包含在回复文本中）  # 先获得文本
                response_text = score_result.content if hasattr(score_result, 'content') else str(score_result)
                
                # 尝试找到JSON部分  # 通过第一个 { 与最后一个 } 截取子串
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:  # 找到合理的 JSON 边界
                    json_str = response_text[start_idx:end_idx]  # 截取
                    parsed_scores = json.loads(json_str)  # 反序列化
                    
                    # 验证评分格式  # 必要字段校验
                    required_keys = ['technical_score', 'hr_score', 'boss_score', 'overall_score', 
                                   'score_details', 'evaluation_summary', 'recommendation', 'improvement_suggestions']
                    
                    if all(key in parsed_scores for key in required_keys):  # 字段齐全
                        self.interview_scores = parsed_scores  # 写入评分
                        print(f"✅ 成功解析评分结果：总分 {self.interview_scores['overall_score']}/100")  # 成功提示
                    else:
                        raise ValueError("评分结果格式不完整")  # 字段缺失
                else:
                    raise ValueError("未找到有效的JSON格式")  # 未检出 JSON
                     
            except (json.JSONDecodeError, ValueError, KeyError) as e:  # 解析期间异常
                print(f"⚠️ 解析评分结果失败: {e}")  # 提示失败
                print("使用默认评分...")  # 使用兜底
                
                # 使用默认评分  # 兜底评分结构
                self.interview_scores = {
                    "technical_score": 75,  # 默认技术分
                    "hr_score": 75,  # 默认 HR 分
                    "boss_score": 75,  # 默认 Boss 分
                    "overall_score": 75,  # 默认总分
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
            
            print(f"面试评分完成：总分 {self.interview_scores['overall_score']}/100")  # 打印最终总分
            
        except Exception as e:  # 评分流程外层异常
            print(f"❌ 评分生成失败: {str(e)}")  # 错误
            # 设置默认评分  # 外层异常时的兜底
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
    
    async def extract_candidate_info(self):  # 异步：抽取候选人信息
        """从面试对话中提取候选人信息"""  # 文档
        try:  # 异常保护
            # 创建信息提取智能体  # 构建 extractor
            info_extractor = create_info_extractor()
            
            # 构建对话内容摘要  # 与评分类似的摘要
            conversation_summary = ""
            
            # 添加技术面试内容  # 有则补充
            if self.technical_interview_result:
                conversation_summary += "技术面试内容：已了解候选人的技术背景和项目经验\n"
            
            # 添加HR面试内容  # 有则补充
            if self.hr_interview_result:
                conversation_summary += "HR面试内容：已了解候选人的个人背景和职业规划\n"
            
            # 添加Boss面试内容  # 有则补充
            if self.boss_interview_result:
                conversation_summary += "Boss面试内容：已了解候选人的综合能力和发展潜力\n"
            
            # 获取候选人信息  # 发送抽取指令
            candidate_info_result = info_extractor.generate_reply(
                messages=[{"role": "user", "content": f"请从以下面试对话中提取候选人信息：\n{conversation_summary}"}]  # 用户消息
            )
            
            # 尝试解析候选人信息  # 解析 JSON
            try:
                import json  # 导入以使用
                # 提取JSON内容  # 获取文本
                response_text = candidate_info_result.content if hasattr(candidate_info_result, 'content') else str(candidate_info_result)
                
                # 尝试找到JSON部分  # 通过 { } 截取
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:  # 找到 JSON
                    json_str = response_text[start_idx:end_idx]  # 截取为字符串
                    parsed_info = json.loads(json_str)  # 反序列化
                    
                    # 验证信息格式  # 必要字段列表
                    required_keys = ['name', 'age', 'education', 'experience_years', 'current_position', 
                                   'target_position', 'technical_skills', 'key_projects', 'career_goals', 'salary_expectation']
                    
                    if all(key in parsed_info for key in required_keys):  # 字段齐全
                        # 检查提取的名字是否有效，避免LLM幻觉  # 防幻觉保护
                        extracted_name = parsed_info.get('name')
                        
                        # 保存原始重要信息，避免被覆盖  # 先缓存原值
                        original_position = self.candidate_info.get('target_position', '')
                        original_skills = self.candidate_info.get('technical_skills', [])
                        original_projects = self.candidate_info.get('key_projects', [])
                        
                        if extracted_name and extracted_name != "未知" and extracted_name != "候选人":  # 姓名有效
                            # 更新候选人信息，但保留原始重要信息  # 选择性更新
                            temp_parsed_info = parsed_info.copy()  # 拷贝
                            temp_parsed_info.pop('name', None)  # 移除提取的名字（保留原始）
                            temp_parsed_info.pop('target_position', None)  # 移除职位（保留原始）
                            temp_parsed_info.pop('technical_skills', None)  # 移除技能（保留原始）
                            temp_parsed_info.pop('key_projects', None)  # 移除项目（保留原始）
                            self.candidate_info.update(temp_parsed_info)  # 合并更新
                            print(f"✅ 成功提取候选人信息（保留原始重要信息：{self.candidate_info.get('name', '未知')} - {original_position}）")  # 成功提示
                        else:
                            # 提取的名字无效，只更新其他信息，保留原始重要信息  # 姓名无效时的策略
                            temp_parsed_info = parsed_info.copy()
                            temp_parsed_info.pop('name', None)
                            temp_parsed_info.pop('target_position', None)  # 移除职位
                            temp_parsed_info.pop('technical_skills', None)  # 移除技能
                            temp_parsed_info.pop('key_projects', None)  # 移除项目
                            self.candidate_info.update(temp_parsed_info)  # 合并
                            print(f"⚠️ 提取的候选人名字无效或未知，保留原始重要信息: {self.candidate_info.get('name', '未知')} - {original_position}")  # 提示
                        
                        # 确保重要信息不被覆盖  # 恢复关键字段
                        if original_position and original_position != "未知":
                            self.candidate_info['target_position'] = original_position
                        if original_skills:
                            self.candidate_info['technical_skills'] = original_skills
                        if original_projects:
                            self.candidate_info['key_projects'] = original_projects
                    else:
                        raise ValueError("候选人信息格式不完整")  # 字段缺失
                else:
                    raise ValueError("未找到有效的JSON格式")  # 未检出 JSON
                     
            except (json.JSONDecodeError, ValueError, KeyError) as e:  # 解析异常
                print(f"⚠️ 解析候选人信息失败: {e}")  # 提示失败
                print("保留原始候选人信息...")  # 保留原值
            
            # 智能职位推断逻辑  # 如果无明确职位，基于技能/项目推断
            candidate_skills = self.candidate_info.get("technical_skills", [])  # 技能列表
            candidate_projects = self.candidate_info.get("key_projects", [])  # 项目列表
            
            # 保存原始职位信息  # 缓存
            original_position = self.candidate_info.get('target_position', '')
            
            # 如果已有明确的职位信息且不是"未知"，则保留  # 不覆盖已有明确值
            if original_position and original_position != "未知":
                print(f"✅ 保留原始职位信息: {original_position}")  # 提示
                # 确保职位信息不被覆盖  # 再次写回
                self.candidate_info['target_position'] = original_position
            else:
                # 只有在确实没有职位信息时才进行智能推断  # 调用推断函数
                inferred_position = self._infer_position_from_skills_and_projects(candidate_skills, candidate_projects)
                self.candidate_info['target_position'] = inferred_position  # 写回推断值
                print(f"✅ 智能推断职位: {inferred_position}")  # 提示
            
            print("候选人信息提取完成")  # 完成提示
            
        except Exception as e:  # 外层异常
            print(f"❌ 候选人信息提取失败: {str(e)}")  # 错误提示
            print("保留原始候选人信息...")  # 兜底
    
    def _infer_position_from_skills_and_projects(self, skills, projects):  # 同步：职位智能推断
        """根据技能和项目经验智能推断职位
         
        Args:
            skills (list): 技能列表
            projects (list): 项目经验列表
             
        Returns:
            str: 推断的职位名称
        """  # 文档
        # 定义技能分类和权重  # 关键词、候选职位、加权
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
        
        # 计算每个类别的得分  # 统计技能与项目关键词匹配
        category_scores = {}
        for category, config in skill_categories.items():  # 遍历分类
            score = 0  # 初始分
            for skill in skills:  # 遍历技能
                for keyword in config["keywords"]:  # 遍历关键词
                    if keyword in skill:  # 匹配到关键词
                        score += 1  # 计分+1
                        break  # 每个技能只计算一次
             
            # 考虑项目经验  # 项目命中加 0.5
            for project in projects:
                for keyword in config["keywords"]:
                    if keyword in project:
                        score += 0.5  # 项目经验权重较低
                        break
             
            category_scores[category] = score * config["weight"]  # 乘以类别权重
        
        # 找出得分最高的类别  # 选择最佳类别
        if category_scores:
            # 打印调试信息  # 输出每类得分
            print("=== 职位推断调试信息 ===")
            for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"{category}: {score}")  # 从高到低打印
             
            top_category = max(category_scores.items(), key=lambda x: x[1])  # 最高分类别
            if top_category[1] > 0:
                # 根据得分选择具体职位  # 按类别选择候选职位
                category_config = skill_categories[top_category[0]]
                positions = category_config["positions"]
                
                # 特殊处理：如果候选人明确有大模型相关技能和项目，优先考虑AI/ML职位  # 大模型优先
                ai_ml_indicators = [
                    any("大模型" in skill for skill in skills),
                    any("LLM" in skill for skill in skills),
                    any("LoRA" in skill for skill in skills),
                    any("大模型" in project for project in projects),
                    any("LLM" in project for project in projects),
                    any("LoRA" in project for project in projects)
                ]
                
                if any(ai_ml_indicators) and top_category[0] in ["ai_ml", "backend_dev"]:  # 满足大模型迹象
                    print("检测到大模型相关技能/项目，优先考虑AI/ML职位")  # 调试提示
                    if any("大模型" in skill or "LLM" in skill for skill in skills):
                        return "大模型算法工程师"  # 精确返回
                    elif any("机器学习" in skill or "深度学习" in skill for skill in skills):
                        return "机器学习工程师"  # 次优
                    else:
                        return "AI工程师"  # 兜底 AI
                 
                # 根据技能特点选择最合适的职位  # 非特殊情况
                if top_category[0] == "ai_ml":
                    # AI/ML类别，进一步细分  # 再按技能细化
                    if any("大模型" in skill or "LLM" in skill for skill in skills):
                        return "大模型算法工程师"
                    elif any("机器学习" in skill or "深度学习" in skill for skill in skills):
                        return "机器学习工程师"
                    else:
                        return "AI工程师"
                elif top_category[0] == "backend_dev":
                    # 后端开发类别  # 再判断云原生/微服务
                    if any("云原生" in skill or "微服务" in skill for skill in skills):
                        return "云原生后端工程师"
                    else:
                        return "Python开发工程师"
                else:
                    # 其他类别返回第一个职位  # 直接选首位
                    return positions[0]
        
        # 如果没有匹配到任何类别，返回默认职位  # 全无命中时的默认
        return "Python开发工程师"
    
    async def generate_offer_if_qualified(self):  # 异步：若达标生成 Offer
        """如果候选人分数>=60，生成offer通知信"""  # 文档
        try:  # 异常保护
            overall_score = self.interview_scores.get("overall_score", 0)  # 读取总分
             
            if not should_generate_offer(overall_score):  # 判断达标与否
                print(f"\n候选人总分{overall_score}分，未达到发放offer标准（>=60分）")  # 不达标提示
                return  # 直接返回
             
            print(f"\n候选人总分{overall_score}分，达到发放offer标准，正在生成offer通知信...")  # 达标提示
             
            # 构建面试数据  # 传给生成器的上下文
            interview_data = {
                "interview_scores": self.interview_scores,  # 评分
                "candidate_profile": self.candidate_info  # 画像
            }
             
            # 生成offer通知信  # 调用生成器
            self.offer_letter = generate_offer_letter(interview_data)
             
            print("✅ Offer通知信生成完成！")  # 成功提示
            print("\n" + "=" * 80)  # 分隔线
            print("OFFER通知信")  # 标题
            print("=" * 80)  # 分隔线
            print(self.offer_letter)  # 打印正文
            print("=" * 80)  # 分隔线
             
            # 保存offer到文件  # 按候选人名建目录保存
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 时间戳
             
            # 获取候选人名字  # 用于目录与文件名
            candidate_name = self.candidate_info.get('name', f"候选人_{current_time}")
             
            # 创建候选人文件夹（如果不存在）  # 在 60plus 下保存
            candidate_folder = f"data/interview_results/60plus/{candidate_name}"
            if not os.path.exists(candidate_folder):
                os.makedirs(candidate_folder)  # 递归创建
             
            offer_filename = f"{candidate_folder}/offer_letter_{current_time}.txt"  # 文件名
             
            with open(offer_filename, 'w', encoding='utf-8') as f:  # 打开文件
                f.write(self.offer_letter)  # 写入正文
             
            print(f"\nOffer通知信已保存到: {offer_filename}")  # 保存位置提示
             
        except Exception as e:  # 异常
            print(f"❌ 生成offer通知信失败: {str(e)}")  # 错误提示
    
    async def generate_interview_summary(self):  # 异步：打印面试总结
        """生成面试总结"""  # 文档
        print("\n面试总结报告")  # 标题
        print("=" * 60)  # 分隔线
        print("三轮面试已完成")  # 概览
         
        # 显示评分结果  # 打印分项与总分
        print(f"\n📊 面试评分结果：")  # 标题
        print(f"技术面试：{self.interview_scores['technical_score']}/100")  # 技术分
        print(f"HR面试：{self.interview_scores['hr_score']}/100")  # HR 分
        print(f"Boss面试：{self.interview_scores['boss_score']}/100")  # Boss 分
        print(f"总分：{self.interview_scores['overall_score']}/100")  # 总分
        print(f"最终建议：{self.interview_scores.get('recommendation', '需要进一步评估')}")  # 建议
         
        print("\n面试内容回顾：")  # 段落标题
        print("技术面试：")  # 小节
        print("  - 技术能力评估")  # 条目
        print("  - 项目经验探讨")  # 条目
        print("  - 问题解决能力测试")  # 条目
        print("  - 技术发展趋势讨论")  # 条目
         
        print("\nHR面试：")  # 小节
        print("  - 个人背景了解")  # 条目
        print("  - 职业规划评估")  # 条目
        print("  - 团队协作能力")  # 条目
        print("  - 企业文化匹配")  # 条目
        print("  - 薪资期望沟通")  # 条目
         
        print("\nBoss面试：")  # 小节
        print("  - 综合能力评估")  # 条目
        print("  - 技术战略匹配")  # 条目
        print("  - 团队融入能力")  # 条目
        print("  - 发展潜力评估")  # 条目
        print("  - 最终录用决策")  # 条目
         
        print("\n后续建议：")  # 小节
        print("  - 等待面试结果通知")  # 条目
        print("  - 可继续使用career_agent工具进行技能评估")  # 条目
        print("  - 制定个人发展计划")  # 条目
    
    async def save_interview_results(self):  # 异步：保存面试结果到 JSON
        """保存面试结果到JSON文件"""  # 文档
        try:  # 异常保护
            # 获取当前时间  # 时间戳
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
             
            # 提取面试对话内容  # 初始化对话列表
            technical_conversation = []
            hr_conversation = []
            boss_conversation = []
             
            # 提取技术面试对话内容  # 从结果对象抽取聊天历史
            if self.technical_interview_result:
                try:
                    # 尝试从对话结果中提取消息  # 兼容 messages
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
                        # 如果无法提取具体对话，至少保存面试完成信息  # 占位
                        technical_conversation.append({
                            "role": "system",
                            "content": "技术面试已完成，对话内容已记录",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                except Exception as e:
                    print(f"提取技术面试对话失败: {e}")  # 提取失败提示
                    technical_conversation.append({
                        "role": "system",
                        "content": "技术面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
             
            # 提取HR面试对话内容  # 同上逻辑
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
                    print(f"提取HR面试对话失败: {e}")  # 提示
                    hr_conversation.append({
                        "role": "system",
                        "content": "HR面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
             
            # 提取Boss面试对话内容  # 同上逻辑
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
                    print(f"提取Boss面试对话失败: {e}")  # 提示
                    boss_conversation.append({
                        "role": "system",
                        "content": "Boss面试已完成",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
             
            # 创建面试结果数据  # 组织完整 JSON 结构
            interview_results = {
                "interview_info": {
                    "candidate_name": getattr(self, 'candidate_info', {}).get('name', '候选人'),  # 姓名
                    "position": getattr(self, 'candidate_info', {}).get('target_position', '应聘职位'),  # 目标职位
                    "interview_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 日期
                    "interview_id": f"INT_{current_time}",  # 面试 ID
                    "total_score": self.interview_scores["overall_score"]  # 总分
                },
                "interview_scores": self.interview_scores,  # 分数详情
                "interview_rounds": {
                    "technical_interview": {
                        "interviewer": "技术面试官",  # 角色
                        "focus_areas": [
                            "技术能力评估",
                            "项目经验探讨", 
                            "问题解决能力测试",
                            "技术发展趋势讨论"
                        ],  # 关注点
                        "status": "completed",  # 状态
                        "score": self.interview_scores["technical_score"],  # 分数
                        "conversation": technical_conversation,  # 对话细节
                        "summary": "技术面试已完成，评估了候选人的技术能力、项目经验和问题解决能力"  # 小结
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
                    "total_rounds": 3,  # 总轮数
                    "interview_sequence": [
                        "技术面试 → HR面试 → Boss面试"
                    ],  # 流程顺序描述
                    "boss_evaluation_basis": [
                        "基于技术面试的技术能力评估",
                        "基于HR面试的沟通协作能力评估", 
                        "综合两轮面试的学习能力和发展潜力评估"
                    ]  # Boss 评估依据
                },
                "candidate_profile": getattr(self, 'candidate_info', {  # 候选人画像（无则默认）
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
             
            # 获取候选人名字  # 用于目录划分
            candidate_name = self.candidate_info.get('name', f"候选人_{current_time}")
             
            # 根据分数确定保存文件夹  # >=60 保存到 60plus，否则 below60
            overall_score = self.interview_scores["overall_score"]
            if overall_score >= 60:
                base_folder = "data/interview_results/60plus"
            else:
                base_folder = "data/interview_results/below60"
             
            # 创建以候选人名字命名的文件夹  # 若不存在则创建
            candidate_folder = f"{base_folder}/{candidate_name}"
            if not os.path.exists(candidate_folder):
                os.makedirs(candidate_folder)
                print(f"创建候选人文件夹: {candidate_folder}")  # 提示
             
            # 保存到JSON文件  # 写盘
            filename = f"{candidate_folder}/interview_results_{current_time}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(interview_results, f, ensure_ascii=False, indent=2)  # UTF-8 + 缩进
             
            print(f"\n面试结果已保存到: {filename}")  # 路径提示
            print(f"总分: {overall_score}/100")  # 分数提示
            print(f"保存位置: {candidate_folder}/")  # 目录提示
            print("文件包含完整的面试对话内容和评分详情")  # 内容说明
             
        except Exception as e:  # 外层异常
            print(f"❌ 保存面试结果失败: {str(e)}")  # 错误提示
    
    async def conduct_full_interview(self):  # 异步：进行完整面试流程
        """进行完整面试流程"""  # 文档
        print("智能面试系统 - 三角色面试")  # 标题
        print("=" * 60)  # 分隔线
        print("面试流程：技术面试 → HR面试 → Boss面试")  # 流程说明
        print("角色：技术面试官 + HR面试官 + Boss面试官 + 面试者")  # 角色说明
        print("=" * 60)  # 分隔线
                 
        # 从candidate_agent.py动态获取默认候选人信息  # 延迟导入避免循环依赖
        from agents.candidate_agent import get_default_candidate_info, create_candidate_agent  # 动态导入
         
        # 获取默认候选人信息  # 默认画像
        candidate_info = get_default_candidate_info()
         
        # 获取候选人职位信息  # 若无则默认 Python 开发
        target_position = candidate_info.get('target_position', 'Python开发工程师')
         
        # 创建智能体  # 三位面试官 + 候选人
        self.interviewer = create_technical_interviewer(target_position)
        self.hr = create_hr_interviewer(target_position)
        self.boss = create_boss_interviewer()
        self.user = create_candidate_agent(candidate_info)
         
        # 保存候选人信息供后续使用  # 缓存画像到实例
        self.candidate_info = candidate_info
         
        print("\n面试开始...")  # 提示
        print("注意：现在是AI智能体自动对话演示。")  # 说明
        print("-" * 60)  # 分隔线
         
        try:  # 流程保护
            # 第一阶段：技术面试  # 执行
            await self.conduct_technical_interview()
            
            print("\n" + "=" * 60)  # 分隔线
            print("技术面试结束，准备进入HR面试...")  # 流转提示
            print("=" * 60)  # 分隔线
            
            # 第二阶段：HR面试  # 执行
            await self.conduct_hr_interview()
            
            print("\n" + "=" * 60)  # 分隔线
            print("HR面试结束，准备进入Boss面试...")  # 流转提示
            print("=" * 60)  # 分隔线
            
            # 第三阶段：Boss面试  # 执行
            await self.conduct_boss_interview()
            
            # 生成评分  # 调用评分流程
            await self.generate_interview_scores()
 
            # 提取候选人信息  # 调用抽取与推断
            await self.extract_candidate_info()
            
            # 生成总结  # 打印报告
            await self.generate_interview_summary()
            
            # 保存面试结果  # 写 JSON
            await self.save_interview_results()
            
            # 生成offer通知信（如果分数>=60）  # 条件生成并写盘
            await self.generate_offer_if_qualified()
            
        except Exception as e:  # 全流程异常
            print(f"❌ 面试过程中出现错误: {str(e)}")  # 错误提示

async def main():  # 异步主函数
    """主函数"""  # 文档
    print("欢迎参加智能面试系统")  # 欢迎语
    print("=" * 50)  # 分隔线
    print("AI智能体自动演示三轮面试：")  # 说明
    print("1. 技术面试 - 技术面试官 vs 面试者")  # 列举阶段
    print("2. HR面试 - HR面试官 vs 面试者")  # 列举阶段
    print("3. Boss面试 - 技术总监 vs 面试者")  # 列举阶段
    print("\n面试者：AI智能体（模拟真实候选人）")  # 面试者类型
    print("演示完整的面试对话流程！")  # 说明
    print("=" * 50)  # 分隔线
     
    input("按回车键开始面试...")  # 等待用户按回车
     
    interview_system = ThreeRoleInterviewSystem()  # 实例化系统
    await interview_system.conduct_full_interview()  # 运行完整流程

if __name__ == "__main__":  # 脚本直接执行时的入口
    try:
        asyncio.run(main())  # 运行异步主函数
    except KeyboardInterrupt:
        print("\n\n面试被中断")  # 捕获 Ctrl+C
    except Exception as e:
        print(f"\n系统错误: {str(e)}")  # 其他异常
        print("请检查API密钥和网络连接")  # 排查建议