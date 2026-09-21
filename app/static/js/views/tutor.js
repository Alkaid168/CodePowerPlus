/* 代码辅导：把题目、代码与评测结果交给模型，得到分级提示。 */
import { api } from '../api.js';
import { h, mount } from '../dom.js';
import { store } from '../store.js';
import { button, card, errorBox, field, loading, notice } from '../components.js';

const VERDICTS = ['WA', 'TLE', 'MLE', 'RE', 'CE', 'AC'];

export default {
  async render() {
    const configured = Boolean(store.state.health?.model_configured);
    const problem = h('textarea', { rows: 6, placeholder: '题目描述（可以只贴关键部分）' });
    const code = h('textarea', { rows: 10, placeholder: '你的代码' });
    const verdict = h('select', { class: 'input' }, VERDICTS.map((value) => h('option', { value }, value)));
    const result = h('div', { class: 'stack' });

    const form = h('form', { class: 'stack' },
      field('题目', problem),
      h('div', { class: 'grid two' }, field('评测结果', verdict), h('div', {})),
      field('代码', code),
      h('div', { class: 'row' }, button('获取分级提示', { iconName: 'message-circle', type: 'submit' })),
      result);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!problem.value.trim() || !code.value.trim()) {
        mount(result, notice('题目和代码都要填。', 'warn'));
        return;
      }
      mount(result, loading('正在生成提示…'));
      try {
        const data = await api.tutorHint({
          problem: problem.value.trim(), code: code.value.trim(), verdict: verdict.value,
        });
        mount(result, data.hint
          ? card({ title: '辅导提示' }, h('pre', { class: 'code' }, data.hint))
          : card({ title: '提示词预览' },
              notice(data.message || '尚未配置模型。', 'warn'),
              h('pre', { class: 'code', style: { marginTop: '10px' } }, data.prompt)));
      } catch (error) {
        mount(result, errorBox(error));
      }
    });

    return h('div', { class: 'stack' },
      configured ? null : notice('未配置模型密钥：这里只返回将要发送给模型的提示词，便于检查内容。', 'warn'),
      card({ title: '代码辅导' },
        h('p', { class: 'hint', style: { marginBottom: '10px' } },
          '提示分三层：先给思考方向，再定位可疑代码，最后给验证思路；默认不直接给完整代码。'),
        form));
  },
};
