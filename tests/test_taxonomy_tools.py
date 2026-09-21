import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.knowledge import DEFAULT_PATH, ROOT, Taxonomy


def cli(*args):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/taxonomy_tool.py'), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8')


@pytest.mark.parametrize('format', ['json', 'csv'])
def test_catalog_roundtrip_preserves_every_field(tmp_path, format):
    exported = tmp_path / f'catalog.{format}'
    restored = tmp_path / 'restored.json'
    result = cli('export', '--output', exported, '--format', format)
    assert result.returncode == 0, result.stderr
    result = cli('import', '--input', exported, '--output', restored, '--format', format)
    assert result.returncode == 0, result.stderr
    assert Taxonomy(restored).data == Taxonomy().data


def test_failed_import_and_existing_output_are_never_overwritten(tmp_path):
    source = tmp_path / 'invalid.json'
    source.write_text('{"version":"2026.09.3","nodes":[]}', encoding='utf-8')
    destination = tmp_path / 'target.json'
    destination.write_text('valuable existing file', encoding='utf-8')
    assert cli('import', '--input', source, '--output', destination).returncode != 0
    assert destination.read_text(encoding='utf-8') == 'valuable existing file'
    assert cli('export', '--output', destination).returncode != 0


def test_migration_is_explicit_dry_run_and_preserves_source(tmp_path):
    source = tmp_path / 'records.json'
    original = {'dataset_version': 'fixture-1', 'records': [{'id': 7, 'taxonomy_version': '2026.09.2',
               'primary_knowledge_ids': ['dp.knapsack.01'], 'secondary_knowledge_ids': [],
               'evidence': {'dp.knapsack.01': 'each item once'}, 'knowledge_confidence': {'dp.knapsack.01': 0.8}}]}
    source.write_text(json.dumps(original), encoding='utf-8')
    mapping = tmp_path / 'mapping.json'
    mapping.write_text(json.dumps({'source_version': '2026.09.2', 'target_version': Taxonomy().version,
                                  'mapping': {'dp.knapsack.01': 'dp.knapsack.01'}}), encoding='utf-8')
    destination = tmp_path / 'migrated.json'
    args = ('migrate', '--input', source, '--mapping', mapping, '--output', destination)
    result = cli(*args)
    assert result.returncode == 0, result.stderr
    assert not destination.exists()
    result = cli(*args, '--apply')
    assert result.returncode == 0, result.stderr
    migrated = json.loads(destination.read_text(encoding='utf-8'))
    assert migrated['records'][0]['taxonomy_version'] == Taxonomy().version
    assert migrated['records'][0]['migration_source'] == original['records'][0]
    assert json.loads(source.read_text(encoding='utf-8')) == original
    assert cli(*args, '--apply').returncode != 0


def test_unmapped_migration_fails_without_output(tmp_path):
    source = tmp_path / 'source.json'
    source.write_text(json.dumps({'records': [{'taxonomy_version': '2026.09.2', 'knowledge_ids': ['dp.knapsack.01']}]}), encoding='utf-8')
    mapping = tmp_path / 'map.json'
    mapping.write_text(json.dumps({'source_version': '2026.09.2', 'target_version': Taxonomy().version, 'mapping': {}}), encoding='utf-8')
    destination = tmp_path / 'out.json'
    assert cli('migrate', '--input', source, '--mapping', mapping, '--output', destination, '--apply').returncode != 0
    assert not destination.exists()
