export type ThemeDefault = 'light' | 'dark' | 'system';

/** Server default only; each browser may override it locally. */
export function getEnvTheme(): ThemeDefault | undefined {
  const raw = process.env.DEFAULT_THEME?.trim().toLowerCase();
  if (raw === 'light' || raw === 'dark' || raw === 'system') return raw;
  if (raw) console.warn('[LibreTV] DEFAULT_THEME invalid, ignored:', raw);
  return undefined;
}