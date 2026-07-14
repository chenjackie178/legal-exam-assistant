---
name: legal-exam-assistant
description: 法考知识查询与真题检索助手。当用户提到法考、法律职业资格考试、法考真题、法考知识点、法考备考、法律知识查询、法考题库、法考刷题、考点分析、法考科目、法考复习、司法考试等与法考学习相关的需求时使用此技能。支持按科目/章节/知识点查询知识体系，按条件检索历年真题，统计高频考点，以及法考相关的智能问答和备考建议。
---

# 法考助手

基于2022-2024年法考客观题真题（869道）和18科目四级知识点体系（890个知识点），提供知识查询、真题检索、考点分析和智能问答服务。

## 数据来源

数据文件位于本技能 `data/` 目录下：
- `knowledge_tree.json` — 18科目四级知识点树（科目→章→节→知识点），含重要性和关联法条
- `questions_all.json` — 869道真题（834道2022-2024真题 + 35道示范题），结构化存储
- `stats.json` — 多维统计摘要（年度/科目/题型/难度分布）

## 工具使用

通过 `python main.py <命令>` 调用查询工具，命令如下：

| 命令 | 用途 | 示例 |
|------|------|------|
| `subjects` | 列出所有科目及题量 | `python main.py subjects` |
| `knowledge [科目id] [章id] [节id]` | 逐级查询知识点树 | `python main.py knowledge criminal_law` |
| `search --subject xx --year xx --keyword xx --limit xx` | 检索真题 | `python main.py search --subject civil_law --year 2024` |
| `stats` | 查看统计数据 | `python main.py stats` |
| `analyze [科目id]` | 分析知识点考查频率 | `python main.py analyze` |
| `kp_name <知识点id>` | 查询知识点名称 | `python main.py kp_name cl_ch01_s01_kp01` |

### 科目ID对照表

| ID | 科目 | ID | 科目 |
|----|------|----|------|
| criminal_law | 刑法 | civil_law | 民法 |
| criminal_procedure | 刑事诉讼法 | civil_procedure | 民事诉讼法 |
| jurisprudence | 法理学 | commercial_law | 商法 |
| constitutional_law | 宪法 | economic_law | 经济法 |
| administrative_law | 行政法 | ip_law | 知识产权法 |
| legal_history | 中国法律史 | labor_law | 劳动法 |
| judicial_system | 司法制度 | environmental_law | 环境资源法 |
| public_international_law | 国际法 | private_international_law | 国际私法 |
| international_economic_law | 国际经济法 | xjp法治思想 | 习近平法治思想 |

### 搜索参数

- `--subject <科目ID>`：按科目筛选
- `--year <年份>`：按年份筛选（2022/2023/2024）
- `--question_type <题型>`：single_choice/multi_choice/indefinite_choice
- `--difficulty <难度>`：easy/medium/hard
- `--keyword <关键词>`：在题干和选项中搜索
- `--knowledge_point_id <知识点ID>`：按关联知识点筛选
- `--limit <数量>`：返回数量上限，默认20

## 工作流程

### 1. 知识点查询
用户问到某个知识点或科目时：
1. 先用 `subjects` 确认科目ID
2. 用 `knowledge <科目id>` 查看该科目知识体系
3. 可继续下钻到章、节级别
4. 结合知识点的重要性、关联法条给出解读

### 2. 真题检索
用户想找真题练习或查看某知识点的考题时：
1. 确认用户要查的科目/年份/知识点
2. 用 `search` 命令检索
3. 展示题目时保留完整题干和选项，答案和解析视用户需求展示
4. 如用户说"来几道刑法题"，用 `search --subject criminal_law --limit 5`

### 3. 考点分析
用户问高频考点、备考重点时：
1. 用 `stats` 看整体数据
2. 用 `analyze` 看知识点考查频率
3. 结合数据给出备考建议，指出高分值科目和高频考点

### 4. 智能问答
用户问法考相关问题（概念解释、法条适用、案例分析等）时：
1. 先用 `knowledge` 定位相关知识点，获取知识点描述和关联法条
2. 用 `search --keyword` 找相关真题作为参考
3. 综合知识点信息和真题案例回答用户问题
4. 回答要准确引用法条和知识点，不编造法律依据

## 输出规范

- 展示真题时格式清晰：题目内容 → 选项 → 答案 → 解析
- 引用知识点时注明来源（科目/章/节）
- 涉及法条时列出具体法律名称和条款
- 给备考建议时用数据说话（题目数量、考查频率），不说空话

## 注意事项

- 真题为考生回忆版，部分题干可能不完整
- 回忆版真题的答案和解析可能为空，此时如实告知用户
- 知识点匹配率约43.6%，未匹配的真题通过关键词搜索可补充
- 数据覆盖2022-2024年客观题，不含主观题
