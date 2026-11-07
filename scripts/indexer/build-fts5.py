#!/usr/bin/env python3
"""
Indexer SQLite FTS5 + Entities + Relations untuk Wiki Soeharto.
Membangun index pencarian dari content/*.md dan content/**/*.md.

Batch 3 (audit 7 Nov 2026): dua pass — pass 1 memetakan semua
entity_id/judul/alias ke entity_id kanonikal, pass 2 menyimpan relasi
dengan target_entity = entity_id kanonikal (bukan teks judul mentah),
sehingga traversal multi-hop (get_relations depth>1, relations_between)
tidak putus di tengah jalan. Teks asli target disimpan di kolom
target_label. Target yang tidak punya halaman (mis. konsep yang sudah
digabung ke glosarium) tetap disimpan apa adanya dan dihitung sebagai
unresolved di log.
"""

import os
import sqlite3
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import yaml

REPO = Path(os.environ.get('PAKHARTO_REPO') or '/home/ubuntu/quartz')
CONTENT = REPO / 'content'
_DB_ENV = os.environ.get('PAKHARTO_DB', '')
DB_PATH = Path(_DB_ENV) if _DB_ENV else REPO / 'scripts/indexer/wiki-fts5.db'

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


def build_alias_map(records):
    """Kunci (lowercase): entity_id, title, tiap alias -> entity_id.
    Kunci yang menunjuk ke >1 entity_id dianggap ambigu dan dibuang."""
    amap = {}
    ambiguous = set()
    for r in records:
        eid = r['entity_id']
        if not eid:
            continue
        keys = {eid.lower(), (r['title'] or '').lower()}
        for a in r['aliases']:
            keys.add(str(a).lower())
        for k in keys:
            if not k:
                continue
            if k in amap and amap[k] != eid:
                ambiguous.add(k)
            else:
                amap[k] = eid
    for k in ambiguous:
        amap.pop(k, None)
    return amap, ambiguous


def resolve_target(target, amap):
    """Target relasi/wikilink -> entity_id kanonikal, atau None bila
    tidak ada halaman yang cocok (tetap disimpan sebagai teks)."""
    t = (target or '').strip()
    if not t:
        return None
    key = t.lower()
    if key in amap:
        return amap[key]
    if '/' in t:
        last = t.rsplit('/', 1)[-1].split('#')[0].strip()
        if last.lower() in amap:
            return amap[last.lower()]
    if '#' in t:
        base = t.split('#')[0].strip()
        if base.lower() in amap:
            return amap[base.lower()]
    # Fallback slug: "Kasus Kedung Ombo" -> entity_id kasus-kedung-ombo
    slug = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    if slug in amap:
        return amap[slug]
    return None


