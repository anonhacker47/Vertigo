export function dominantRgb(value: unknown): [number, number, number] | null {
  if (Array.isArray(value) && value.length >= 3) {
    const [r, g, b] = value.map(Number);
    return [r, g, b].every(Number.isFinite) ? [r, g, b] : null;
  }
  if (typeof value === "string") {
    const match = value.match(/(\d+)\D+(\d+)\D+(\d+)/);
    if (match) return [Number(match[1]), Number(match[2]), Number(match[3])];
  }
  return null;
}
