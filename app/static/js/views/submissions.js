/* 提交记录：手工登记判题结果，系统自动带上该题已审核分析的标签。 */
import { api } from '../api.js';
import { h, mount } from '../dom.js';
import { navigate } from '../router.js';
import { store } from '../store.js';
import { button, card, emptyState, errorBox, field, formatDate, loading, notice, table, tag, toast, verdictBadge } from '../components.js';

const VERDICTS = ['AC', 'WA', 'TLE', 'MLE', 'RE', 'CE'];

export default {
  async render({ param }) {
    await store.ensureKnowledge(api);
    const names = new Map(store.state.knowledge.map((node) => [node.id, node.name]));
    const problems = (await api.problems({ limit: 200 })).items || [];

    const picker = h('select', { class: 'input' }, problems.map((problem) => h('option', {
      value: String(problem.id), selected: param ? Number(param) === problem.id : false,
    }, `#${problem.id} ${problem.title}`)));
    const verdict = h('select', { class: 'input' }, VERDICTS.map((value) => h('option', { value }, value)));
    const language = h('input', { class: 'input', value: 'cpp', placeholder: '语言' });
    const code = h('textarea', { rows: 6, placeholder: '代码（可选，用于后续辅导）' });
    const result = h('div', {});
    const listHost = h('div', {});

    async function loadList() {
      mount(listHost, loading('读取提交记录…'));
      try {
        const data = await api.submissions({ user_id: store.state.userId, limit: 50 });
        mount(listHost, data.items.length
          ? table(['#', '题目', '结果', '知识证据', '难度', '时间'],
              data.items.map((item) => [
                String(item.id),
                h('button', { class: 'btn link', onClick: () => navigate(`problems/${item.problem_id}`) }, `#${item.problem_id}`),
                verdictBadge(item.verdict),
                item.knowledge_ids.length
                  ? h('span', { class: 'row wrap' }, item.knowledge_ids.map((id) => tag(names.get(id) || id, 'muted')))
                  : h('span', { class: 'hint' }, '无（题目还没有已通过的分析）'),
                item.difficulty ?? '—',
                formatDate(item.created_at),
              ]))
          : emptyState('还没有提交记录。'));
      } catch (error) {
        mount(listHost, errorBox(error, loadList));
      }
    }

    const form = h('form', { class: 'stack' },
      problems.length
        ? h('div', { class: 'grid two' }, field('题目', picker), field('判题结果', verdict))
        : notice('题目库为空，请先录入题目。', 'warn'),
      h('div', { class: 'grid two' }, field('语言', language), h('div', {})),
      field('代码', code),
      h('div', { class: 'row' },
        button('记录提交', { iconName: 'send', type: 'submit', disabled: problems.length === 0 }),
        h('span', { class: 'hint' }, '知识证据来自题目当前已审核的分析，客户端不能自带标签')),
      result);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      try {
        const data = await api.createSubmission({
          user_id: store.state.userId,
          problem_id: Number(picker.value),
          verdict: verdict.value,
          language: language.value.trim() || 'unknown',
          code: code.value,
        });
        mount(result, notice(data.warning || `已记录提交 #${data.id}，知识证据：${data.knowledge_ids.length ? data.knowledge_ids.map((id) => names.get(id) || id).join('、') : '无'}`, data.warning ? 'warn' : 'ok'));
        toast('提交已记录', 'ok');
        loadList();
      } catch (error) {
        mount(result, errorBox(error));
      }
    });

    loadList();
    return h('div', { class: 'stack' },
      card({ title: `记录提交 · ${store.state.userId}` }, form),
      card({ title: '最近提交' }, listHost));
  },
};
