# 面试系统问题分析流程图

```mermaid
flowchart TD
    A[开始: smart_interview.py] --> B[初始化候选人信息]
    B --> C[调用 get_default_candidate_info()]
    C --> D[设置默认信息: 林义超, 大模型算法工程师]
    
    D --> E[conduct_full_interview 开始]
    E --> F[技术面试]
    F --> G[HR面试]
    G --> H[Boss面试]
    
    H --> I[extract_candidate_info 被调用]
    I --> J[info_extractor 分析对话内容]
    J --> K{info_extractor 返回什么?}
    
    K -->|返回"未知"或无效信息| L[保留原始信息]
    K -->|返回有效信息| M[更新候选人信息]
    
    L --> N[检查 target_position]
    M --> N
    
    N --> O{target_position 是什么?}
    O -->|"未知"或空| P[调用 _infer_position_from_skills_and_projects]
    O -->|有明确值| Q[保留原始职位]
    
    P --> R[分析技能和项目]
    R --> S[计算类别得分]
    S --> T[选择最高得分类别]
    
    T --> U{最高得分类别?}
    U -->|ai_ml| V[返回: 大模型算法工程师]
    U -->|backend_dev| W[返回: Python开发工程师]
    U -->|其他| X[返回对应职位]
    
    V --> Y[设置 candidate_info.target_position]
    W --> Y
    X --> Y
    Q --> Y
    
    Y --> Z[generate_offer_if_qualified]
    Z --> AA[调用 generate_offer_letter]
    AA --> BB[hr_offer_agent.py 处理]
    
    BB --> CC[determine_position 函数]
    CC --> DD[分析技能和项目]
    DD --> EE[计算 refined_position]
    
    EE --> FF{refined_position 是什么?}
    FF -->|大模型算法工程师| GG[使用AI/ML职位]
    FF -->|Python开发工程师| HH[使用后端职位]
    FF -->|其他| II[使用对应职位]
    
    GG --> JJ[生成offer letter]
    HH --> JJ
    II --> JJ
    
    JJ --> KK[保存到文件]
    KK --> LL[结束]

    style A fill:#e1f5fe
    style LL fill:#c8e6c9
    style W fill:#ffcdd2
    style HH fill:#ffcdd2
    style V fill:#c8e6c9
    style GG fill:#c8e6c9
```

## 问题分析

### 当前问题
Offer letter 中显示 "Python开发工程师" 而不是 "大模型算法工程师"

### 可能的原因

1. **技能分析权重问题**
   - 候选人的技能中既包含AI/ML技能，也包含后端开发技能
   - `_infer_position_from_skills_and_projects` 函数可能错误地将候选人归类为 `backend_dev` 而不是 `ai_ml`

2. **技能关键词匹配问题**
   - AI/ML关键词权重可能不够高
   - 后端开发关键词匹配过多

3. **职位推断逻辑问题**
   - 在 `hr_offer_agent.py` 的 `determine_position` 函数中可能存在类似问题

### 调试建议

1. **检查技能分类得分**
   ```python
   # 在 _infer_position_from_skills_and_projects 中添加调试输出
   print("=== 职位推断调试信息 ===")
   for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
       print(f"{category}: {score}")
   ```

2. **检查候选人技能列表**
   ```python
   # 在 extract_candidate_info 中输出技能信息
   print(f"候选人技能: {self.candidate_info.get('technical_skills', [])}")
   print(f"候选人项目: {self.candidate_info.get('key_projects', [])}")
   ```

3. **检查职位推断结果**
   ```python
   # 在职位推断后输出结果
   print(f"推断的职位: {self.candidate_info.get('target_position')}")
   ```

### 解决方案

1. **调整技能权重**
   - 增加AI/ML相关技能的权重
   - 减少后端开发技能的权重

2. **优化关键词匹配**
   - 添加更多AI/ML相关关键词
   - 确保"大模型"、"LLM"、"LoRA"等关键词被正确识别

3. **改进职位推断逻辑**
   - 优先考虑AI/ML技能
   - 当检测到大模型相关技能时，强制返回AI/ML职位
