"""提交接口：知识证据只能来自已审核分析，客户端不能自带标签。"""


def submit(client, problem_id, verdict='AC', user='u1', **extra):
    return client.post('/api/submissions',
                       json={'user_id': user, 'problem_id': problem_id, 'verdict': verdict} | extra)


def test_submission_uses_approved_analysis_tags(client, approved_problem):
    problem, analysis = approved_problem(primary=('math.number-theory.prime',))
    response = submit(client, problem['id'])
    assert response.status_code == 201, response.text
    body = response.json()
    assert body['knowledge_ids'] == ['math.number-theory.prime']
    assert body['analysis_id'] == analysis['analysis_id']
    assert body['taxonomy_version']
    assert body['warning'] == ''


def test_pending_analysis_is_not_evidence(client, make_problem):
    problem, _ = make_problem()
    body = submit(client, problem['id']).json()
    assert body['knowledge_ids'] == []
    assert body['warning']
    assert body['analysis_id'] is None


def test_client_cannot_supply_tags(client, approved_problem):
    problem, _ = approved_problem()
    response = submit(client, problem['id'], tags=['forged'])
    assert response.status_code == 422
    assert response.json()['code'] == 'invalid_request'


def test_missing_problem_is_404(client):
    assert submit(client, 999).status_code == 404


def test_history_profile_and_ce_rules(client, approved_problem):
    problem, _ = approved_problem(primary=('math.number-theory.prime',))
    for verdict in ('WA', 'AC', 'CE'):
        assert submit(client, problem['id'], verdict).status_code == 201

    listing = client.get('/api/submissions', params={'user_id': 'u1'}).json()
    assert listing['total'] == 3
    assert client.get('/api/submissions').json()['total'] == 3
    assert client.get('/api/submissions', params={'user_id': 'other'}).json()['total'] == 0

    profile = client.get('/api/users/u1/profile').json()
    skill = next(item for item in profile['skills'] if item['knowledge_id'] == 'math.number-theory.prime')
    assert skill['evidence_count'] == 1
    assert 0.5 < skill['mastery'] < 1
    assert profile['submission_count'] == 3
    assert profile['unmapped_submission_count'] == 0


def test_old_version_submissions_are_unmapped(client, make_problem, container):
    problem, analysis = make_problem()
    client.post(f"/api/problems/{problem['id']}/review", json={
        'action': 'approve', 'reviewer': 'tester', 'comment': 'ok',
        'expected_analysis_id': analysis['analysis_id']})
    # 直接写入一条旧版本提交，模拟历史数据。
    container.submissions.add('u1', problem['id'], 'AC', knowledge_ids=['basic.prefix-sum'],
                              taxonomy_version='2020.01.1')
    profile = client.get('/api/users/u1/profile').json()
    assert profile['skill_mastery'] == {}
    assert profile['unmapped_submission_count'] == 1
