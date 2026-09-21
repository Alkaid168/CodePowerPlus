"""学习者接口：画像、推荐与学习路径。"""


def test_profile_recommendations_and_learning_path(client, approved_problem):
    solved, _ = approved_problem(title='已解题', primary=('basic.prefix-sum',))
    target, _ = approved_problem(title='待练题', primary=('math.number-theory.prime',))
    client.post('/api/submissions', json={'user_id': 'u1', 'problem_id': solved['id'], 'verdict': 'AC'})

    profile = client.get('/api/users/u1/profile').json()
    assert profile['submission_count'] == 1
    assert profile['skill_mastery']['basic.prefix-sum'] > 0.5
    assert profile['algorithm_version']

    recommendations = client.get('/api/users/u1/recommendations').json()
    assert recommendations['taxonomy_version']
    assert [item['problem_id'] for item in recommendations['recommendations']] == [target['id']]
    first = recommendations['recommendations'][0]
    assert first['target_knowledge_ids'] == ['math.number-theory.prime']
    assert first['score_breakdown']['weakness'] >= 0

    path = client.get('/api/users/u1/learning-path',
                      params={'target_id': 'math.number-theory.prime'}).json()
    assert path['target_id'] == 'math.number-theory.prime'
    assert [step['knowledge_id'] for step in path['steps']] == ['math', 'math.number-theory',
                                                               'math.number-theory.prime']
    assert path['steps'][-1]['problem_ids'] == [target['id']]


def test_learning_path_rejects_l1_target(client):
    response = client.get('/api/users/u1/learning-path', params={'target_id': 'math'})
    assert response.status_code == 422
    assert response.json()['code'] == 'invalid_input'


def test_empty_profile_still_lists_knowledge_nodes(client):
    profile = client.get('/api/users/ghost/profile').json()
    assert profile['submission_count'] == 0
    assert profile['skill_mastery'] == {}
    assert len(profile['skills']) >= 330
    assert all(skill['mastery'] is None for skill in profile['skills'])


def test_recommendations_ignore_pending_analysis(client, make_problem):
    make_problem(title='未审核', primary=('basic.prefix-sum',))
    assert client.get('/api/users/u1/recommendations').json()['recommendations'] == []
