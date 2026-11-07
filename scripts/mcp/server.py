#!/usr/bin/env python3
"""
FastMCP Server untuk Wiki Soeharto (pakharto.my.id).
Mengekspos 12 tools standar pengetahuan sejarah Orde Baru & Soeharto.
Dapat dijalankan via stdio (default) atau SSE/HTTP (--port 8000).
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Pastikan import wiki_query dari direktori yang sama
sys.path.insert(0, str(Path(__file__).parent))
from fastmcp import FastMCP
from wiki_query import WikiQuery

mcp = FastMCP(
    "WikiSoeharto",
    instructions=(
        "Wiki Soeharto Knowledge Graph & FTS5 Search MCP Server. "
        "Menyediakan akses terstruktur ke arsip pidato, peristiwa, konsep, regulasi, "
        "dan entitas sejarah Orde Baru (1966-1998). "
        "Semua jalur tulis dilindungi melalui save_draft ke proposals/ untuk review manusia."
    )
)

wq = WikiQuery()

@mcp.tool()
def search(query: str, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Pencarian FTS5 BM25 berbobot (judul x10, deskripsi x5, body x1) dengan snippet dan ekspansi alias."""
    return wq.search(query=query, limit=limit, category=category)

@mcp.tool()
def get_entity(name_or_id: str) -> Dict[str, Any]:
    """Mengambil profil entitas (aktor, topik, konsep, peristiwa). Jika ambigu, mengembalikan candidates[]."""
    return wq.get_entity(name_or_id=name_or_id)

@mcp.tool()
def get_relations(entity_id: str, depth: int = 1, origin: Optional[str] = None, predicate: Optional[str] = None) -> List[Dict[str, Any]]:
    """Mengambil graf relasi N-hop dari entitas. origin: 'frontmatter' atau 'wikilink'."""
    return wq.get_relations(entity_id=entity_id, depth=depth, origin=origin, predicate=predicate)

@mcp.tool()
def relations_between(source_id: str, target_id: str, max_depth: int = 4) -> Dict[str, Any]:
    """Pencarian jalur terpendek (BFS) relasi antar-dua entitas."""
    return wq.relations_between(source_id=source_id, target_id=target_id, max_depth=max_depth)

@mcp.tool()
def timeline(entity_id: Optional[str] = None, category: Optional[str] = None, limit: int = 20, sort: str = "asc") -> List[Dict[str, Any]]:
    """Daftar kronologi peristiwa/pidato bertanggal terurut."""
    return wq.timeline(entity_id=entity_id, category=category, limit=limit, sort=sort)

@mcp.tool()
def get_page(path_or_id: str) -> Dict[str, Any]:
    """Membaca teks halaman markdown asli dan YAML frontmatter langsung dari disk."""
    return wq.get_page(path_or_id=path_or_id)

@mcp.tool()
def stats() -> Dict[str, Any]:
    """Statistik indeks pencarian, jumlah halaman, entitas, dan relasi."""
    return wq.stats()

@mcp.tool()
def save_draft(slug: str, title: str, content: str, reason: str = "") -> Dict[str, Any]:
    """SATU-SATUNYA jalur tulis MCP: menyimpan draft artikel baru ke proposals/<slug>.md untuk ditinjau."""
    return wq.save_draft(slug=slug, title=title, content=content, reason=reason)

