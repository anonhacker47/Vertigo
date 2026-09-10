/**
 * Renders the tier list to a PNG on an offscreen canvas.
*/

export interface TierListImageTier {
  name: string
  color: string
  covers: (string | null)[]
}

export interface TierListImageInput {
  title: string
  tiers: TierListImageTier[]
  footer?: string
}

export interface Rect {
  x: number
  y: number
  w: number
  h: number
}

export interface TierRowLayout {
  rect: Rect
  label: Rect
  content: Rect
  covers: Rect[]
}

export interface TierListLayout {
  width: number
  height: number
  titleCenterY: number
  rows: TierRowLayout[]
  footerBaselineY: number | null
}

const PAGE_W = 1600
const PAD = 40
const BG = '#0f172a'
const ROW_BG = '#1a2332'
const CONTENT_BG = '#141b2b'
const ROW_BORDER = '#314158'
const ROW_RADIUS = 10
const ROW_GAP = 12
const ROW_PAD = 12
const LABEL_W = 96
const LABEL_FONT = '900 44px "Nunito", sans-serif'
const LABEL_TEXT = 'rgba(0,0,0,0.8)'
const TITLE_SIZE = 44
const TITLE_MIN_SIZE = 24
const TITLE_H = 56
const TITLE_GAP = 24
const COVER_W = 130
const COVER_H = 195
const COVER_GAP = 10
const COVER_RADIUS = 6
const COVER_BORDER = '#314158'
const PLACEHOLDER_BG = '#273244'
const PLACEHOLDER_TEXT = '#90a1b9'
const EMPTY_ROW_H = 96
const FOOTER_FONT = '400 16px "Nunito", sans-serif'
const FOOTER_COLOR = '#90a1b9'
const FOOTER_H = 24
const FOOTER_GAP = 16

const IMAGE_TIMEOUT_MS = 15_000
const IMAGE_CONCURRENCY = 8

const EXPORT_SCALE = 2

// Conservative browser canvas limits (per side, and total area).
export const MAX_CANVAS_SIDE = 16384
export const MAX_CANVAS_AREA = 268_435_456

function titleFont(size: number) {
  return `700 ${size}px "Nunito", sans-serif`
}


export function measureTierListLayout(
  tiers: TierListImageTier[],
  opts: { footer?: boolean } = {},
): TierListLayout {
  const rowW = PAGE_W - 2 * PAD
  const contentW = rowW - LABEL_W - 2 * ROW_PAD
  const perLine = Math.max(1, Math.floor((contentW + COVER_GAP) / (COVER_W + COVER_GAP)))

  let y = PAD + TITLE_H + TITLE_GAP
  const titleCenterY = PAD + TITLE_H / 2
  const rows: TierRowLayout[] = []

  for (const tier of tiers) {
    const n = tier.covers.length
    const lines = Math.ceil(n / perLine)
    const rowH = n === 0 ? EMPTY_ROW_H : 2 * ROW_PAD + lines * COVER_H + (lines - 1) * COVER_GAP

    const rect = { x: PAD, y, w: rowW, h: rowH }
    const label = { x: PAD, y, w: LABEL_W, h: rowH }
    const content = { x: PAD + LABEL_W, y, w: rowW - LABEL_W, h: rowH }
    const covers: Rect[] = []
    for (let i = 0; i < n; i++) {
      covers.push({
        x: content.x + ROW_PAD + (i % perLine) * (COVER_W + COVER_GAP),
        y: y + ROW_PAD + Math.floor(i / perLine) * (COVER_H + COVER_GAP),
        w: COVER_W,
        h: COVER_H,
      })
    }
    rows.push({ rect, label, content, covers })
    y += rowH + ROW_GAP
  }
  if (tiers.length) y -= ROW_GAP

  let footerBaselineY: number | null = null
  if (opts.footer) {
    y += FOOTER_GAP
    footerBaselineY = y + FOOTER_H - 6
    y += FOOTER_H
  }

  return { width: PAGE_W, height: y + PAD, titleCenterY, rows, footerBaselineY }
}

