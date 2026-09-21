/* 能力画像：按知识标签汇总做题证据，并说明汇总口径。 */
import { api } from '../api.js';
import { h } from '../dom.js';
import { navigate } from '../router.js';
import { store } from '../store.js';
import { button, card, emptyState, notice, progress, table, tile } from '../components.js';

export default {
  async render() {
    const data = await api.profile(store.state.userId);
    const skills = (data.skills || [])
      .filter((skill) => skill.level > 1 && skill.evidence_count > 0)
      .sort((a, b) => (a.mastery ?? 1) - (b.mastery ?? 1));

    return h('div', { class: 'stack' },
      h('div', { class: 'grid three' },
        tile('提交记录', data.submission_count, `算法版本 ${data.algorithm_version}`),
        tile('有证据的知识点', skills.length, `知识体系 ${data.taxonomy_version}`),
        tile('未纳入证据的提交', data.unmapped_submission_count, '未审核、旧版本或不含标签')),
      notice(data.explanation || '掌握度是启发式估计，不是考试成绩。'),
      card({ title: '知识点掌握度' },
        skills.length
          ? table(['层级', '知识点', '掌握度', '题目证据', '直接证据', '置信度', ''],
              skills.map((skill) => [
                `L${skill.level}`,
                h('button', { class: 'btn link', onClick: () => navigate(`knowledge/${encodeURIComponent(skill.knowledge_id)}`) }, skill.name),
                progress(skill.mastery),
                String(skill.evidence_count),
                String(skill.direct_evidence_count),
                `${Math.round(skill.confidence * 100)}%`,
                button('规划路径', { variant: 'secondary', small: true, iconName: 'route',
                  onClick: () => navigate(`path/${encodeURIComponent(skill.knowledge_id)}`) }),
              ]))
          : emptyState('还没有可用于画像的证据。先审核题目分析，再用「提交记录」登记结果。',
              button('去记录提交', { iconName: 'send', onClick: () => navigate('submissions') })),
        h('p', { class: 'hint', style: { marginTop: '10px' } },
          '父节点的分数由子树证据汇总而来，只用于看整体方向；直接证据数表示确实被标在这一个节点上的题目数。')));
  },
};