@mcp.tool()
def list_entities(entity_type: Optional[str] = None, category: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Daftar entitas terdaftar dengan filter tipe (aktor, topik, konsep, peristiwa) dan kategori."""
    return wq.list_entities(entity_type=entity_type, category=category, limit=limit, offset=offset)

@mcp.tool()
def get_backlinks(entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Mengambil backlink dan relasi masuk yang menunjuk ke entitas ini."""
    return wq.get_backlinks(entity_id=entity_id, limit=limit)

@mcp.tool()
def search_by_tag(tag: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Mencari entitas dan halaman berdasarkan tag kanonikal."""
    return wq.search_by_tag(tag=tag, limit=limit)

@mcp.tool()
def list_categories() -> List[Dict[str, Any]]:
    """Daftar 6 kategori kanonikal Orde Baru dan jumlah artikel di tiap kategori."""
    return wq.list_categories()


def run_self_test():
    """Verifikasi 12 tools dengan assertion nyata (batch 2 audit 7 Nov 2026).

    Dulu: sebagian hasil hanya dicetak 'OK' tanpa menguji kebenaran
    (search 0 hasil pun lolos), dan save_draft meninggalkan file uji
    permanen di proposals/. Sekarang: setiap tool harus mengembalikan
    hasil yang benar-benar ada, dan draft uji dibersihkan kembali.
    """
    print("=== VERIFIKASI 12 TOOLS MCP WIKI SOEHARTO ===")

    # 1. stats — indeks harus mencerminkan konten saat ini (bukan DB basi)
    st = stats()
    assert st["total_pages"] > 1000, f"total_pages terlalu kecil: {st}"
    assert int(st["meta"]["file_count"]) == st["total_pages"], \
        f"meta file_count {st['meta']} != total_pages {st['total_pages']}"
    print(f"[1/12] stats: {st['total_pages']} halaman, {st['total_entities']} entitas, {st['total_relations']} relasi -> OK")

    # 2. search — harus menemukan hasil, bukan 0
    sr = search(query="pembangunan", limit=3)
    assert len(sr) > 0, "search('pembangunan') mengembalikan 0 hasil"
    print(f"[2/12] search('pembangunan'): ditemukan {len(sr)} hasil -> OK")

    # 3. get_entity
    ent = get_entity(name_or_id="soeharto")
    assert ent.get("found") is True
    print(f"[3/12] get_entity('soeharto'): {ent['title']} ({ent['entity_type']}) -> OK")

    # Ambiguity check (informatif, bukan assertion keras)
    amb = get_entity(name_or_id="pembangunan")
    print(f"       ambiguity test on 'pembangunan': ambiguous={amb.get('ambiguous', False)} candidates={len(amb.get('candidates', []))} -> OK")

    # 4. get_relations
    rels = get_relations(entity_id="soeharto", depth=1)
    assert len(rels) > 0, "get_relations('soeharto') mengembalikan 0 relasi"
    print(f"[4/12] get_relations('soeharto'): {len(rels)} relasi ditemukan -> OK")

    # 5. relations_between — jalur soeharto -> Kopkamtib harus ditemukan
    rb = relations_between(source_id="soeharto", target_id="Kopkamtib", max_depth=3)
    assert rb.get("found") is True, f"relations_between soeharto->Kopkamtib tidak ketemu: {rb}"
    print(f"[5/12] relations_between('soeharto', 'Kopkamtib'): found={rb.get('found')} hops={rb.get('hops')} -> OK")

    # 6. timeline
    tl = timeline(limit=5)
    assert len(tl) > 0, "timeline() mengembalikan 0 peristiwa"
    print(f"[6/12] timeline(limit=5): {len(tl)} peristiwa kronologis -> OK")

    # 7. get_page — baca valid + tolak traversal (negatif)
    pg = get_page(path_or_id="content/hub/orde-baru.md")
    assert pg.get("found") is True
    assert get_page(path_or_id="../../etc/passwd").get("found") is False
    assert get_page(path_or_id="/etc/passwd").get("found") is False
    print(f"[7/12] get_page('content/hub/orde-baru.md'): {pg['frontmatter'].get('title')} ({pg['size_bytes']} bytes); traversal ditolak -> OK")

    # 8. save_draft — tulis, timpa slug yang sama harus jadi versi baru
    # (bukan menimpa), lalu bersihkan semua file uji.
    dr = save_draft(
        slug="uji-coba-mcp",
        title="Uji Coba MCP Tool",
        content="Ini adalah konten uji coba untuk memverifikasi save_draft.",
        reason="Pengujian otomatis Phase 3"
    )
    assert dr.get("success") is True
    first_path = wq.proposals_dir / Path(dr["file_path"]).name
    assert first_path.exists(), f"draft tidak tertulis: {first_path}"
    dr2 = save_draft(
        slug="uji-coba-mcp",
        title='Uji "kedua" dengan kutip',
        content="Draft kedua, slug sama.",
        reason="Uji anti-timpa + YAML escaping"
    )
    assert dr2.get("success") is True
    assert dr2.get("versioned") is True, "slug sama seharusnya jadi versi baru, bukan menimpa"
    assert dr2["file_path"] != dr["file_path"], "path versi kedua harus berbeda"
    second_path = wq.proposals_dir / Path(dr2["file_path"]).name
    assert second_path.exists(), f"draft versi kedua tidak tertulis: {second_path}"
    first_path.unlink()
    second_path.unlink()
    assert not first_path.exists() and not second_path.exists()
    print(f"[8/12] save_draft('uji-coba-mcp'): tulis + anti-timpa (versi) + YAML aman + cleanup -> OK")

    # 9. list_entities
    le = list_entities(limit=5)
    assert len(le) > 0, "list_entities() mengembalikan 0 entitas"
    print(f"[9/12] list_entities(limit=5): {len(le)} entitas terdaftar -> OK")

    # 10. get_backlinks
    bl = get_backlinks(entity_id="soeharto")
    assert len(bl) > 0, "get_backlinks('soeharto') mengembalikan 0 backlink"
    print(f"[10/12] get_backlinks('soeharto'): {len(bl)} backlink masuk -> OK")

    # 11. search_by_tag
    stg = search_by_tag(tag="orde-baru", limit=5)
    assert len(stg) > 0, "search_by_tag('orde-baru') mengembalikan 0 artikel"
    print(f"[11/12] search_by_tag('orde-baru'): {len(stg)} artikel -> OK")

    # 12. list_categories — 6 slug kanonikal konten, bukan slug MCP lama
    cats = list_categories()
    assert len(cats) == 6, f"list_categories() mengembalikan {len(cats)} kategori, harus 6"
    expected_slugs = {
        "kekuasaan-dan-legitimasi", "ekonomi-dan-kepemilikan",
        "keamanan-dan-kebebasan", "pembangunan-dan-kehidupan",
        "krisis-dan-reformasi", "konsep",
    }
    assert {c["slug"] for c in cats} == expected_slugs, \
        f"slug kategori tidak cocok: {[c['slug'] for c in cats]}"
    print(f"[12/12] list_categories(): {len(cats)} kategori resmi, slug sesuai konten -> OK")

    print("\n✅ SEMUA 12 TOOLS MCP BERHASIL DIVERIFIKASI DENGAN SUKSES!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Wiki Soeharto FastMCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--test", action="store_true", help="Jalankan verifikasi mandiri 12 tools")
    args = parser.parse_args()

    if args.test:
        run_self_test()
    else:
        if args.transport == "stdio":
            mcp.run(transport="stdio")
        else:
            mcp.run(transport=args.transport, port=args.port)
