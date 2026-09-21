/* 学习路径：选择一个知识点，按知识树层级给出顺序与配套题目。 */
import { api } from '../api.js';
import { h, mount } from '../dom.js';
import { navigate } from '../router.js';
import { store } from '../store.js';
import { button, card, emptyState, errorBox, loading, notice, progress } from '../components.js';

export default {
  async render({ param }) {
    const knowledge = await store.ensureKnowledge(api);
    const selectable = knowledge.filter((node) => node.level > 1);
    const picker = h('select', { class: 'input' }, [
      h('option', { value: '' }, '按当前薄弱点自动选择'),
      ...selectable.map((node) => h('option', { value: node.id, selected: param === node.id },
        `${node.name} · ${node.id}`)),
    ]);
    const result = h('div', { class: 'stack' });

    async function generate() {
      mount(result, loading('生成路径…'));
      try {
        const data = await api.learningPath(store.state.userId, picker.value || undefined);
        mount(result, data.steps.length
          ? h('div', { class: 'stack' }, data.steps.map((step, index) => h('div', { class: 'list-item' },
              h('div', { class: 'row wrap' },
                h('span', { class: 'badge info' }, `${index + 1}`),
                h('button', { class: 'btn link', onClick: () => navigate(`knowledge/${encodeURIComponent(step.knowledge_id)}`) }, step.name),
                h('span', { class: 'tag teal' }, `L${step.level}`),
                h('span', { class: 'hint' }, step.reason),
                h('span', { class: 'spacer' }),
                step.problem_ids.length
                  ? h('span', { class: 'row wrap' }, step.problem_ids.map((id) =>
                      button(`练习 #${id}`, { variant: 'secondary', small: true, onClick: () => navigate(`problems/${id}`) })))
                  : h('span', { class: 'hint' }, '暂无配套题目')),
              h('div', { style: { marginTop: '8px', maxWidth: '320px' } }, progress(step.mastery)))))
          : notice('还没有足够的已审核题目来生成路径。先分析并审核几道题，或直接选一个知识点。', 'warn'));
      } catch (error) {
        mount(result, errorBox(error, generate));
      }
    }

    const form = h('form', { class: 'inline-form' },
      h('div', { style: { flex: '2' } }, h('label', { class: 'field-label' }, '目标知识点（留空 = 自动选最薄弱处）'), picker),
      button('生成路径', { iconName: 'route', type: 'submit' }));
    form.addEventListener('submit', (event) => { event.preventDefault(); generate(); });

    if (param && !selectable.some((node) => node.id === param)) {
      mount(result, notice(`知识点 ${param} 不存在或不是 L2/L3 标签。`, 'warn'));
    } else {
      generate();
    }

    return h('div', { class: 'stack' },
      card({ title: `学习路径 · ${store.state.userId}` }, form),
      result);
  },
};
