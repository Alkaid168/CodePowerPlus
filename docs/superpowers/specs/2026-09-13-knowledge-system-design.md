# 知识体系与学习闭环设计

用户已授权本轮完成全部十一项范围。沿用当前 FastAPI + SQLite + 原生前端，不依赖学校 OJ，不引入图数据库。

## 领域边界

知识分类只保留 L1 领域、L2 节点与 L3 知识点，L2 既可以是分支，也可以本身就是知识点（数学 → 快速幂）。节点只保存 id、name、level、parent_id。题目难度仍为 1—5，由题目分析给出，与知识节点无关。目录结构参考 OI Wiki 栏目，未经教师审核，不能声称专家认可或 OI Wiki 官方目录。

2026.09.6 起节点不再有难度、典型算法、学习目标、例子与前置关系：知识体系是题目标签词表，只回答“这道题考什么”；2026.09.7 给 342 个叶子知识点补了一段 summary（50–200 字介绍），只用于界面展示，不参与标注。标注规则保持不变——只能选 L2/L3，同一 L2 分支最多一个主标签，不同时选祖先与后代。目录覆盖基础算法、搜索、DP、字符串、数学、数据结构、图论、计算几何与杂项，更冷门专题按题目需求逐步补充。

## 数据与人工审核

分析包含非空 primary_knowledge_ids、secondary_knowledge_ids、evidence（每个 ID 的非空解释）、knowledge_confidence（每个 ID 的 0..1 分数）、taxonomy_version、difficulty 1..5、confidence、model_name、prompt_version。模型只选 active L2/L3；同一路径不同时选祖先/后代，主节点在同一 L2 分支最多一个。服务端固定当前版本和模型溯源，拒绝未知或空 ID，不相信模型自行声称版本。

分析以不可变 revision 保存，状态 pending/approved/rejected；人工纠正新增 revision，审核另存 append-only audit（reviewer、时间、动作、理由、原 revision、新 revision），并以 expected_analysis_id 防止覆盖陈旧审核。用户勾选确认后才能进入画像和推荐。旧数据保留，不从自由标签默默猜 ID；标为 legacy，重新分析/审核即可恢复使用。

提交由题目当前 approved 分析推导知识证据，忽略客户端自由标签；保存知识 ID、知识体系版本、分析 revision、代码、语言、判题结果和时间。尚无 approved 分析时允许记录代码，但知识证据为空且返回明确提示。CE 不作为算法知识错误；相同题目的多次尝试只按最后一次算法结果计入画像，并保留实际尝试次数。

能力按知识点输出 mastery、evidence_count、confidence；无证据为 unknown，不宣称掌握。L1/L2 汇总去重后的题目证据，不能把父节点能力自动灌给所有孩子。推荐仅使用当前版本 approved 题目，排除已 AC，结合薄弱项、适合难度和前置掌握情况；候选保留分项得分和理由。学习路径先补未掌握前置，再学目标，可返回暂无对应题目的知识学习步骤。

## 共享接口契约

Taxonomy(path=默认绝对数据路径) 提供 data/version/nodes、validate、get(id)、children(parent_id=None)、leaves()、tree()、search(q, level=None)、allowed(ids)、describe()、ancestors(id)、branch(id)、validate_assignment(primary, secondary, evidence, knowledge_confidence=None)。validate_assignment 返回 None 或抛 TaxonomyError；若 confidence 为 None 则由调用方单独校验。类加载用真实 JSON Schema 校验，并检查 ID 唯一、层级连续、父节点存在，以及每个叶子知识点都带 20–400 字的 summary；allowed 只接受 L2/L3。

HTTP：
- GET /api/knowledge/tree → {version,tree}; GET /api/knowledge/search?q=&level= → {version,items}; GET /api/knowledge/{id} → 节点 + ancestors 节点数组 + children 节点数组。
- GET/POST /api/problems；创建字段 title,description,source 可选。GET /api/problems/{id} → 题目 + analysis（包含 analysis_id,review_status,primary_knowledge_ids,secondary_knowledge_ids,evidence,knowledge_confidence,taxonomy_version,difficulty,confidence）。
- POST /api/problems/analyze 支持 title,description,source；POST /api/problems/{id}/analyze 重新分析已有题目。模型缺失 503，不产生半成品。
- POST /api/problems/{id}/analyses 手工分析，字段与分析相同（模型版本由后端标记 manual），允许无模型完成流程，初始 pending。
- GET /api/reviews?status=pending → {items:题目含 analysis}; POST /api/problems/{id}/review → {action:approve|reject,reviewer,comment,expected_analysis_id,correction?:完整分析字段}; GET /api/problems/{id}/reviews → {items}。
- POST /api/submissions 字段 user_id,problem_id,verdict,code,language；GET /api/submissions?user_id= → {items}。
- GET /api/users/{user_id}/profile → {user_id,submission_count,skill_mastery:{id:number},skills:[{knowledge_id,name,level,mastery:number|null,evidence_count,confidence}],taxonomy_version,unmapped_submission_count}。
- GET /api/users/{user_id}/recommendations → {user_id,taxonomy_version,recommendations:[题目 + recommendation_score,reasons:string[],target_knowledge_ids:string[],score_breakdown:object]}。
- GET /api/users/{user_id}/learning-path?target_id= → {user_id,taxonomy_version,steps:[{knowledge_id,name,level,reason,mastery:number|null,problem_ids:number[]}]}；路径就是目标在知识树上的层级（领域 → 分支 → 知识点）。
- 保留原 /api/tutor/hint；辅导增强不超出本轮知识体系展示范围。

## 工具与实验

taxonomy_tool.py 支持 validate/export/import/migrate。JSON/CSV 导出导入保留全部节点字段，严格验证后原子写入；版本迁移提供显式 old->new 映射、dry-run 默认、目标版本校验、未映射失败，不静默删除 ID。源数据/原分析不可改写。迁移新建目标输出，当前应用版本切换需要重启并保留旧版本文件。

标注集使用明确 synthetic/authored_fixture 标记，至少 12 个跨领域题目、正负例和模拟学习者历史。评估支持标签 precision/recall/F1、难度 MAE；推荐比较 baseline 与图前置感知方法，报告 hit@k/MRR/coverage/prerequisite violations。实验使用本地输入与固定 seed，不自动调用付费 API；报告样本数、数据集版本、算法版本和局限。

## 验收

加载非法知识体系失败；分析拒绝不存在知识、错误版本、无证据；审核可追踪且防陈旧提交；学习流程在无模型时通过手工标注可完成；数据迁移/导入失败不改变输出；全部测试使用隔离数据库；浏览器验证知识树、解释、审核、画像、路径；实验可一条命令生成 JSON/Markdown 报告。Docker 包含知识文件并使用数据卷，README 清晰说明本地单用户边界。
