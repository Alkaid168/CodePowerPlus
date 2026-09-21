/* 题目分析：调用模型分析新题，或手工标注/纠正已有题目。 */
import { api } from '../api.js';
import { h, mount } from '../dom.js';
import { store } from '../store.js';
import { button, card, errorBox, field, loading, notice, statusBadge, toast } from '../components.js';
import { createTagEditor } from '../tagEditor.js';

export default {
  async render({ param }) {
    const problems = await api.problems({ limit: 200 });
    const options = problems.items || [];
    const initialId = param ? Number(param) : (options[0] ? options[0].id : null);
    return h('div', { class: 'stack' }, modelCard(), await manualCard(options, initialId));
  },
};

function modelCard() {
  const title = h('input', { class: 'input', placeholder: '题目名称（可留空，模型会给出标题）' });
  const description = h('textarea', { rows: 8, placeholder: '粘贴题面：输入、输出与数据范围' });
  const source = h('input', { class: 'input', placeholder: '来源（可选，例如 Codeforces 1234A）' });
  const result = h('div', {});
  const configured = Boolean(store.state.health?.model_configured);
  const form = h('form', { class: 'stack' },
    field('题目名称', title),
    field('题面', description),
    field('来源', source),
    h('div', { class: 'row' },
      button('调用模型分析并保存', { iconName: 'sparkles', type: 'submit', disabled: !configured }),
      h('span', { class: 'hint' }, configured ? '模型输出会自动做标签与置信度校验' : '未配置 DEEPSEEK_API_KEY，暂不可用')),
    result);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!description.value.trim()) {
      mount(result, notice('请先填写题面。', 'warn'));
      return;
    }
    mount(result, loading('模型分析中，通常需要十几秒…'));
    try {
      const data = await api.analyzeNewProblem({
        title: title.value.trim() || '未命名题目',
        description: description.value.trim(),
        source: source.value.trim(),
      });
      mount(result, notice(`已保存题目 #${data.problem.id}，分析 #${data.analysis.analysis_id} 待审核。`, 'ok'));
      toast('模型分析已保存，等待人工审核', 'ok');
    } catch (error) {
      mount(result, errorBox(error));
    }
  });
  return card({ title: '用模型分析新题目' }, form);
}

async function manualCard(options, initialId) {
  const picker = h('select', { class: 'input' }, options.length
    ? options.map((problem) => h('option', { value: String(problem.id), selected: problem.id === initialId },
        `#${problem.id} ${problem.title}`))
    : h('option', { value: '' }, '还没有题目，请先用模型分析录入'));
  const current = h('div', {});
  const difficulty = h('input', { class: 'input', type: 'number', min: '1', max: '5', step: '1', value: '2' });
  const confidence = h('input', { class: 'input', type: 'number', min: '0', max: '1', step: '0.05', value: '0.8' });
  const reason = h('input', { class: 'input', placeholder: '难度判断理由（可选）' });
  const idea = h('textarea', { rows: 3, placeholder: '解题思路（可选）' });
  const editor = await createTagEditor([]);
  const result = h('div', {});
  const isPlaceholder = Boolean(initialId) && options.length === 0;

  async function loadCurrent() {
    const problemId = Number(picker.value);
    if (!problemId) return;
    mount(current, loading('读取当前分析…'));
    try {
      const problem = await api.problem(problemId);
      const analysis = problem.analysis;
      if (analysis) {
        editor.reset([
          ...analysis.primary_knowledge_ids.map((id) => ({ id, role: 'primary',
            evidence: analysis.evidence?.[id] || '', confidence: analysis.knowledge_confidence?.[id] ?? 0.8 })),
          ...analysis.secondary_knowledge_ids.map((id) => ({ id, role: 'secondary',
            evidence: analysis.evidence?.[id] || '', confidence: analysis.knowledge_confidence?.[id] ?? 0.8 })),
        ]);
        difficulty.value = String(analysis.difficulty ?? 2);
        confidence.value = String(analysis.confidence ?? 0.8);
        reason.value = analysis.difficulty_reason || '';
        idea.value = analysis.solution_idea || '';
        mount(current, h('div', { class: 'notice' },
          `当前分析 #${analysis.analysis_id}（`, statusBadge(analysis.review_status),
          '）。保存会生成一条新的待审核版本，旧版本与审核记录都会保留。'));
      } else {
        editor.reset([]);
        mount(current, notice('这道题还没有分析，保存即创建第一版。', 'warn'));
      }
    } catch (error) {
      mount(current, errorBox(error, loadCurrent));
    }
  }

  picker.addEventListener('change', loadCurrent);
  const form = h('form', { class: 'stack' },
    options.length ? field('选择题目', picker) : notice('还没有可标注的题目，请先用模型分析录入。', 'warn'),
    current,
    editor.node,
    h('div', { class: 'grid two' },
      field('题目难度（1–5）', difficulty),
      field('整体置信度（0–1）', confidence)),
    field('难度判断理由', reason),
    field('解题思路', idea),
    h('div', { class: 'row' }, button('保存标注（进入待审核）', { iconName: 'save', type: 'submit', disabled: isPlaceholder })),
    result);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const problemId = Number(picker.value);
    if (!problemId) return;
    try {
      const payload = editor.read();
      const data = await api.saveAnalysis(problemId, {
        difficulty: Number(difficulty.value),
        confidence: Number(confidence.value),
        difficulty_reason: reason.value.trim(),
        solution_idea: idea.value.trim(),
        taxonomy_version: store.state.knowledgeVersion,
        ...payload,
      });
      mount(result, notice(`已保存分析 #${data.analysis.analysis_id}（待审核）。`, 'ok'));
      toast('标注已保存，等待人工审核', 'ok');
    } catch (error) {
      mount(result, errorBox(error));
    }
  });

  if (!isPlaceholder) await loadCurrent();
  return card({ title: '手工标注或纠正' }, form);
}
