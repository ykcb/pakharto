#!/usr/bin/env python3
"""
WikiQuery: Engine pencarian, entitas, relasi, dan draft untuk Wiki Soeharto.
Membaca dari SQLite FTS5 (scripts/indexer/wiki-fts5.db) dan repo content/.
"""

import sqlite3
import re
import os
import yaml
from pathlib import Path
from collections import deque

REPO_DIR = Path("/home/ubuntu/quartz")
DB_PATH = REPO_DIR / "scripts/indexer/wiki-fts5.db"
CONTENT_DIR = REPO_DIR / "content"
PROPOSALS_DIR = REPO_DIR / "proposals"

CANONICAL_CATEGORIES = [
    {"slug": "kekuasaan-dan-legitimasi", "name": "Bagaimana Orde Baru Berkuasa?", "desc": "Transisi kekuasaan, legitimasi, pemilu, militer, dan aturan main politik 1966–1998"},
    {"slug": "ekonomi-dan-pembangunan", "name": "Siapa Menguasai Ekonomi?", "desc": "Pembangunan, konglomerat, BUMN, utang, dan konsentrasi kepemilikan di era Orde Baru"},
    {"slug": "keamanan-dan-keadilan", "name": "Siapa Diawasi, Siapa Dibungkam?", "desc": "Keamanan, intelijen, pers, dan penindakan terhadap oposisi dan kritik"},
    {"slug": "kesejahteraan-dan-kemasyarakatan", "name": "Bagaimana Rakyat Hidup?", "desc": "Desa, buruh, tani, pendidikan, transmigrasi, dan kehidupan sehari-hari di bawah pembangunan Orde Baru"},
    {"slug": "budaya-dan-ideologi", "name": "Konsep Kunci", "desc": "Penjelas istilah dan konsep yang sering dipakai untuk memahami Orde Baru"},
    {"slug": "transisi-dan-konstitusi", "name": "Bagaimana Orde Baru Berakhir?", "desc": "Krisis 1997–1998, gerakan reformasi, dan transisi keluar dari Orde Baru"}
]


