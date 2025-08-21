#!/usr/bin/env python3
"""
HR Offer Agent - 负责生成offer通知信
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path

# MCP 协议相关导入
try:
    from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("警告: MCP 协议不可用，将使用直接 HTTP 调用")

# Adzuna API 配置（从环境变量读取）
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
ADZUNA_BASE_URL = os.getenv("ADZUNA_BASE_URL", "https://api.adzuna.com/v1/api/jobs/gb/search/1")

async def get_market_salary_data(position="Python Developer", location="London"):
    """通过 Adzuna API 获取市场薪资数据"""
    # 优先使用 MCP 协议
    if MCP_AVAILABLE:
        return await get_market_salary_data_mcp(position, location)
    else:
        # 备用方案：直接 HTTP 调用
        return await get_market_salary_data_http(position, location)

async def get_market_salary_data_mcp(position="Python Developer", location="London"):
    """通过 MCP 协议获取市场薪资数据"""
    try:
        # 创建 MCP 服务器连接
        adzuna_server = StdioServerParams(
            command="python",
            args=["mcp_servers/adzuna_mcp_server.py"]
        )
        
        # 获取 MCP 工具
        tools = await mcp_server_tools(adzuna_server)
        
        # 查找薪资数据工具
        for tool in tools:
            if tool.get("name") == "get_market_salary_data":
                # 调用 MCP 工具
                result = await tool["function"](position=position, location=location)
                if result.get("success", True):
                    return {
                        'average_salary': result.get('average_salary'),
                        'min_salary': result.get('min_salary'),
                        'max_salary': result.get('max_salary'),
                        'sample_count': result.get('sample_count'),
                        'currency': result.get('currency', 'GBP')
                    }
                else:
                    print(f"MCP 调用失败: {result.get('error')}")
                    return None
        
        print("未找到 MCP 工具")
        return None
        
    except Exception as e:
        print(f"MCP 获取市场薪资数据失败: {e}")
        return None

async def get_market_salary_data_http(position="Python Developer", location="London"):
    """通过直接 HTTP 调用获取市场薪资数据（备用方案）"""
    try:
        # 构建 API URL
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'results_per_page': 50,
            'what': position,
            'where': location
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(ADZUNA_BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return analyze_salary_data(data)
                else:
                    print(f"Adzuna API 请求失败: {response.status}")
                    return None
    except Exception as e:
        print(f"获取市场薪资数据失败: {e}")
        return None

def analyze_salary_data(api_data):
    """分析 API 返回的薪资数据"""
    try:
        results = api_data.get('results', [])
        if not results:
            return None
            
        salaries = []
        for job in results:
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            if salary_min and salary_max:
                avg_salary = (salary_min + salary_max) / 2
                salaries.append(avg_salary)
        
        if salaries:
            avg_market_salary = sum(salaries) / len(salaries)
            min_salary = min(salaries)
            max_salary = max(salaries)
            
            return {
                'average_salary': round(avg_market_salary, 2),
                'min_salary': round(min_salary, 2),
                'max_salary': round(max_salary, 2),
                'sample_count': len(salaries),
                'currency': 'GBP'
            }
    except Exception as e:
        print(f"分析薪资数据失败: {e}")
    
    return None

def create_hr_offer_agent():
    """创建HR offer agent"""
    return {
        "name": "hr_offer_agent",
        "description": "HR offer生成助手，负责根据面试结果和市场数据生成offer通知信",
        "system_message": """
你是一个专业的HR助手，专门负责处理招聘后续工作。

**任务要求：**
请根据提供的候选人面试信息和实时市场薪资数据，直接生成一份完整的、可直接使用的offer通知信。不要询问确认，直接输出最终版本。

**输出格式：**
1. 候选人面试表现分析（简洁明了）
2. 实时市场薪资参考（基于Adzuna API数据）
3. 完整的offer通知信（包含所有必要信息）

