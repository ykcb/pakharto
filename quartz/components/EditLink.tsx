import { existsSync } from "node:fs"
import { join } from "node:path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

/**
 * Link kecil di footer halaman yang membuka halaman ini langsung di editor tim
 * (/input/?edit=<path>).
 *
 * relativePath untuk halaman konten = path file di content/ (mis. "peristiwa/foo.md"),
 * dan untuk halaman folder = "<folder>/_index.md". Halaman generated (tag, 404) punya
 * relativePath juga, tapi file-nya tidak ada di content/ — jadi disaring dengan existsSync.
 */
const EDIT_BASE = "https://pakharto.my.id/input/?edit="

const EditLink: QuartzComponent = ({ fileData, ctx }: QuartzComponentProps) => {
  const rel = fileData.relativePath
  if (!rel || !rel.endsWith(".md")) {
    return null
  }
  if (!existsSync(join(ctx.argv.directory, rel))) {
    return null
  }
  const target = rel.slice(0, -3) // buang ".md"
  return (
    <a href={EDIT_BASE + target} class="edit-page-link" title="Edit halaman ini lewat editor tim">
      ✎ Edit halaman ini
    </a>
  )
}

export default (() => EditLink) satisfies QuartzComponentConstructor
