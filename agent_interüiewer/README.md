# HR Offer Agent 与三角色智能面试系统

## 项目简介

本项目提供一套可直接运行的三角色智能面试系统（技术/HR/Boss）与 HR Offer 生成智能体，支持面试自动化、评分评估、候选人画像提取、结果归档与 Offer 生成。并提供 MCP 服务器接入外部岗位市场薪资数据（Adzuna）。

## 目录结构

```
agent_training/
├── agents/                          # 智能体模块
│   ├── __init__.py
│   ├── hr_offer_agent.py           # HR Offer 生成智能体
│   ├── technical_interviewer.py    # 技术面试官
│   ├── hr_interviewer.py           # HR 面试官
│   ├── boss_interviewer.py         # Boss 面试官
│   ├── candidate_agent.py          # 候选人智能体
│   ├── score_evaluator.py          # 评分评估器
│   └── info_extractor.py           # 信息提取器
│
├── mcp_servers/                     # MCP 服务器
│   └── adzuna_mcp_server.py        # Adzuna API MCP 服务器
│
├── data/                           # 数据
│   └── interview_results/
│       ├── 60plus/                 # 60分以上候选人
│       │   └── [候选人姓名]/
│       │       ├── interview_results_*.json
│       │       └── offer_letter_*.txt
│       └── below60/                # 60分以下候选人
│           └── [候选人姓名]/
│               └── interview_results_*.json
│
├── docs/                           # 文档与导出图片
│   └── flowchart.jpg               # 面试流程图（如已生成）
│
├── smart_interview.py              # 主程序入口
├── smart_interview_annotated.py    # 注释版副本（可选）
├── requirements.txt                # 依赖包
└── README.md                       # 项目文档
```

## 功能特性

- 三角色智能面试流程：技术面试、HR 面试、Boss 面试
- 自动评分与评语：汇总三轮并生成总分与建议
- 候选人信息抽取：从对话中提取画像并智能推断职位
- 结果归档：完整对话、评分、摘要归档为 JSON
- Offer 生成：分数达标自动生成 Offer 文案并保存
- 市场薪资集成（可选）：通过 MCP 服务器接入 Adzuna API

## 业务流程概览

Mermaid 源码如下，可在 Markdown 支持 Mermaid 的环境中渲染：

```mermaid
graph TD
  A[候选人进入流程] --> B[初筛与职位匹配]
  B --> C{是否匹配岗位?}
  C -->|否| Z[进入人才库/结束]
  C -->|是| D[安排面试日程]
  D --> E[技术面试]
  E --> F[HR 面试]
  F --> G[Boss 面试]
  G --> H[汇总评估与评分]
  H --> I{是否达录用阈值(>=60)?}
  I -->|否| J[不通过/进入人才库]
  I -->|待定| K[补充材料/加面]
  I -->|是| L[生成 Offer 文案]
  L --> M[HR 审核并发 Offer]
  M --> N{候选人是否接受?}
  N -->|接受| O[入职流程启动]
  N -->|拒绝| P[归档/加入人才库]
  H --> Q[归档面试档案]
```

若需导出 JPG，可参考下文“文档输出与导出”。

## 安装与配置

### Python 环境

建议使用 Conda：

```bash
# 推荐环境（示例）
conda create -n rag4 python=3.10 -y
conda activate rag4
```

### 依赖安装

```bash
pip install -r requirements.txt
```

### API 配置

- Adzuna API（可选）：
  - App ID: 在 Adzuna 控制台获取
  - App Key: 在 Adzuna 控制台获取
  - API URL: `https://api.adzuna.com/v1/api/jobs/gb/search/1`

- LLM 提供商：请在运行环境中设置密钥，避免写入源码：

