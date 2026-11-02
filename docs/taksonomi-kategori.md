# Taksonomi Kategori — Wiki Orde Baru

Dokumen ini adalah source of truth untuk struktur klasifikasi, navigasi publik, dan metadata kategori di Wiki Orde Baru.

---

## 1. Prinsip Taksonomi

1. **Dua Lapis:**
   - **Nama Tampil:** Singkat, lugas, mengundang baca (format pertanyaan atau frasa pemantik).
   - **Deskriptor:** Menjelaskan cakupan topik dan menyertakan kata kunci penting untuk manusia dan LLM/mesin pencari.
2. **Satu Halaman, Satu Kategori Utama:**
   - Setiap halaman wajib memiliki tepat satu nilai pada field frontmatter `kategori: <slug>`.
   - Hubungan lintas kategori dicatat opsional pada field `kategori_tambahan: [<slug>]`.
3. **Pemisahan Kategori dan Tag:**
   - **Kategori:** Navigasi kasar (6 pilar utama sistemik).
   - **Tags:** Indeks halus (topik spesifik, institusi, instrumen kebijakan, aktor).
   - Tag dan kategori tidak dicampuradukkan.
4. **Halaman Arsip Kategori:**
   - Tiap kategori memiliki halaman representatif di `content/kategori/<slug>.md`.
   - Berisi definisi kategori, cakupan, dan daftar entri (Hub, Peristiwa, Analisis, Aktor, Regulasi).

---

## 2. Enam Kategori Publik (Resmi)

| # | Nama Tampil | Slug | Deskriptor Berkata Kunci |
|---|---|---|---|
| 1 | **Bagaimana Orde Baru Berkuasa?** | `kekuasaan-dan-legitimasi` | Transisi kekuasaan, legitimasi politik, pemilu, militer/Dwifungsi ABRI, dan aturan main kenegaraan 1966–1998. |
| 2 | **Siapa Menguasai Ekonomi?** | `ekonomi-dan-kepemilikan` | Pembangunan ekonomi, konglomerat, BUMN, utang luar negeri, technocrats, dan konsentrasi kepemilikan modal di era Orde Baru. |
| 3 | **Siapa Diawasi, Siapa Dibungkam?** | `keamanan-dan-kebebasan` | Keamanan negara, intelijen, sensor pers, Kopkamtib/Bakin, dan penindakan terhadap kritik serta oposisi politik. |
| 4 | **Bagaimana Rakyat Hidup?** | `pembangunan-dan-kehidupan` | Dinamika desa, buruh, tani, pendidikan, transmigrasi, kesehatan, dan kehidupan sehari-hari di bawah program pembangunan. |
| 5 | **Bagaimana Orde Baru Berakhir?** | `krisis-dan-reformasi` | Krisis moneter 1997–1998, gerakan mahasiswa dan masyarakat sipil, kejatuhan rezim, dan transisi awal era reformasi. |
| 6 | **Konsep Kunci** | `konsep` | Penjelas istilah, doktrin politik, instrumen hukum, dan konsep sentral untuk memahami cara kerja sistem Orde Baru. |

---

## 3. Integrasi Taksonomi ke Quartz & LLM

- Halaman beranda (`content/index.md`) mengelompokkan navigasi utama ke dalam blok "Mulai dari Sini!" berdasarkan 6 kategori ini.
- Daftar slug dan deskriptor ini diekspor ke file `llms.txt` sebagai peta konteks sistemik saat model bahasa mengindeks situs.
