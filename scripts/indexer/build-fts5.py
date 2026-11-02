#!/usr/bin/env python3
"""
Indexer SQLite FTS5 untuk Wiki Soeharto.
Membangun index pencarian dari content/*.md dan content/**/*.md.
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime, timezone

REPO = Path('/home/ubuntu/quartz')
CONTENT = REPO / 'content'
DB_PATH = REPO / 'scripts/indexer/wiki-fts5.db'

SKIP_FILES = {'_index.md', 'index.md'}

FM_RE = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.DOTALL)
FIELD_RE = re.compile(r'^(\w[\w-]*):\s*(.*)$', re.MULTILINE)


def parse_frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    data = {}
    for line in fm_text.splitlines():
        fm = FIELD_RE.match(line)
        if fm:
            k, v = fm.group(1), fm.group(2).strip()
            if v.startswith('[') and v.endswith(']'):
                try:
                    v = eval(v)
                except Exception:
                    pass
            elif v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            data[k] = v
    return data, body


def collect_files():
    return sorted(set(f for f in CONTENT.rglob('*.md') if f.name not in SKIP_FILES))


def build_index(files):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('''
        CREATE VIRTUAL TABLE pages USING fts5(
            path UNINDEXED,
            title,
            description,
            body,
            entity_type UNINDEXED,
            entity_id UNINDEXED,
            kategori UNINDEXED,
            tags UNINDEXED,
            tokenize = 'porter unicode61'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    now = datetime.now(timezone.utc).isoformat()
    count = 0
    errors = []
    for f in files:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
            fm, body = parse_frontmatter(text)
            path = str(f.relative_to(REPO))
            title = fm.get('title', f.stem)
            desc = fm.get('description', '')
            entity_type = fm.get('entity_type', '')
            entity_id = fm.get('entity_id', '')
            kategori = fm.get('kategori', '')
            tags = ','.join(fm.get('tags', [])) if isinstance(fm.get('tags'), list) else str(fm.get('tags', ''))
            c.execute(
                'INSERT INTO pages (path,title,description,body,entity_type,entity_id,kategori,tags) VALUES (?,?,?,?,?,?,?,?)',
                (path, title, desc, body, entity_type, entity_id, kategori, tags)
            )
            count += 1
        except Exception as e:
            errors.append(f'{f}: {e}')

    c.execute('INSERT INTO meta VALUES (?,?)', ('built_at', now))
    c.execute('INSERT INTO meta VALUES (?,?)', ('file_count', str(count)))
    conn.commit()
    conn.close()
    return count, errors


def main():
    print('Mengumpulkan file markdown...')
    files = collect_files()
    print(f'Ditemukan {len(files)} file')
    print('Membangun index FTS5...')
    count, errors = build_index(files)
    print(f'Index selesai: {count} file masuk, {len(errors)} error')
    if errors:
        for e in errors[:10]:
            print(f'  ERROR: {e}')
    print(f'DB: {DB_PATH}')


if __name__ == '__main__':
    main()
