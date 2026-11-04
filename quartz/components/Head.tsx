import { i18n } from "../i18n"
import { FullSlug, joinSegments, pathToRoot } from "../util/path"
import { CSSResourceToStyleElement, JSResourceToScriptElement } from "../util/resources"
import { googleFontHref, googleFontSubsetHref } from "../util/theme"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { unescapeHTML } from "../util/escape"

export default (() => {
  const Head: QuartzComponent = ({
    cfg,
    fileData,
    externalResources,
    ctx,
  }: QuartzComponentProps) => {
    const titleSuffix = cfg.pageTitleSuffix ?? ""
    const rawTitle = fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title
    const title = (rawTitle ? rawTitle + titleSuffix : cfg.pageTitle ?? "Wiki Soeharto")
    const description =
      fileData.frontmatter?.socialDescription ??
      fileData.frontmatter?.description ??
      unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)

    const { css, js, additionalHead } = externalResources

    const baseUrl = cfg.baseUrl ?? "pakharto.my.id"
    const url = new URL(`https://${baseUrl}`)
    const path = url.pathname as FullSlug
    const baseDir = fileData.slug === "404" ? path : pathToRoot(fileData.slug!)
    const iconPath = joinSegments(baseDir, "static/icon.png")

    // Canonical & Social URL of current page
    const isHome = fileData.slug === "index" || fileData.slug === "" || !fileData.slug
    const is404 = fileData.slug === "404"
    const canonicalUrl = isHome
      ? `https://${baseUrl}/`
      : is404
      ? `https://${baseUrl}/404`
      : `https://${baseUrl}/${fileData.slug}`

    const socialUrl = canonicalUrl

    const usesCustomOgImage = ctx.cfg.plugins.emitters.some((e) => e.name === "CustomOgImages")

    // OG Image: banner poster "Wiki Soeharto - Meluruskan sejarah"
    // (content/img/og-image.jpg -> public/img/og-image.jpg saat build).
    // Parameter `v` dipakai untuk memaksa WhatsApp/Telegram mengambil ulang
    // gambar saat banner diganti (cache OG image cukup agresif).
    const ogImageUrl = `https://${baseUrl}/img/og-image.jpg`
    const ogImageVersion = 2
    const ogImageDefaultPath = `${ogImageUrl}?v=${ogImageVersion}`
    const ogImageType = "image/jpeg"
    const ogImageWidth = 1376
    const ogImageHeight = 768

    const coreStylesheet = css[0]?.content
    const coreScript = js.find(
      (r) => r.loadTime === "beforeDOMReady" && r.contentType === "external",
    )

    // Metadata ekstra untuk Artikel / Tokoh / Peristiwa
    const isArticle = !isHome && !is404
    const publishDate = fileData.frontmatter?.date ? String(fileData.frontmatter.date).slice(0, 10) : undefined
    const modifiedDate = fileData.frontmatter?.last_updated
      ? String(fileData.frontmatter.last_updated).slice(0, 10)
      : fileData.frontmatter?.updated
      ? String(fileData.frontmatter.updated).slice(0, 10)
      : publishDate
    const kategori = fileData.frontmatter?.kategori ? String(fileData.frontmatter.kategori) : undefined
    const rawTags = (fileData.frontmatter?.tags as string[]) ?? []
    const tagsList = Array.isArray(rawTags) ? rawTags : []
    const keywords = tagsList.length > 0 ? tagsList.join(", ") : undefined

    // JSON-LD Schema.org Structured Data (Optimal untuk GEO, AEO, dan Google Search)
    const jsonLd = (() => {
      if (is404) return null

      if (isHome) {
        return {
          "@context": "https://schema.org",
          "@graph": [
            {
              "@type": "WebSite",
              "@id": `https://${baseUrl}/#website`,
              "url": `https://${baseUrl}/`,
              "name": cfg.pageTitle ?? "Wiki Soeharto",
              "alternateName": ["Pakharto Wiki", "Wiki Orde Baru", "Ensiklopedi Soeharto"],
              "description": description,
              "inLanguage": "id-ID",
              "publisher": {
                "@type": "Organization",
                "@id": `https://${baseUrl}/#organization`,
                "name": "Wiki Soeharto",
                "url": `https://${baseUrl}/`,
                "logo": {
                  "@type": "ImageObject",
                  "url": `https://${baseUrl}/static/icon.png`
                }
              }
            },
            {
              "@type": "Organization",
              "@id": `https://${baseUrl}/#organization`,
              "name": "Wiki Soeharto",
              "url": `https://${baseUrl}/`,
              "logo": `https://${baseUrl}/static/icon.png`,
              "description": "Ensiklopedia independen berbasis data dan arsip primer tentang era Orde Baru Indonesia.",
              "sameAs": [
                "https://github.com/ykcb/pakharto"
              ]
            }
          ]
        }
      }

      // Deteksi entity_type untuk schema.org yang presisi
      const entityType = fileData.frontmatter?.entity_type ? String(fileData.frontmatter.entity_type) : undefined
      let schemaType: string | string[] = "Article"
      if (entityType === "aktor") {
        schemaType = ["Person", "Article"]
      } else if (entityType === "peristiwa") {
        schemaType = ["HistoricalEvent", "Article"]
      }

      const slugParts = fileData.slug ? fileData.slug.split("/") : []
      const sectionSlug = slugParts.length > 1 ? slugParts[0] : undefined
      const sectionName = sectionSlug
        ? sectionSlug.charAt(0).toUpperCase() + sectionSlug.slice(1).replace(/-/g, " ")
        : "Artikel"

      const breadcrumbList = {
        "@type": "BreadcrumbList",
        "@id": `${canonicalUrl}#breadcrumb`,
        "itemListElement": [
          {
            "@type": "ListItem",
            "position": 1,
            "name": "Beranda",
            "item": `https://${baseUrl}/`
          },
          ...(sectionSlug
            ? [
                {
                  "@type": "ListItem",
                  "position": 2,
                  "name": sectionName,
                  "item": `https://${baseUrl}/${sectionSlug}`
                },
                {
                  "@type": "ListItem",
                  "position": 3,
                  "name": rawTitle,
                  "item": canonicalUrl
                }
              ]
            : [
                {
                  "@type": "ListItem",
                  "position": 2,
                  "name": rawTitle,
                  "item": canonicalUrl
                }
              ])
        ]
      }

      const articleNode = {
        "@type": schemaType,
        "@id": `${canonicalUrl}#mainEntity`,
        "isPartOf": {
          "@type": "WebPage",
          "@id": canonicalUrl,
          "url": canonicalUrl,
          "name": title
        },
        "headline": rawTitle,
        "name": rawTitle,
        "description": description,
        "inLanguage": "id-ID",
        "mainEntityOfPage": canonicalUrl,
        "url": canonicalUrl,
        "image": ogImageUrl,
        ...(publishDate ? { "datePublished": publishDate } : {}),
        ...(modifiedDate ? { "dateModified": modifiedDate } : {}),
        "author": {
          "@type": "Organization",
          "name": "Tim Riset Wiki Soeharto",
          "url": `https://${baseUrl}/`
        },
        "publisher": {
          "@type": "Organization",
          "@id": `https://${baseUrl}/#organization`,
          "name": "Wiki Soeharto",
          "url": `https://${baseUrl}/`,
          "logo": {
            "@type": "ImageObject",
            "url": `https://${baseUrl}/static/icon.png`
          }
        },
        ...(keywords ? { "keywords": keywords } : {}),
        ...(kategori ? { "articleSection": kategori } : {})
      }

      return {
        "@context": "https://schema.org",
        "@graph": [articleNode, breadcrumbList]
      }
    })()

    return (
      <head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        <link rel="canonical" href={canonicalUrl} />

        {/* Search & AI Crawlers Directive */}
        <meta
          name="robots"
          content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
        />
        <meta
          name="googlebot"
          content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
        />
        <meta
          name="bingbot"
          content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
        />

        {/* AI Engine Optimization & Corpus Discovery */}
        <link rel="alternate" type="text/plain" href={`https://${baseUrl}/llms.txt`} title="LLM Context Summary" />
        <link rel="alternate" type="text/plain" href={`https://${baseUrl}/llms-full.txt`} title="LLM Full Context" />
        <meta name="ai-content-declaration" content="human-curated, verified-historical-archive" />
        <meta name="author" content="Tim Riset Wiki Soeharto" />
        {keywords && <meta name="keywords" content={keywords} />}

        {coreStylesheet && <link rel="preload" href={coreStylesheet} as="style" />}
        {coreScript && coreScript.contentType === "external" && (
          <link rel="preload" href={coreScript.src} as="script" />
        )}
        {cfg.theme.cdnCaching && cfg.theme.fontOrigin === "googleFonts" && (
          <>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" />
            <link rel="stylesheet" href={googleFontHref(cfg.theme)} />
            {cfg.theme.typography.title && (
              <link rel="stylesheet" href={googleFontSubsetHref(cfg.theme, cfg.pageTitle)} />
            )}
          </>
        )}
        <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossOrigin="anonymous" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        {/* OpenGraph Metadata */}
        <meta name="og:site_name" content={cfg.pageTitle} />
        <meta property="og:title" content={title} />
        <meta property="og:type" content={isArticle ? "article" : "website"} />
        <meta property="og:description" content={description} />
        <meta property="og:image:alt" content={description} />
        <meta property="og:url" content={canonicalUrl} />

        {/* Article specific OpenGraph */}
        {isArticle && publishDate && <meta property="article:published_time" content={publishDate} />}
        {isArticle && modifiedDate && <meta property="article:modified_time" content={modifiedDate} />}
        {isArticle && kategori && <meta property="article:section" content={kategori} />}
        {isArticle && tagsList.map((tag) => <meta property="article:tag" content={tag} key={tag} />)}

        {/* Twitter Card Metadata */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta property="twitter:domain" content={baseUrl} />
        <meta property="twitter:url" content={canonicalUrl} />

        {!usesCustomOgImage && (
          <>
            <meta property="og:image" content={ogImageDefaultPath} />
            <meta property="og:image:url" content={ogImageDefaultPath} />
            <meta property="og:image:secure_url" content={ogImageDefaultPath} />
            <meta name="twitter:image" content={ogImageDefaultPath} />
            <meta property="og:image:type" content={ogImageType} />
            <meta property="og:image:width" content={String(ogImageWidth)} />
            <meta property="og:image:height" content={String(ogImageHeight)} />
            <meta name="twitter:image:alt" content="Wiki Soeharto - Meluruskan sejarah" />
          </>
        )}

        <link rel="icon" href={iconPath} />
        <meta name="description" content={description} />
        <meta name="generator" content="Quartz" />

        {/* JSON-LD Structured Data for AI & Search Engines */}
        {jsonLd && (
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
          />
        )}

        {css.map((resource) => CSSResourceToStyleElement(resource, true))}
        {js
          .filter((resource) => resource.loadTime === "beforeDOMReady")
          .map((res) => JSResourceToScriptElement(res, true))}
        {additionalHead.map((resource) => {
          if (typeof resource === "function") {
            return resource(fileData)
          } else {
            return resource
          }
        })}
      </head>
    )
  }

  return Head
}) satisfies QuartzComponentConstructor