**薪资建议：**
- 78分以上：市场薪资区间的75-90百分位数（高于市场平均）
- 70-77分：市场薪资区间的60-75百分位数（接近市场平均）
- 60-69分：市场薪资区间的40-60百分位数（低于市场平均）

**注意事项：**
- 薪资建议要基于面试分数和实时市场数据
- Offer信要专业、正式、完整
- 所有输出都要用中文
- 直接输出最终版本，不要重复确认
- 包含具体的联系方式、入职时间等详细信息
        """
    }

def get_latest_interview_result():
    """获取最新的面试结果JSON文件"""
    try:
        # 查找面试结果文件（包括60分以上和以下的所有候选人文件夹）
        base_dir = Path("data/interview_results")
        
        if not base_dir.exists():
            return None
        
        # 收集所有候选人文件夹中的JSON文件
        json_files = []
        
        # 检查60分以上的候选人文件夹
        plus_dir = base_dir / "60plus"
        if plus_dir.exists():
            for candidate_dir in plus_dir.iterdir():
                if candidate_dir.is_dir():
                    json_files.extend(list(candidate_dir.glob("*.json")))
        
        # 检查60分以下的候选人文件夹
        below_dir = base_dir / "below60"
        if below_dir.exists():
            for candidate_dir in below_dir.iterdir():
                if candidate_dir.is_dir():
                    json_files.extend(list(candidate_dir.glob("*.json")))
        
        # 如果没有找到文件，尝试旧格式
        if not json_files:
            json_files = list(base_dir.glob("*.json"))
        
        if not json_files:
            return None
            
        # 获取最新的文件
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"读取面试结果文件失败: {e}")
        return None

async def generate_offer_letter_with_market_data(interview_data):
    """根据面试数据和市场数据生成offer通知信"""
    if not interview_data:
        return "无法获取面试结果数据"
    
    # 提取面试信息
    interview_scores = interview_data.get("interview_scores", {})
    candidate_info = interview_data.get("candidate_profile", {})
    
    total_score = interview_scores.get("overall_score", 0)
    technical_score = interview_scores.get("technical_score", 0)
    hr_score = interview_scores.get("hr_score", 0)
    boss_score = interview_scores.get("boss_score", 0)
    
    candidate_name = candidate_info.get("name", "候选人")
    if candidate_name == "未知":
        candidate_name = "候选人"
        
    target_position = candidate_info.get("target_position", "Python开发工程师")  
    if target_position == "未知":
        target_position = "Python开发工程师"
    
    # 职位名称映射（中文到英文）
    position_mapping = {
        # 传统开发职位
        "Python开发工程师": "Python Developer",
        "Python工程师": "Python Developer",
        "后端开发工程师": "Backend Developer",
        "前端开发工程师": "Frontend Developer",
        "全栈开发工程师": "Full Stack Developer",
        "软件工程师": "Software Engineer",
        "系统工程师": "Systems Engineer",
        "DevOps工程师": "DevOps Engineer",
        "云原生后端工程师": "Cloud Native Backend Engineer",
        "数据后端工程师": "Data Backend Engineer",
        
        # 数据科学和机器学习
        "数据科学家": "Data Scientist",
        "数据分析师": "Data Analyst",
        "机器学习工程师": "Machine Learning Engineer",
        "深度学习工程师": "Deep Learning Engineer",
        "AI工程师": "AI Engineer",
        "人工智能工程师": "AI Engineer",
        "数据工程师": "Data Engineer",
        "数据平台工程师": "Data Platform Engineer",
        
        # 算法和AI专业方向
        "算法工程师": "Algorithm Engineer",
        "大模型算法工程师": "LLM Algorithm Engineer",
        "自然语言处理工程师": "NLP Engineer",
        "计算机视觉工程师": "Computer Vision Engineer",
        "推荐算法工程师": "Recommendation Algorithm Engineer",
        "搜索算法工程师": "Search Algorithm Engineer",
        "语音识别工程师": "Speech Recognition Engineer",
        "知识图谱工程师": "Knowledge Graph Engineer",
        "全栈AI工程师": "Full Stack AI Engineer",
        
        # 新兴AI职位
        "Prompt工程师": "Prompt Engineer",
        "AI产品经理": "AI Product Manager",
        "机器学习研究员": "ML Researcher",
        "AI架构师": "AI Architect",
        "模型工程师": "Model Engineer",
        "AI运维工程师": "AI Ops Engineer",
        "大模型训练工程师": "LLM Training Engineer",
        "AI推理优化工程师": "AI Inference Engineer",
        
        # 移动开发
        "移动开发工程师": "Mobile Developer",
        "Android开发工程师": "Android Developer",
        "iOS开发工程师": "iOS Developer",
        
        # 安全相关
        "安全工程师": "Security Engineer",
        "网络安全工程师": "Cybersecurity Engineer",
        
        # 游戏开发
        "游戏开发工程师": "Game Developer",
        
        # 前端相关
        "前端开发工程师": "Frontend Developer",
        "UI/UX工程师": "UI/UX Engineer"
    }
    
    # 根据候选人信息动态调整职位描述
    candidate_skills = candidate_info.get("technical_skills", [])
    candidate_projects = candidate_info.get("key_projects", [])
    
    # 定义技能分类和权重
    skill_categories = {
        "ai_ml": {
            "keywords": ["大模型", "LLM", "LoRA", "微调", "深度学习", "机器学习", "AI", "人工智能", "NLP", "自然语言处理", "计算机视觉", "推荐算法", "向量数据库", "FAISS", "Milvus", "LangChain", "RAG", "Prompt Engineering", "Transformer", "BERT", "GPT", "强化学习", "知识图谱"],
            "weight": 1.5
        },
        "backend_dev": {
            "keywords": ["Django", "Flask", "FastAPI", "MySQL", "PostgreSQL", "Redis", "Docker", "微服务", "高并发", "API", "后端", "Spring Boot", "Node.js", "Go", "微服务架构", "分布式系统"],
            "weight": 1.0
        },
        "frontend_dev": {
            "keywords": ["React", "Vue", "Angular", "JavaScript", "TypeScript", "前端", "UI/UX", "Web开发", "移动端", "小程序"],
            "weight": 0.8
        },
        "data_engineering": {
            "keywords": ["数据工程", "ETL", "数据仓库", "Spark", "Hadoop", "Kafka", "数据湖", "数据管道", "数据治理", "BI", "数据可视化"],
            "weight": 1.2
        },
        "cloud_devops": {
            "keywords": ["Kubernetes", "AWS", "Azure", "GCP", "云原生", "DevOps", "CI/CD", "Jenkins", "GitLab", "监控", "日志", "容器化"],
            "weight": 1.1
        },
        "mobile_dev": {
            "keywords": ["Android", "iOS", "移动开发", "React Native", "Flutter", "原生开发", "移动应用"],
            "weight": 0.9
        },
        "security": {
            "keywords": ["网络安全", "信息安全", "渗透测试", "安全开发", "加密", "认证", "授权", "安全架构"],
            "weight": 1.3
        },
        "game_dev": {
            "keywords": ["游戏开发", "Unity", "Unreal", "游戏引擎", "3D建模", "游戏设计"],
            "weight": 0.7
        }
    }
    
    # 计算各技能类别的得分
    skill_scores = {}
    for category, config in skill_categories.items():
        score = sum(1 for skill in candidate_skills if any(keyword in skill for keyword in config["keywords"]))
        skill_scores[category] = score * config["weight"]
    
    # 分析项目经验
    project_analysis = {
        "ai_ml_projects": sum(1 for project in candidate_projects if any(keyword in str(project) for keyword in ["大模型", "LLM", "AI", "机器学习", "深度学习", "算法"])),
        "backend_projects": sum(1 for project in candidate_projects if any(keyword in str(project) for keyword in ["后端", "API", "微服务", "数据库", "系统"])),
        "data_projects": sum(1 for project in candidate_projects if any(keyword in str(project) for keyword in ["数据", "分析", "ETL", "仓库"])),
        "cloud_projects": sum(1 for project in candidate_projects if any(keyword in str(project) for keyword in ["云", "容器", "部署", "运维"]))
    }
    
    # 调试信息：输出技能得分
    print("=== HR Offer Agent 技能分析调试 ===")
    print(f"候选人技能: {candidate_skills}")
    print(f"候选人项目: {candidate_projects}")
    print(f"技能得分: {skill_scores}")
    print(f"项目分析: {project_analysis}")
    
    # 职位智能匹配逻辑
    def determine_position():
        # 获取最高分的技能类别
        top_skill = max(skill_scores.items(), key=lambda x: x[1])
        
        # 根据技能组合和项目经验确定职位
        if top_skill[0] == "ai_ml" and top_skill[1] >= 3:
            if project_analysis["ai_ml_projects"] >= 2:
                if any("大模型" in skill or "LLM" in skill for skill in candidate_skills):
                    return "大模型算法工程师"
                elif any("推荐" in skill or "搜索" in skill for skill in candidate_skills):
                    return "推荐算法工程师"
                elif any("NLP" in skill or "自然语言" in skill for skill in candidate_skills):
                    return "自然语言处理工程师"
                elif any("计算机视觉" in skill or "CV" in skill for skill in candidate_skills):
                    return "计算机视觉工程师"
                else:
                    return "机器学习工程师"
            else:
                return "AI工程师"
        
        elif top_skill[0] == "backend_dev" and top_skill[1] >= 2:
            if project_analysis["cloud_projects"] >= 1:
                return "云原生后端工程师"
            elif project_analysis["data_projects"] >= 1:
                return "数据后端工程师"
            else:
                return "后端开发工程师"
        
        elif top_skill[0] == "data_engineering" and top_skill[1] >= 2:
            if project_analysis["ai_ml_projects"] >= 1:
                return "数据科学家"
            else:
                return "数据工程师"
        
        elif top_skill[0] == "cloud_devops" and top_skill[1] >= 2:
            return "DevOps工程师"
        
        elif top_skill[0] == "frontend_dev" and top_skill[1] >= 2:
            return "前端开发工程师"
        
        elif top_skill[0] == "mobile_dev" and top_skill[1] >= 2:
            return "移动开发工程师"
        
        elif top_skill[0] == "security" and top_skill[1] >= 2:
            return "安全工程师"
        
        elif top_skill[0] == "game_dev" and top_skill[1] >= 2:
            return "游戏开发工程师"
        
        # 多技能组合情况
        elif skill_scores["ai_ml"] >= 2 and skill_scores["backend_dev"] >= 2:
            return "全栈AI工程师"
        
        elif skill_scores["backend_dev"] >= 2 and skill_scores["frontend_dev"] >= 1:
            return "全栈开发工程师"
        
        elif skill_scores["data_engineering"] >= 2 and skill_scores["backend_dev"] >= 1:
            return "数据平台工程师"
        
        # 默认情况
        else:
            return target_position if target_position != "未知" else "软件工程师"
    
    # 确定最终职位
    refined_position = determine_position()
    
    # 转换为英文职位名称
    english_position = position_mapping.get(refined_position, "Python Developer")
    
    # 更新英文职位名称
    english_position = position_mapping.get(refined_position, english_position)
    
    # 获取实时市场薪资数据
    market_data = await get_market_salary_data(english_position, "London")
    
    # 根据分数和市场数据确定薪资范围
    if market_data:
        min_market_salary = market_data['min_salary']
        max_market_salary = market_data['max_salary']
        avg_market_salary = market_data['average_salary']
        
        # 计算市场薪资区间的百分位数位置
        if total_score >= 78:
            # 高分：75-90百分位数（高于市场平均）
            position_factor = 0.75 + (total_score - 78) / 22 * 0.15  # 78-100分映射到75%-90%
            suggested_position = 0.82  # 82%位置
        elif total_score >= 70:
            # 中上分：60-75百分位数（接近市场平均）
            position_factor = 0.60 + (total_score - 70) / 8 * 0.15   # 70-77分映射到60%-75%
            suggested_position = 0.67  # 67%位置
        else:
            # 及格分：40-60百分位数（低于市场平均）
            position_factor = 0.40 + (total_score - 60) / 10 * 0.20  # 60-69分映射到40%-60%
            suggested_position = 0.50  # 50%位置（中位数）
        
        # 基于市场区间计算薪资
        suggested_salary_value = min_market_salary + (max_market_salary - min_market_salary) * suggested_position
        range_min = min_market_salary + (max_market_salary - min_market_salary) * (suggested_position - 0.05)
        range_max = min_market_salary + (max_market_salary - min_market_salary) * (suggested_position + 0.05)
        
        salary_range = f"{round(range_min, 0):,.0f}-{round(range_max, 0):,.0f}英镑/年"
        suggested_salary = f"{round(suggested_salary_value, 0):,.0f}英镑/年"
        
        # 根据候选人技能和职位生成个性化的市场分析
        skill_analysis = ""
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        skill_names = []
        for skill_type, score in top_skills:
            if score > 0:
                if skill_type == "ai_ml":
                    skill_names.append("AI/机器学习")
                elif skill_type == "backend_dev":
                    skill_names.append("后端开发")
                elif skill_type == "frontend_dev":
                    skill_names.append("前端开发")
                elif skill_type == "data_engineering":
                    skill_names.append("数据工程")
                elif skill_type == "cloud_devops":
                    skill_names.append("云原生/DevOps")
                elif skill_type == "mobile_dev":
                    skill_names.append("移动开发")
                elif skill_type == "security":
                    skill_names.append("安全技术")
                elif skill_type == "game_dev":
                    skill_names.append("游戏开发")
        
        if skill_names:
            skill_analysis = f"候选人主要技能方向：{', '.join(skill_names)}，技能匹配度：{top_skills[0][1]:.1f}分，符合{refined_position}岗位要求。"
        else:
            skill_analysis = f"候选人技能信息待完善，根据职位要求匹配{refined_position}岗位。"
        
        market_info = f"""