export function fitsCanvasLimits(layout: TierListLayout, scale: number): boolean {
  const w = layout.width * scale
  const h = layout.height * scale
  return w <= MAX_CANVAS_SIDE && h <= MAX_CANVAS_SIDE && w * h <= MAX_CANVAS_AREA
}

/** The sharp scale, or 1x for a list too long to fit a browser canvas at 2x. */
function pickScale(layout: TierListLayout): 1 | 2 {
  if (fitsCanvasLimits(layout, EXPORT_SCALE)) return EXPORT_SCALE
  if (fitsCanvasLimits(layout, 1)) return 1
  throw new Error(
    `The image would be ${layout.width} x ${layout.height} px, more than browsers can render. ` +
      'Rank fewer series and try again.',
  )
}

// ---------------------------------------------------------------- drawing helpers

function roundRectPath(ctx: CanvasRenderingContext2D, r: Rect, radius: number) {
  const { x, y, w, h } = r
  const rad = Math.min(radius, w / 2, h / 2)
  ctx.beginPath()
  ctx.moveTo(x + rad, y)
  ctx.arcTo(x + w, y, x + w, y + h, rad)
  ctx.arcTo(x + w, y + h, x, y + h, rad)
  ctx.arcTo(x, y + h, x, y, rad)
  ctx.arcTo(x, y, x + w, y, rad)
  ctx.closePath()
}

function strokeRoundRect(ctx: CanvasRenderingContext2D, r: Rect, radius: number, color: string) {
  ctx.save()
  ctx.strokeStyle = color
  ctx.lineWidth = 1
  roundRectPath(ctx, { x: r.x + 0.5, y: r.y + 0.5, w: r.w - 1, h: r.h - 1 }, radius)
  ctx.stroke()
  ctx.restore()
}

function fillRect(ctx: CanvasRenderingContext2D, r: Rect, color: string) {
  ctx.fillStyle = color
  ctx.fillRect(r.x, r.y, r.w, r.h)
}

function drawTitle(ctx: CanvasRenderingContext2D, title: string, layout: TierListLayout) {
  const maxW = layout.width - 2 * PAD
  let size = TITLE_SIZE
  ctx.font = titleFont(size)
  while (ctx.measureText(title).width > maxW && size > TITLE_MIN_SIZE) {
    size -= 2
    ctx.font = titleFont(size)
  }
  let text = title
  while (text.length > 1 && ctx.measureText(text + '…').width > maxW) {
    text = text.slice(0, -1)
  }
  if (text !== title) text += '…'

  ctx.fillStyle = '#ffffff'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, layout.width / 2, layout.titleCenterY)
}

function drawChrome(ctx: CanvasRenderingContext2D, layout: TierListLayout, input: TierListImageInput) {
  fillRect(ctx, { x: 0, y: 0, w: layout.width, h: layout.height }, BG)
  drawTitle(ctx, input.title, layout)

  layout.rows.forEach((row, i) => {
    const tier = input.tiers[i]
    ctx.save()
    roundRectPath(ctx, row.rect, ROW_RADIUS)
    ctx.clip()
    fillRect(ctx, row.rect, ROW_BG)
    fillRect(ctx, row.label, tier.color)
    fillRect(ctx, row.content, CONTENT_BG)
    ctx.restore()
    strokeRoundRect(ctx, row.rect, ROW_RADIUS, ROW_BORDER)

    ctx.fillStyle = LABEL_TEXT
    ctx.font = LABEL_FONT
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    // Nunito sits slightly high with the middle baseline; nudge for optical centring.
    ctx.fillText(tier.name, row.label.x + row.label.w / 2, row.label.y + row.label.h / 2 + 2)
  })

  if (input.footer && layout.footerBaselineY !== null) {
    ctx.fillStyle = FOOTER_COLOR
    ctx.font = FOOTER_FONT
    ctx.textAlign = 'right'
    ctx.textBaseline = 'alphabetic'
    ctx.fillText(input.footer, layout.width - PAD, layout.footerBaselineY)
  }
}

