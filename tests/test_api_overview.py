"""总览接口：计数与个人薄弱知识点。"""


def test_overview_counts_and_weakest_knowledge(client, approved_problem, make_problem, version):
    approved, _ = approved_problem(title='已审核', primary=('basic.prefix-sum',))
    make_problem(title='待审核', primary=('string.kmp',))
    client.post('/api/submissions', json={'user_id': 'u1', 'problem_id': approved['id'], 'verdict': 'WA'})

    data = client.get('/api/overview', params={'user_id': 'u1'}).json()
    assert data['app_version'] and data['taxonomy_version'] == version
    assert data['problems'] == 2
    assert data['analyses'] == 2
    assert data['pending_reviews'] == 1
    assert data['approved_analyses'] == 1
    assert data['submissions'] == 1
    assert data['learners'] == 1
    assert data['knowledge_nodes'] >= 330
    assert data['model_configured'] is False
    names = [item['name'] for item in data['weakest_knowledge']]
    assert '前缀和' in names


def test_overview_without_user_has_no_weakest_list(client):
    data = client.get('/api/overview').json()
    assert data['problems'] == 0
    assert data['weakest_knowledge'] == []