**实时市场薪资数据（基于{market_data['sample_count']}个职位样本）：**
- 目标职位：{refined_position}（{english_position}）
- 市场平均薪资：{market_data['average_salary']:,.0f}英镑/年
- 市场薪资范围：{market_data['min_salary']:,.0f} - {market_data['max_salary']:,.0f}英镑/年
- 技能匹配分析：{skill_analysis}
- 数据来源：Adzuna API（实时更新）
"""
    else:
        # 如果无法获取市场数据，使用默认薪资
        if total_score >= 78:
            salary_range = "60,000-65,000英镑/年"
            suggested_salary = "62,000英镑/年"
        elif total_score >= 70:
            salary_range = "55,000-60,000英镑/年"
            suggested_salary = "57,000英镑/年"
        else:
            salary_range = "50,000-55,000英镑/年"
            suggested_salary = "52,000英镑/年"
        
        # 根据候选人技能生成个性化的市场分析
        skill_analysis = ""
        # 重新计算技能得分（因为备用方案中没有skill_scores）
        skill_categories = {
            "ai_ml": ["大模型", "LLM", "LoRA", "微调", "深度学习", "机器学习", "AI", "人工智能", "NLP", "自然语言处理", "计算机视觉", "推荐算法", "向量数据库", "FAISS", "Milvus", "LangChain", "RAG", "Prompt Engineering"],
            "backend_dev": ["Django", "Flask", "FastAPI", "MySQL", "PostgreSQL", "Redis", "Docker", "微服务", "高并发", "API", "后端"],
            "frontend_dev": ["React", "Vue", "Angular", "JavaScript", "TypeScript", "前端", "UI/UX", "Web开发"],
            "data_engineering": ["数据工程", "ETL", "数据仓库", "Spark", "Hadoop", "Kafka", "数据湖", "数据管道"],
            "cloud_devops": ["Kubernetes", "AWS", "Azure", "GCP", "云原生", "DevOps", "CI/CD", "Jenkins", "GitLab", "监控", "日志", "容器化"]
        }
        
        skill_scores = {}
        for category, keywords in skill_categories.items():
            score = sum(1 for skill in candidate_skills if any(keyword in skill for keyword in keywords))
            skill_scores[category] = score
        
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        skill_names = []
        for skill_type, score in top_skills:
            if score > 0:
                if skill_type == "ai_ml":
                    skill_names.append("AI/机器学习")
                elif skill_type == "backend_dev":
                    skill_names.append("后端开发")
                elif skill_type == "frontend_dev":
                    skill_names.append("前端开发")
                elif skill_type == "data_engineering":
                    skill_names.append("数据工程")
                elif skill_type == "cloud_devops":
                    skill_names.append("云原生/DevOps")
        
        if skill_names:
            skill_analysis = f"候选人主要技能方向：{', '.join(skill_names)}，技能匹配度：{top_skills[0][1]}分，符合{refined_position}岗位要求。"
        else:
            skill_analysis = f"候选人技能信息待完善，根据职位要求匹配{refined_position}岗位。"
        
        market_info = f"""