```bash
export SILICONFLOW_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

如需本地加载 `.env`，可安装 `python-dotenv` 并在入口中加载（当前 `smart_interview.py` 已内置自动加载）。

#### 快速设置步骤

1) 基于示例创建 `.env` 文件：

```bash
cp env_example.txt .env
```

2) 编辑 `.env` 并填入你的真实密钥与配置（仅示例占位，勿直接使用）：

```
# LLM 提供商
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Adzuna 市场薪资数据
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
ADZUNA_BASE_URL=https://api.adzuna.com/v1/api/jobs/gb/search/1
```

3) 运行（程序会自动读取 `.env`）：

```bash
python smart_interview.py
```

4) 备选方案：直接用环境变量运行（不创建 `.env`）：

```bash
export SILICONFLOW_API_KEY=your_key
export OPENAI_API_KEY=your_key
export ADZUNA_APP_ID=your_adzuna_app_id
export ADZUNA_APP_KEY=your_adzuna_app_key
python smart_interview.py
```

5) 验证是否加载成功（任一其一）：

```bash
python - <<'PY'
import os
print(bool(os.getenv('SILICONFLOW_API_KEY')),
      bool(os.getenv('OPENAI_API_KEY')),
      bool(os.getenv('ADZUNA_APP_ID')),
      bool(os.getenv('ADZUNA_APP_KEY')))
PY
```

#### 安全提示

- 切勿将真实密钥写入源码或提交到仓库。`.env` 已在 `.gitignore` 中忽略。
- 生产部署请使用 CI/CD 或密钥管理服务注入环境变量。
- 不同环境（本地/测试/生产）建议使用独立密钥与 `.env` 文件。

## 快速开始

```bash
python smart_interview.py
```

运行后，程序会：
1. 加载默认候选人画像
2. 创建技术/HR/Boss/候选人四个智能体
3. 依次执行三轮面试
4. 生成评分与总结
5. 保存完整结果至 `data/interview_results/` 下
6. 若总分 >= 60，生成 Offer 到 `60plus/[候选人姓名]/`

## HR Offer Agent 独立使用

```python
from agents.hr_offer_agent import generate_offer_letter

# interview_data 需包含评分与候选人画像
offer = generate_offer_letter(interview_data)
print(offer)
```

## MCP 服务器

启动 Adzuna MCP 服务器（Python 3.10+ 环境）：

```bash
python mcp_servers/adzuna_mcp_server.py
```

客户端可通过 MCP 协议调用以拉取市场薪资数据，为 Offer 论证提供参考。

## 数据与文件

- 面试结果 JSON：`data/interview_results/[60plus|below60]/[候选人姓名]/interview_results_YYYYMMDD_HHMMSS.json`
- Offer 文案 TXT：`data/interview_results/60plus/[候选人姓名]/offer_letter_YYYYMMDD_HHMMSS.txt`

示例：

```
data/interview_results/
├── 60plus/
│   └── 张三/
│       ├── interview_results_20250820_123456.json
│       └── offer_letter_20250820_123456.txt
└── below60/
    └── 王五/
        └── interview_results_20250820_345678.json
```

## 文档输出与导出

如需在本地导出面试流程图：
1. 将 Mermaid 源码保存为 `docs/flowchart.mmd`
2. 使用 `mermaid-cli` 或在线服务渲染为 PNG/SVG
3. 需要 JPG 时，可用 Pillow 将 PNG 转换为 JPG

## 安全与合规

- 不要在仓库中提交明文 API 密钥，请使用环境变量或密钥管理服务
- 面试对话与候选人画像中可能包含个人信息，请遵守数据最小化与留存周期
- 输出文件仅供内部决策参考，必要时进行匿名化与脱敏

## 常见问题

- 评分 JSON 解析失败：系统会自动回退到默认评分，建议检查上下文长度与模型输出格式
- 候选人信息抽取有偏差：系统会保护关键字段并尝试智能职位推断，可在默认画像中补充更准确信息
- Boss 面试不生成建议：请确认前两轮结果已成功产出摘要

## 许可证

本项目使用 MIT 许可证。
