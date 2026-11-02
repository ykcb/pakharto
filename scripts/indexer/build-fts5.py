#!/usr/bin/env python3
"""
Indexer SQLite FTS5 + Entities + Relations untuk Wiki Soeharto.
Membangun index pencarian dari content/*.md dan content/**/*.md.
"""

import sqlite3
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import yaml

REPO = Path('/home/ubuntu/quartz')
CONTENT = REPO / 'content'
DB_PATH = REPO / 'scripts/indexer/wiki-fts5.db'

SKIP_FILES = {'_index.md', 'index.md'}


def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    fm_text, body = m.group(1), m.group(2)
    try:
        data = yaml.safe_load(fm_text) or {}
    except Exception:
        data = {}
    return data, body


def collect_files():
    return sorted(set(f for f in CONTENT.rglob('*.md') if f.name not in SKIP_FILES))


def content_hash(text):
    return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()


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
            content_hash UNINDEXED,
            tokenize = 'porter unicode61'
        )
    ''')
    c.execute('''
        CREATE TABLE entities (
            entity_id TEXT PRIMARY KEY,
            entity_type TEXT,
            title TEXT,
            description TEXT,
            path TEXT UNIQUE,
            kategori TEXT,
            aliases TEXT,
            tags TEXT,
            content_hash TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_entity TEXT,
            predikat TEXT,
            target_entity TEXT,
            sumber TEXT,
            UNIQUE(source_entity, predikat, target_entity, sumber)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_relations_predikat ON relations(predikat)')

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
            aliases = fm.get('aliases', [])
            tags = fm.get('tags', [])
            chash = content_hash(text)

            # FTS5
            c.execute(
                'INSERT INTO pages (path,title,description,body,entity_type,entity_id,kategori,tags,content_hash) VALUES (?,?,?,?,?,?,?,?,?)',
                (path, title, desc, body, entity_type, entity_id, kategori,
                 ','.join(str(t) for t in tags) if isinstance(tags, list) else str(tags),
                 chash)
            )

            # Entities
            if entity_id:
                c.execute(
                    'INSERT OR REPLACE INTO entities (entity_id,entity_type,title,description,path,kategori,aliases,tags,content_hash) VALUES (?,?,?,?,?,?,?,?,?)',
                    (entity_id, entity_type, title, desc, path, kategori,
                     ','.join(str(a) for a in aliases) if isinstance(aliases, list) else str(aliases),
                     ','.join(str(t) for t in tags) if isinstance(tags, list) else str(tags),
                     chash)
                )

            # Relations from frontmatter relasi[]
            rels = fm.get('relasi', [])
            if isinstance(rels, list):
                for r in rels:
                    if isinstance(r, dict):
                        src = entity_id or path
                        pred = r.get('predikat', '')
                        obj = r.get('objek', '')
                        src_url = r.get('sumber', '')
                        if src and pred and obj:
                            try:
                                c.execute(
                                    'INSERT OR IGNORE INTO relations (source_entity,predikat,target_entity,sumber) VALUES (?,?,?,?)',
                                    (src, pred, obj, src_url)
                                )
                            except Exception:
                                pass

            # Also extract relations from wikilinks in body: [[Target]]
            for m in re.finditer(r'\[\[([^\]]+)\]\]', body):
                target = m.group(1).split('|')[0].strip()
                if target:
                    try:
                        c.execute(
                            'INSERT OR IGNORE INTO relations (source_entity,predikat,target_entity,sumber) VALUES (?,?,?,?)',
                            (entity_id or title, 'wikilink', target, path)
                        )
                    except Exception:
                        pass

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
    print('Membangun index FTS5 + entities + relations...')
    count, errors = build_index(files)
    print(f'Index selesai: {count} file masuk, {len(errors)} error')
    if errors:
        for e in errors[:10]:
            print(f'  ERROR: {e}')
    print(f'DB: {DB_PATH}')


if __name__ == '__main__':
    main()
