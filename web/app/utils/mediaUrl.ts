/**
 * Résout une URL d'image exercice (catalogue web ou upload API).
 * @param path - Chemin renvoyé par l'API.
 * @returns L'URL complète affichable.
 */
export function resolveMediaUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null
  }
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  if (path.startsWith('/uploads/')) {
    const config = useRuntimeConfig()
    return `${config.public.apiBase}${path}`
  }
  return path
}
