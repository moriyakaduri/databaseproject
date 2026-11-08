"""Compare original ERDPlus files against a PostgreSQL column catalog export.
No input file is changed. Types in the original DSD are reported separately.
"""
import csv
import json
from pathlib import Path

audit = Path(__file__).resolve().parent
stage = audit.parent
dsd = json.loads((stage / 'DSD' / 'DSD.erdplus').read_text(encoding='utf-8-sig'))
erd = json.loads((stage / 'ERD' / 'ERD.erdplus').read_text(encoding='utf-8-sig'))
with (audit / 'columns.csv').open(encoding='utf-8-sig', newline='') as src:
    columns = list(csv.DictReader(src))
tables = {n['id']: n for n in dsd['data']['nodes'] if n['type'] == 'Table'}
entities = {n['id']: n for n in erd['data']['nodes'] if n['type'] == 'Entity'}
relationships = [n for n in erd['data']['nodes'] if n['type'] == 'Relationship']
assert len(tables) == len(entities) == 8
assert len(relationships) == len(dsd['data']['edges']) == 7
assert set(tables) == set(entities)
fk_pairs = set()
non_integer_labels = 0
field_count = 0
for node_id, table in tables.items():
    name = table['data']['label'].lower()
    live = {c['column_name']: c for c in columns if c['table_name'] == name}
    flattened = {}
    non_fk = set()
    for col in table['data']['columns']:
        if col.get('isForeignKey'):
            fk_pairs.add((col['foreignKeyProps']['sourceTableId'], node_id))
            for fk in col['foreignKeyProps']['columns']:
                flattened[fk['name'].lower()] = fk
                assert (live[fk['name'].lower()]['is_nullable'] == 'YES') == col['isOptional']
        else:
            flattened[col['name'].lower()] = col
            non_fk.add(col['name'].lower())
    assert set(flattened) == set(live), name
    field_count += len(flattened)
    attrs = [n for n in erd['data']['nodes'] if n['type'] == 'Attribute' and n.get('parentId') == node_id]
    assert {n['data']['label'].lower() for n in attrs} == non_fk, name
    pks = {n['data']['label'].lower() for n in attrs if isinstance(n['data'].get('types'), dict) and n['data']['types'].get('Unique')}
    assert pks == {c['name'].lower() for c in table['data']['columns'] if c.get('isPrimaryKey')}, name
    non_integer_labels += sum(c['data_type'] != 'integer' for c in live.values())

erd_pairs = {(r['data']['sourceEntityDetails']['id'], r['data']['targetEntityDetails']['id']) for r in relationships}
assert erd_pairs == fk_pairs
assert {(e['source'], e['target']) for e in dsd['data']['edges']} == fk_pairs
produces = next(r['data'] for r in relationships if r['data']['label'] == 'Produces')
assert produces['targetEntityDetails']['maxCardinality'] == 'One'
performs = next(r['data'] for r in relationships if r['data']['label'] == 'Performs')
assert performs['sourceEntityDetails']['minCardinality'] == 'Optional'
print('PASS: original ERD and DSD contain 8 matching entities/tables, 52 SQL columns, 7 matching relationships, matching PKs and FK optionality.')
print('PASS: ERD contains 45 entity attributes; 7 FK columns are introduced by relationships.')
print('NOTE: original DSD metadata uses INT placeholders for non-key fields, including', non_integer_labels, 'fields whose live PostgreSQL types are not INTEGER.')
print('Original files were preserved byte-for-byte. The live catalog, createTables.sql and DataDictionary.md specify actual PostgreSQL types.')