**市场薪资参考：**
- 目标职位：{refined_position}
- 基于伦敦{refined_position}市场薪资调研
- 技能匹配分析：{skill_analysis}
- 数据来源：行业标准参考
"""
    
    # 生成offer信
    current_date = datetime.now().strftime("%Y年%m月%d日")
    entry_date = datetime.now().strftime("%Y年%m月%d日")
    
    offer_letter = f"""
### 候选人面试表现分析

候选人：{candidate_name}
应聘职位：{refined_position}
面试总分：{total_score}分（技术面试{technical_score}分，HR面试{hr_score}分，Boss面试{boss_score}分）

根据面试表现分析，该候选人在技术能力、沟通协作和团队合作方面表现良好，符合岗位要求。

### 市场薪资参考

{market_info}

建议薪资范围为：{salary_range}

### Offer通知信

**[公司名称] 人力资源部**

{current_date}

{candidate_name} 先生/女士：

我们很高兴地通知您，经过三轮面试的全面评估，您已成功通过我们的招聘流程。我们诚挚地邀请您加入我们的团队。

**职位详情：**
- 职位名称：{refined_position}
- 工作地点：伦敦
- 入职时间：{entry_date}（具体时间将另行通知）

**薪资福利：**
- 基础年薪：{suggested_salary}
- 市场参考：基于实时市场数据分析
- 额外福利：包括但不限于医疗保险、养老金、年假等