class WikiQuery:
    def __init__(self, db_path=None, repo_dir=None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.repo_dir = Path(repo_dir) if repo_dir else REPO_DIR
        self.content_dir = self.repo_dir / "content"
        self.proposals_dir = self.repo_dir / "proposals"

    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    # 1. search
    def search(self, query: str, limit: int = 10, category: str = None) -> list[dict]:
        """
        Pencarian FTS5 BM25 berbobot (judul x10, deskripsi x5, body x1) dengan snippet.
        Mendukung ekspansi alias entitas dan filter kategori.
        """
        if not query or not query.strip():
            return []
        
        q_clean = query.strip()
        q_safe = re.sub(r'["\^\*\(\):]', ' ', q_clean).strip()
        if not q_safe:
            q_safe = q_clean

        conn = self._get_conn()
        c = conn.cursor()

        alias_rows = c.execute(
            "SELECT entity_id, title FROM entities WHERE aliases LIKE ? OR title LIKE ? LIMIT 3",
            (f"%{q_clean}%", f"%{q_clean}%")
        ).fetchall()
        
        match_terms = [f'"{q_safe}"']
        for ar in alias_rows:
            if ar["entity_id"]:
                match_terms.append(f'"{ar["entity_id"]}"')
            if ar["title"]:
                match_terms.append(f'"{ar["title"]}"')
        
        fts_match_query = " OR ".join(set(match_terms))

        sql = """
            SELECT path, title, description, entity_type, entity_id, kategori, tags,
                   snippet(pages, 3, '<b>', '</b>', '...', 25) AS snippet,
                   bm25(pages, 10.0, 5.0, 1.0) AS score
            FROM pages
            WHERE pages MATCH ?
        """
        params = [fts_match_query]

        if category:
            sql += " AND kategori = ?"
            params.append(category)

        sql += " ORDER BY score LIMIT ?"
        params.append(limit)

        try:
            rows = c.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            sql_fallback = """
                SELECT path, title, description, entity_type, entity_id, kategori, tags,
                       snippet(pages, 3, '<b>', '</b>', '...', 25) AS snippet,
                       bm25(pages, 10.0, 5.0, 1.0) AS score
                FROM pages
                WHERE pages MATCH ?
            """
            params_fallback = [q_safe]
            if category:
                sql_fallback += " AND kategori = ?"
                params_fallback.append(category)
            sql_fallback += " ORDER BY score LIMIT ?"
            params_fallback.append(limit)
            rows = c.execute(sql_fallback, params_fallback).fetchall()

        results = []
        for r in rows:
            results.append({
                "path": r["path"],
                "title": r["title"],
                "description": r["description"],
                "entity_type": r["entity_type"],
                "entity_id": r["entity_id"],
                "kategori": r["kategori"],
                "tags": [t.strip() for t in (r["tags"] or "").split(",") if t.strip()],
                "snippet": r["snippet"],
                "score": round(r["score"], 4)
            })
        conn.close()
        return results

    # 2. get_entity
    def get_entity(self, name_or_id: str) -> dict:
        """
        Mengambil entitas berdasarkan entity_id, title, atau aliases.
        Bila ambigu, mengembalikan candidates[] tanpa menebak satu halaman.
        """
        if not name_or_id:
            return {"found": False, "error": "name_or_id wajib diisi"}

        target = name_or_id.strip()
        conn = self._get_conn()
        c = conn.cursor()

        exact_id = c.execute(
            "SELECT * FROM entities WHERE LOWER(entity_id) = LOWER(?)", (target,)
        ).fetchall()
        
        exact_title = c.execute(
            "SELECT * FROM entities WHERE LOWER(title) = LOWER(?)", (target,)
        ).fetchall()

        candidates_map = {}
        for r in exact_id + exact_title:
            candidates_map[r["entity_id"] or r["path"]] = dict(r)

        if not candidates_map:
            alias_matches = c.execute(
                "SELECT * FROM entities WHERE aliases LIKE ? OR title LIKE ?",
                (f"%{target}%", f"%{target}%")
            ).fetchall()
            for r in alias_matches:
                candidates_map[r["entity_id"] or r["path"]] = dict(r)

        candidates = list(candidates_map.values())

        if not candidates:
            conn.close()
            return {"found": False, "query": target, "message": "Entitas tidak ditemukan"}

        if len(candidates) > 1:
            conn.close()
            return {
                "found": False,
                "ambiguous": True,
                "query": target,
                "candidates_count": len(candidates),
                "candidates": [
                    {
                        "entity_id": c["entity_id"],
                        "title": c["title"],
                        "entity_type": c["entity_type"],
                        "kategori": c["kategori"],
                        "path": c["path"]
                    }
                    for c in candidates[:10]
                ]
            }

        entity = candidates[0]
        eid = entity["entity_id"] or entity["title"]

        outgoing = c.execute(
            "SELECT predikat, target_entity, sumber FROM relations WHERE source_entity = ? OR source_entity = ?",
            (eid, entity["title"])
        ).fetchall()

        incoming = c.execute(
            "SELECT source_entity, predikat, sumber FROM relations WHERE target_entity = ? OR target_entity = ?",
            (eid, entity["title"])
        ).fetchall()

        conn.close()

        return {
            "found": True,
            "entity_id": entity["entity_id"],
            "title": entity["title"],
            "entity_type": entity["entity_type"],
            "description": entity["description"],
            "path": entity["path"],
            "kategori": entity["kategori"],
            "aliases": [a.strip() for a in (entity["aliases"] or "").split(",") if a.strip()],
            "tags": [t.strip() for t in (entity["tags"] or "").split(",") if t.strip()],
            "content_hash": entity["content_hash"],
            "outgoing_relations": [dict(r) for r in outgoing],
            "incoming_relations": [dict(r) for r in incoming]
        }

    # 3. get_relations
    def get_relations(self, entity_id: str, depth: int = 1, origin: str = None, predicate: str = None) -> list[dict]:
        """
        Mengambil relasi graf dari entitas dengan kedalaman N-hop.
        origin: 'frontmatter' (predikat non-wikilink) atau 'wikilink'.
        """
        if not entity_id:
            return []

        depth = min(max(depth, 1), 3)
        conn = self._get_conn()
        c = conn.cursor()

        visited_nodes = {entity_id.lower()}
        queue = deque([(entity_id, 0)])
        relations_result = []
        seen_edges = set()

        while queue:
            current_entity, current_depth = queue.popleft()
            if current_depth >= depth:
                continue

            sql = "SELECT source_entity, predikat, target_entity, sumber FROM relations WHERE (LOWER(source_entity) = LOWER(?) OR LOWER(source_entity) IN (SELECT LOWER(title) FROM entities WHERE LOWER(entity_id) = LOWER(?)))"
            params = [current_entity, current_entity]

            if origin == "frontmatter":
                sql += " AND predikat != 'wikilink'"
            elif origin == "wikilink":
                sql += " AND predikat = 'wikilink'"

            if predicate:
                sql += " AND predikat = ?"
                params.append(predicate)

            rows = c.execute(sql, params).fetchall()
            for r in rows:
                edge_key = (r["source_entity"], r["predikat"], r["target_entity"])
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    relations_result.append({
                        "source": r["source_entity"],
                        "predicate": r["predikat"],
                        "target": r["target_entity"],
                        "source_ref": r["sumber"],
                        "hop": current_depth + 1
                    })
                    target_lower = r["target_entity"].lower()
                    if target_lower not in visited_nodes:
                        visited_nodes.add(target_lower)
                        queue.append((r["target_entity"], current_depth + 1))

        conn.close()
        return relations_result

    # 4. relations_between
    def relations_between(self, source_id: str, target_id: str, max_depth: int = 4) -> dict:
        """
        Pencarian jalur terpendek (BFS) antara dua entitas dalam tabel relations.
        """
        if not source_id or not target_id:
            return {"found": False, "message": "source_id dan target_id wajib diisi"}

        conn = self._get_conn()
        c = conn.cursor()

        queue = deque([(source_id, [])])
        visited = {source_id.lower()}

        target_lower = target_id.lower()

        while queue:
            current, path = queue.popleft()
            if len(path) >= max_depth:
                continue

            rows = c.execute(
                "SELECT predikat, target_entity, sumber FROM relations WHERE LOWER(source_entity) = LOWER(?)",
                (current,)
            ).fetchall()

            for r in rows:
                tgt = r["target_entity"]
                step = {
                    "from": current,
                    "predicate": r["predikat"],
                    "to": tgt,
                    "source": r["sumber"]
                }
                new_path = path + [step]

                if tgt.lower() == target_lower:
                    conn.close()
                    return {
                        "found": True,
                        "hops": len(new_path),
                        "source": source_id,
                        "target": target_id,
                        "path": new_path
                    }

                if tgt.lower() not in visited:
                    visited.add(tgt.lower())
                    queue.append((tgt, new_path))

        conn.close()
        return {
            "found": False,
            "source": source_id,
            "target": target_id,
            "max_depth": max_depth,
            "message": f"Tidak ditemukan jalur relasi hingga {max_depth} hop"
        }

    # 5. timeline
    def timeline(self, entity_id: str = None, category: str = None, limit: int = 20, sort: str = "asc") -> list[dict]:
        """
        Kronologi peristiwa dan pidato bertanggal.
        """
        conn = self._get_conn()
        c = conn.cursor()

        sql = "SELECT path, title, description, entity_type, entity_id, kategori FROM pages WHERE 1=1"
        params = []

        if category:
            sql += " AND kategori = ?"
            params.append(category)

        if entity_id:
            sql += " AND (entity_id = ? OR body LIKE ? OR title LIKE ?)"
            params.extend([entity_id, f"%{entity_id}%", f"%{entity_id}%"])

        rows = c.execute(sql, params).fetchall()
        conn.close()

        date_pattern = re.compile(r'\b(19\d{2}-\d{2}-\d{2}|19\d{2}-\d{2}|19\d{2})\b')
        items = []

        for r in rows:
            m = date_pattern.search(r["title"]) or date_pattern.search(r["path"])
            date_str = m.group(1) if m else "1900-01-01"
            items.append({
                "date": date_str,
                "title": r["title"],
                "description": r["description"],
                "entity_type": r["entity_type"],
                "entity_id": r["entity_id"],
                "kategori": r["kategori"],
                "path": r["path"]
            })

        items.sort(key=lambda x: x["date"], reverse=(sort.lower() == "desc"))
        return items[:limit]

    # 6. get_page
    def get_page(self, path_or_id: str) -> dict:
        """
        Membaca teks halaman markdown asli lengkap + parsing frontmatter dari disk.
        """
        if not path_or_id:
            return {"found": False, "error": "path_or_id wajib diisi"}

        conn = self._get_conn()
        c = conn.cursor()
        row = c.execute(
            "SELECT path, entity_id, title FROM pages WHERE path = ? OR entity_id = ? LIMIT 1",
            (path_or_id, path_or_id)
        ).fetchone()
        conn.close()

        rel_path = row["path"] if row else path_or_id
        full_path = self.repo_dir / rel_path

        if not full_path.exists() and not full_path.suffix:
            full_path = self.repo_dir / f"{rel_path}.md"

        if not full_path.exists():
            return {"found": False, "path": rel_path, "error": "File tidak ditemukan di disk"}

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
            if m:
                fm_raw, body = m.group(1), m.group(2)
                fm = yaml.safe_load(fm_raw) or {}
            else:
                fm = {}
                body = content

            return {
                "found": True,
                "path": str(full_path.relative_to(self.repo_dir)),
                "frontmatter": fm,
                "body": body,
                "size_bytes": len(content.encode("utf-8"))
            }
        except Exception as e:
            return {"found": False, "path": rel_path, "error": str(e)}

    # 7. stats
    def stats(self) -> dict:
        """
        Statistik index pencarian, entitas, dan relasi.
        """
        conn = self._get_conn()
        c = conn.cursor()

        total_pages = c.execute("SELECT count(*) FROM pages").fetchone()[0]
        total_entities = c.execute("SELECT count(*) FROM entities").fetchone()[0]
        total_relations = c.execute("SELECT count(*) FROM relations").fetchone()[0]
        fm_relations = c.execute("SELECT count(*) FROM relations WHERE predikat != 'wikilink'").fetchone()[0]
        wikilink_relations = c.execute("SELECT count(*) FROM relations WHERE predikat = 'wikilink'").fetchone()[0]

        meta_rows = c.execute("SELECT key, value FROM meta").fetchall()
        meta = {r["key"]: r["value"] for r in meta_rows}

        category_counts = {}
        for r in c.execute("SELECT kategori, count(*) FROM pages GROUP BY kategori").fetchall():
            if r[0]:
                category_counts[r[0]] = r[1]

        type_counts = {}
        for r in c.execute("SELECT entity_type, count(*) FROM entities GROUP BY entity_type").fetchall():
            if r[0]:
                type_counts[r[0]] = r[1]

        conn.close()

        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            "total_pages": total_pages,
            "total_entities": total_entities,
            "total_relations": total_relations,
            "relations_breakdown": {
                "frontmatter": fm_relations,
                "wikilink": wikilink_relations
            },
            "category_distribution": category_counts,
            "entity_type_distribution": type_counts,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "meta": meta
        }

    # 8. save_draft (SATU-SATUNYA JALUR TULIS)
    def save_draft(self, slug: str, title: str, content: str, reason: str = "") -> dict:
        """
        Satu-satunya jalur tulis lewat MCP. Menulis draft ke proposals/<slug>.md untuk review.
        DILARANG menulis langsung ke content/ (regresi governance).
        """
        if not slug or not title or not content:
            return {"success": False, "error": "slug, title, dan content wajib diisi"}

        clean_slug = re.sub(r"[^a-z0-9\-]", "", slug.lower().strip().replace(" ", "-"))
        if not clean_slug:
            return {"success": False, "error": "slug tidak valid"}

        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        target_file = self.proposals_dir / f"{clean_slug}.md"

        fm_header = (
            "---\n"
            f'title: "{title}"\n'
            f'status: "draft"\n'
            f'reason: "{reason}"\n'
            "---\n\n"
        )
        
        full_doc = fm_header + content.strip() + "\n"

        try:
            target_file.write_text(full_doc, encoding="utf-8")
            return {
                "success": True,
                "slug": clean_slug,
                "file_path": str(target_file.relative_to(self.repo_dir)),
                "message": f"Draft berhasil disimpan di proposals/{clean_slug}.md untuk review manual user.",
                "size_bytes": len(full_doc.encode("utf-8"))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # 9. list_entities
    def list_entities(self, entity_type: str = None, category: str = None, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        Daftar entitas terdaftar dengan filter entity_type dan kategori.
        """
        conn = self._get_conn()
        c = conn.cursor()

        sql = "SELECT entity_id, entity_type, title, description, kategori, path FROM entities WHERE 1=1"
        params = []

        if entity_type:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        if category:
            sql += " AND kategori = ?"
            params.append(category)

        sql += " ORDER BY title LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = c.execute(sql, params).fetchall()
        conn.close()

        return [dict(r) for r in rows]

    # 10. get_backlinks
    def get_backlinks(self, entity_id: str, limit: int = 50) -> list[dict]:
        """
        Mengambil semua backlink / relasi masuk yang menunjuk ke entitas ini.
        """
        if not entity_id:
            return []

        conn = self._get_conn()
        c = conn.cursor()

        rows = c.execute(
            """
            SELECT source_entity, predikat, sumber 
            FROM relations 
            WHERE LOWER(target_entity) = LOWER(?) 
               OR LOWER(target_entity) IN (SELECT LOWER(title) FROM entities WHERE LOWER(entity_id) = LOWER(?))
            LIMIT ?
            """,
            (entity_id, entity_id, limit)
        ).fetchall()
        conn.close()

        return [
            {
                "source": r["source_entity"],
                "predicate": r["predikat"],
                "source_ref": r["sumber"]
            }
            for r in rows
        ]

    # 11. search_by_tag
    def search_by_tag(self, tag: str, limit: int = 20) -> list[dict]:
        """
        Mencari entitas dan halaman berdasarkan tag kanonikal.
        """
        if not tag:
            return []

        tag_clean = tag.strip().lower()
        conn = self._get_conn()
        c = conn.cursor()

        rows = c.execute(
            "SELECT path, title, description, entity_type, entity_id, kategori, tags FROM pages WHERE tags LIKE ? LIMIT ?",
            (f"%{tag_clean}%", limit)
        ).fetchall()
        conn.close()

        results = []
        for r in rows:
            tag_list = [t.strip().lower() for t in (r["tags"] or "").split(",") if t.strip()]
            if tag_clean in tag_list or any(tag_clean in t for t in tag_list):
                results.append({
                    "path": r["path"],
                    "title": r["title"],
                    "description": r["description"],
                    "entity_type": r["entity_type"],
                    "entity_id": r["entity_id"],
                    "kategori": r["kategori"],
                    "tags": tag_list
                })
        return results

    # 12. list_categories
    def list_categories(self) -> list[dict]:
        """
        Daftar 6 kategori resmi dan jumlah artikel di masing-masing kategori.
        """
        conn = self._get_conn()
        c = conn.cursor()
        counts = dict(c.execute("SELECT kategori, count(*) FROM pages GROUP BY kategori").fetchall())
        conn.close()

        categories = []
        for cat in CANONICAL_CATEGORIES:
            slug = cat["slug"]
            categories.append({
                "slug": slug,
                "name": cat["name"],
                "description": cat["desc"],
                "page_count": counts.get(slug, 0)
            })
        return categories