function drawPlaceholder(ctx: CanvasRenderingContext2D, rect: Rect) {
  ctx.save()
  roundRectPath(ctx, rect, COVER_RADIUS)
  ctx.clip()
  fillRect(ctx, rect, PLACEHOLDER_BG)
  ctx.fillStyle = PLACEHOLDER_TEXT
  ctx.font = '400 14px "Nunito", sans-serif'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('No cover', rect.x + rect.w / 2, rect.y + rect.h / 2)
  ctx.restore()
  strokeRoundRect(ctx, rect, COVER_RADIUS, COVER_BORDER)
}

/**
 * Shrinks a crop of `img` by repeated halving until it is within 2x of the target size.
 * Firefox ignores imageSmoothingQuality, and a single 8-10x downscale of a 3000 px cover
 * aliases visibly; halving steps keep it clean everywhere.
 */
function downscaleCrop(
  img: HTMLImageElement,
  crop: Rect,
  targetW: number,
  targetH: number,
  scratch: [HTMLCanvasElement, HTMLCanvasElement],
): { source: CanvasImageSource; rect: Rect } {
  let source: CanvasImageSource = img
  let rect = crop
  let flip = 0
  while (rect.w > 2 * targetW && rect.h > 2 * targetH) {
    const nw = Math.ceil(rect.w / 2)
    const nh = Math.ceil(rect.h / 2)
    const canvas = scratch[flip]
    flip = 1 - flip
    canvas.width = nw
    canvas.height = nh
    const c = canvas.getContext('2d')
    if (!c) break
    c.imageSmoothingEnabled = true
    c.imageSmoothingQuality = 'high'
    c.drawImage(source, rect.x, rect.y, rect.w, rect.h, 0, 0, nw, nh)
    source = canvas
    rect = { x: 0, y: 0, w: nw, h: nh }
  }
  return { source, rect }
}

function drawCoverFit(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  rect: Rect,
  scale: number,
  scratch: [HTMLCanvasElement, HTMLCanvasElement],
) {
  const sw = img.naturalWidth
  const sh = img.naturalHeight
  // Centered cover-crop to the 2:3 box.
  let cw: number
  let ch: number
  if (sw / sh > rect.w / rect.h) {
    ch = sh
    cw = Math.round((sh * rect.w) / rect.h)
  } else {
    cw = sw
    ch = Math.round((sw * rect.h) / rect.w)
  }
  const crop = { x: Math.floor((sw - cw) / 2), y: Math.floor((sh - ch) / 2), w: cw, h: ch }
  const { source, rect: src } = downscaleCrop(img, crop, Math.round(rect.w * scale), Math.round(rect.h * scale), scratch)

  ctx.save()
  roundRectPath(ctx, rect, COVER_RADIUS)
  ctx.clip()
  ctx.drawImage(source, src.x, src.y, src.w, src.h, rect.x, rect.y, rect.w, rect.h)
  ctx.restore()
  strokeRoundRect(ctx, rect, COVER_RADIUS, COVER_BORDER)
}

// ---------------------------------------------------------------- loading

function abortError() {
  return new DOMException('Tier list export cancelled.', 'AbortError')
}

/**
 * Resolves to the image, or null on error, timeout or abort. Only CORS-enabled loads are
 * returned. Setting `src = ''` cancels the network fetch so nothing keeps downloading.
 */