**面试评估总结：**
- 技术面试评分：{technical_score}/25
- HR面试评分：{hr_score}/25
- Boss面试评分：{boss_score}/25
- 综合评分：{total_score}/25

**评估亮点：**
{interview_scores.get('evaluation_summary', '候选人整体表现良好，符合岗位要求')}

**改进建议：**
"""
    
    improvement_suggestions = interview_scores.get('improvement_suggestions', [])
    for i, suggestion in enumerate(improvement_suggestions, 1):
        offer_letter += f"- {suggestion}\n"
    
    offer_letter += f"""
**下一步流程：**
1. 请在本offer发出后7个工作日内回复是否接受
2. 如接受，我们将安排入职前准备事项
3. 如有疑问，请随时联系HR部门

**联系方式：**
- 邮箱：hr@company.com
- 电话：+44 20 1234 5678

我们期待您的加入，相信您将为团队带来宝贵的贡献！

此致
敬礼

{current_date}
公司名称
HR部门
"""
    
    return offer_letter

def generate_offer_letter(interview_data):
    """同步版本的offer生成函数，用于向后兼容"""
    # 尝试使用实时市场数据
    try:
        # 检查是否已经在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，使用备用方案
            print("已在事件循环中，使用备用方案")
            return generate_offer_letter_fallback(interview_data)
        except RuntimeError:
            # 没有运行中的事件循环，可以创建新的
            pass
        
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(generate_offer_letter_with_market_data(interview_data))
        finally:
            loop.close()
    except Exception as e:
        print(f"使用市场数据生成offer失败，使用备用方案: {e}")
        # 如果异步版本失败，使用原来的逻辑
        return generate_offer_letter_fallback(interview_data)

def generate_offer_letter_fallback(interview_data):
    """原来的offer生成逻辑，作为备用"""
    if not interview_data:
        return "无法获取面试结果数据"
    
    # 提取面试信息
    interview_scores = interview_data.get("interview_scores", {})
    candidate_info = interview_data.get("candidate_profile", {})
    
    total_score = interview_scores.get("overall_score", 0)
    technical_score = interview_scores.get("technical_score", 0)
    hr_score = interview_scores.get("hr_score", 0)
    boss_score = interview_scores.get("boss_score", 0)
    
    candidate_name = candidate_info.get("name", "候选人")
    if candidate_name == "未知":
        candidate_name = "候选人"
        
    target_position = candidate_info.get("target_position", "Python开发工程师")  
    if target_position == "未知" or not target_position:
        # 如果职位信息缺失，尝试从候选人技能推断
        candidate_skills = candidate_info.get("technical_skills", [])
        if candidate_skills and any("大模型" in skill or "LLM" in skill or "算法" in skill for skill in candidate_skills):
            target_position = "大模型算法工程师"
        else:
            target_position = "Python开发工程师"
    
    # 根据候选人信息动态调整职位描述
    candidate_skills = candidate_info.get("technical_skills", [])
    candidate_projects = candidate_info.get("key_projects", [])
    
    # 分析候选人技能和项目，确定更精确的职位定位
    ai_related_keywords = ["大模型", "LLM", "LoRA", "微调", "深度学习", "机器学习", "AI", "人工智能", "NLP", "自然语言处理", "计算机视觉", "推荐算法", "向量数据库", "FAISS", "Milvus", "LangChain", "RAG", "Prompt Engineering"]
    backend_keywords = ["Django", "Flask", "FastAPI", "MySQL", "PostgreSQL", "Redis", "Docker", "微服务", "高并发", "API", "后端"]
    
    # 判断候选人主要方向
    ai_skill_count = sum(1 for skill in candidate_skills if any(keyword in skill for keyword in ai_related_keywords))
    backend_skill_count = sum(1 for skill in candidate_skills if any(keyword in skill for keyword in backend_keywords))
    
    # 根据技能分布调整职位描述
    if ai_skill_count > backend_skill_count:
        # AI/算法方向
        if "大模型" in target_position or "LLM" in target_position:
            refined_position = "大模型算法工程师"
        elif "算法" in target_position:
            refined_position = "算法工程师"
        elif "机器学习" in target_position or "AI" in target_position:
            refined_position = "机器学习工程师"
        else:
            refined_position = target_position
    else:
        # 传统开发方向
        refined_position = target_position
    
    # 根据职位类型和分数确定薪资范围
    def get_salary_by_position_and_score(position, score):
        # 定义不同职位类型的薪资基准
        salary_baselines = {
            "大模型算法工程师": {"base": 75000, "range": 15000},
            "机器学习工程师": {"base": 70000, "range": 12000},
            "AI工程师": {"base": 65000, "range": 10000},
            "数据科学家": {"base": 68000, "range": 12000},
            "数据工程师": {"base": 62000, "range": 10000},
            "云原生后端工程师": {"base": 65000, "range": 10000},
            "DevOps工程师": {"base": 63000, "range": 10000},
            "后端开发工程师": {"base": 58000, "range": 8000},
            "前端开发工程师": {"base": 55000, "range": 8000},
            "全栈开发工程师": {"base": 62000, "range": 10000},
            "移动开发工程师": {"base": 60000, "range": 10000},
            "安全工程师": {"base": 65000, "range": 12000},
            "游戏开发工程师": {"base": 52000, "range": 8000},
            "软件工程师": {"base": 55000, "range": 8000}
        }
        
        # 获取职位基准薪资
        baseline = salary_baselines.get(position, {"base": 55000, "range": 8000})
        base_salary = baseline["base"]
        salary_range = baseline["range"]
        
        # 根据分数调整薪资
        if score >= 78:
            # 高分：基准薪资 + 20%
            adjusted_base = base_salary * 1.2
            range_min = adjusted_base - salary_range * 0.8
            range_max = adjusted_base + salary_range * 0.8
            suggested = adjusted_base
            market_avg = base_salary * 1.1
        elif score >= 70:
            # 中上分：基准薪资 + 10%
            adjusted_base = base_salary * 1.1
            range_min = adjusted_base - salary_range * 0.6
            range_max = adjusted_base + salary_range * 0.6
            suggested = adjusted_base
            market_avg = base_salary * 1.05
        else:
            # 及格分：基准薪资
            adjusted_base = base_salary
            range_min = adjusted_base - salary_range * 0.5
            range_max = adjusted_base + salary_range * 0.5
            suggested = adjusted_base
            market_avg = base_salary * 0.95
        
        return {
            "range": f"{int(range_min):,}-{int(range_max):,}英镑/年",
            "suggested": f"{int(suggested):,}英镑/年",
            "market_avg": f"{int(market_avg):,}英镑/年"
        }
    
    # 获取薪资信息
    salary_info = get_salary_by_position_and_score(refined_position, total_score)
    salary_range = salary_info["range"]
    suggested_salary = salary_info["suggested"]
    market_avg = salary_info["market_avg"]
    
    # 生成offer信
    current_date = datetime.now().strftime("%Y年%m月%d日")
    entry_date = datetime.now().strftime("%Y年%m月%d日")
    
    offer_letter = f"""