def build_index(files):
    # Build atomik (audit 7 Nov 2026): bangun ke DB sementara, verifikasi,
    # lalu tukar dengan os.replace agar MCP tidak pernah membaca DB
    # setengah jadi / hilang bila build gagal di tengah jalan.
    # Journal default (DELETE), bukan WAL, supaya tidak ada file -wal/-shm
    # yang tertinggal saat swap.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = DB_PATH.with_name(DB_PATH.stem + '.tmp.db')
    for suffix in ('', '-wal', '-shm', '-journal'):
        stale = Path(str(tmp_path) + suffix)
        if stale.exists():
            stale.unlink()
    conn = sqlite3.connect(str(tmp_path))
    c = conn.cursor()
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
            target_label TEXT,
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

    # --- Pass 1: baca semua file + bangun peta alias -> entity_id ---
    records = []
    errors = []
    seen_ids = {}
    for f in files:
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
            fm, body = parse_frontmatter(text)
            path = str(f.relative_to(REPO))
            eid = fm.get('entity_id', '') or ''
            if eid:
                if eid in seen_ids:
                    print(f'  PERINGATAN: entity_id duplikat {eid}: {path} vs {seen_ids[eid]}')
                else:
                    seen_ids[eid] = path
            aliases = fm.get('aliases', [])
            if not isinstance(aliases, list):
                aliases = [aliases]
            tags = fm.get('tags', [])
            if not isinstance(tags, list):
                tags = [tags]
            records.append({
                'file': f, 'path': path, 'text': text, 'fm': fm, 'body': body,
                'title': fm.get('title', f.stem) or f.stem,
                'description': fm.get('description', '') or '',
                'entity_type': fm.get('entity_type', '') or '',
                'entity_id': eid,
                'kategori': fm.get('kategori', '') or '',
                'aliases': aliases, 'tags': tags,
                'hash': content_hash(text),
            })
        except Exception as e:
            errors.append(f'{f}: {e}')

    amap, ambiguous = build_alias_map(records)
    if ambiguous:
        print(f'  PERINGATAN: {len(ambiguous)} kunci alias ambigu (dibuang): '
              + ', '.join(sorted(ambiguous)[:10]))

    # --- Pass 2: tulis pages/entities/relations dengan target teresolusi ---
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    resolved = {'frontmatter': 0, 'wikilink': 0}
    unresolved = {'frontmatter': [], 'wikilink': []}

    def insert_relation(src, pred, obj, src_url, kind):
        target_id = resolve_target(obj, amap)
        if target_id:
            resolved[kind] += 1
        else:
            if obj not in unresolved[kind]:
                unresolved[kind].append(obj)
        try:
            c.execute(
                'INSERT OR IGNORE INTO relations '
                '(source_entity,predikat,target_entity,target_label,sumber) '
                'VALUES (?,?,?,?,?)',
                (src, pred, target_id or obj, obj, src_url)
            )
        except Exception:
            pass

    for r in records:
        try:
            c.execute(
                'INSERT INTO pages (path,title,description,body,entity_type,entity_id,kategori,tags,content_hash) VALUES (?,?,?,?,?,?,?,?,?)',
                (r['path'], r['title'], r['description'], r['body'],
                 r['entity_type'], r['entity_id'], r['kategori'],
                 ','.join(str(t) for t in r['tags']), r['hash'])
            )
            if r['entity_id']:
                c.execute(
                    'INSERT OR REPLACE INTO entities (entity_id,entity_type,title,description,path,kategori,aliases,tags,content_hash) VALUES (?,?,?,?,?,?,?,?,?)',
                    (r['entity_id'], r['entity_type'], r['title'],
                     r['description'], r['path'], r['kategori'],
                     ','.join(str(a) for a in r['aliases']),
                     ','.join(str(t) for t in r['tags']), r['hash'])
                )
            rels = r['fm'].get('relasi', [])
            if isinstance(rels, list):
                for rel in rels:
                    if isinstance(rel, dict):
                        src = r['entity_id'] or r['path']
                        pred = rel.get('predikat', '')
                        obj = rel.get('objek', '')
                        src_url = rel.get('sumber', '')
                        if src and pred and obj:
                            insert_relation(src, pred, obj, src_url, 'frontmatter')
            for m in re.finditer(r'\[\[([^\]]+)\]\]', r['body']):
                target = m.group(1).split('|')[0].strip()
                if target:
                    insert_relation(r['entity_id'] or r['title'], 'wikilink',
                                    target, r['path'], 'wikilink')
            count += 1
        except Exception as e:
            errors.append(f"{r['file']}: {e}")

    c.execute('INSERT INTO meta VALUES (?,?)', ('built_at', now))
    c.execute('INSERT INTO meta VALUES (?,?)', ('file_count', str(count)))
    c.execute('INSERT INTO meta VALUES (?,?)',
              ('relations_resolved', str(resolved['frontmatter'] + resolved['wikilink'])))
    c.execute('INSERT INTO meta VALUES (?,?)',
              ('relations_unresolved', str(len(unresolved['frontmatter']) + len(unresolved['wikilink']))))
    conn.commit()
    conn.close()

    # Verifikasi DB sementara sebelum swap: tabel wajib ada, jumlah halaman
    # cocok dengan yang diindeks.
    verify = sqlite3.connect(str(tmp_path))
    vc = verify.cursor()
    tables = {r[0] for r in vc.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert {'pages', 'entities', 'relations', 'meta'} <= tables, \
        f"Tabel hilang di DB sementara: {tables}"
    n_pages = vc.execute('SELECT count(*) FROM pages').fetchone()[0]
    assert n_pages == count and n_pages > 0, \
        f"Jumlah pages di DB ({n_pages}) != file terindeks ({count})"
    verify.close()

    # Bersihkan sidecar WAL lama (dari DB era WAL) lalu tukar atomik.
    for suffix in ('-wal', '-shm', '-journal'):
        stale = Path(str(DB_PATH) + suffix)
        if stale.exists():
            stale.unlink()
    os.replace(tmp_path, DB_PATH)

    print(f"Relasi teresolusi ke entity_id: frontmatter {resolved['frontmatter']}, "
          f"wikilink {resolved['wikilink']}")
    print(f"Target tanpa halaman (tetap teks): frontmatter {len(unresolved['frontmatter'])}, "
          f"wikilink {len(unresolved['wikilink'])}")
    for kind in ('frontmatter', 'wikilink'):
        if unresolved[kind]:
            print(f"  belum teresolusi ({kind}): " + ', '.join(unresolved[kind][:10]))
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