function loadCoverImage(url: string, timeoutMs: number, signal?: AbortSignal): Promise<HTMLImageElement | null> {
  return new Promise((resolve) => {
    if (signal?.aborted) return resolve(null)

    const img = new Image()
    let done = false
    const cancel = () => {
      img.src = ''
      finish(null)
    }
    const finish = (value: HTMLImageElement | null) => {
      if (done) return
      done = true
      clearTimeout(timer)
      signal?.removeEventListener('abort', cancel)
      img.onload = null
      img.onerror = null
      resolve(value)
    }
    const timer = setTimeout(cancel, timeoutMs)
    signal?.addEventListener('abort', cancel)
    img.crossOrigin = 'anonymous'
    img.onload = () => finish(img.naturalWidth > 0 ? img : null)
    img.onerror = () => finish(null)
    img.src = url
  })
}

/**
 * Runs `fn` over `items` with at most `limit` in flight. Stops scheduling new items as soon
 * as one fails or the signal aborts, so a broken or abandoned export does not keep working.
 */
async function mapWithConcurrency<T>(
  items: T[],
  limit: number,
  fn: (item: T) => Promise<void>,
  signal?: AbortSignal,
) {
  let next = 0
  let stopped = false
  const worker = async () => {
    while (!stopped && next < items.length) {
      if (signal?.aborted) {
        stopped = true
        break
      }
      const item = items[next++]
      try {
        await fn(item)
      } catch (err) {
        stopped = true
        throw err
      }
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker))
  if (signal?.aborted) throw abortError()
}

async function ensureFonts() {
  if (typeof document === 'undefined' || !document.fonts) return
  try {
    await Promise.all([titleFont(TITLE_SIZE), LABEL_FONT, FOOTER_FONT].map((f) => document.fonts.load(f)))
    await document.fonts.ready
  } catch {
    // Fall back to the generic family; the render still succeeds.
  }
}

// ---------------------------------------------------------------- entry points

/** Canvas backing stores are freed on GC; zeroing them releases the memory right away. */
function releaseCanvas(canvas: HTMLCanvasElement) {
  canvas.width = 0
  canvas.height = 0
}

export interface RenderOptions {
  /** Abort to stop loading covers, e.g. when the page is left mid-export. Rejects with an AbortError. */
  signal?: AbortSignal
}

export async function renderTierListImage(
  input: TierListImageInput,
  { signal }: RenderOptions = {},
): Promise<Blob> {
  const layout = measureTierListLayout(input.tiers, { footer: !!input.footer })
  const scale = pickScale(layout)

  await ensureFonts()
  if (signal?.aborted) throw abortError()

  const canvas = document.createElement('canvas')
  const scratch: [HTMLCanvasElement, HTMLCanvasElement] = [
    document.createElement('canvas'),
    document.createElement('canvas'),
  ]
  try {
    canvas.width = layout.width * scale
    canvas.height = layout.height * scale
    const ctx = canvas.getContext('2d', { alpha: false })
    if (!ctx) throw new Error('Canvas is not available in this browser.')
    ctx.scale(scale, scale)
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'

    drawChrome(ctx, layout, input)

    const jobs = layout.rows.flatMap((row, r) =>
      row.covers.map((rect, i) => ({ url: input.tiers[r].covers[i], rect })),
    )
    await mapWithConcurrency(
      jobs,
      IMAGE_CONCURRENCY,
      async ({ url, rect }) => {
        const img = url ? await loadCoverImage(url, IMAGE_TIMEOUT_MS, signal) : null
        if (signal?.aborted) return
        if (img) drawCoverFit(ctx, img, rect, scale, scratch)
        else drawPlaceholder(ctx, rect)
      },
      signal,
    )

    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/png'))
    if (signal?.aborted) throw abortError()
    if (!blob) throw new Error('Could not encode the image.')
    return blob
  } finally {
    releaseCanvas(canvas)
    scratch.forEach(releaseCanvas)
  }
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export function tierListFileName(title: string): string {
  const base = title
    .trim()
    // eslint-disable-next-line no-control-regex
    .replace(/[\\/:*?"<>|\x00-\x1f]/g, '')
    .replace(/\s+/g, '_')
    .slice(0, 80)
  return `${base || 'tier-list'}.png`
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