### 候选人面试表现分析

候选人：{candidate_name}
应聘职位：{refined_position}
面试总分：{total_score}分（技术面试{technical_score}分，HR面试{hr_score}分，Boss面试{boss_score}分）

根据面试表现分析，该候选人在技术能力、沟通协作和团队合作方面表现良好，符合岗位要求。

### 市场薪资参考

根据伦敦{refined_position}市场薪资调研，结合候选人面试表现，建议薪资范围为：{salary_range}

### Offer通知信

**[公司名称] 人力资源部**

{current_date}

{candidate_name} 先生/女士：

我们很高兴地通知您，经过三轮面试的全面评估，您已成功通过我们的招聘流程。我们诚挚地邀请您加入我们的团队。

**职位详情：**
- 职位名称：{refined_position}
- 工作地点：伦敦
- 入职时间：{entry_date}（具体时间将另行通知）

**薪资福利：**
- 基础年薪：{suggested_salary}
- 市场参考：该职位在伦敦地区的平均薪资约为{market_avg}
- 额外福利：包括但不限于医疗保险、养老金、年假等

**面试评估总结：**
- 技术面试评分：{technical_score}/100
- HR面试评分：{hr_score}/100
- Boss面试评分：{boss_score}/100
- 综合评分：{total_score}/100

**评估亮点：**
{interview_scores.get('evaluation_summary', '候选人整体表现良好，符合岗位要求')}

**改进建议：**
"""
    
    improvement_suggestions = interview_scores.get('improvement_suggestions', [])
    for i, suggestion in enumerate(improvement_suggestions, 1):
        offer_letter += f"- {suggestion}\n"
    
    offer_letter += f"""
**下一步流程：**
1. 请在本offer发出后7个工作日内回复是否接受
2. 如接受，我们将安排入职前准备事项
3. 如有疑问，请随时联系HR部门

**联系方式：**
- 邮箱：hr@company.com
- 电话：+44 20 1234 5678

我们期待您的加入，相信您将为团队带来宝贵的贡献！

此致
敬礼

{current_date}
公司名称
HR部门
"""
    
    return offer_letter

def should_generate_offer(total_score):
    """判断是否应该生成offer（分数>=60）"""
    return total_score >= 60
