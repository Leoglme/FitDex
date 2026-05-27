/**
 * Indique si la valeur d'icône renvoyée par l'API est un chemin d'image locale.
 * @param icon - Valeur du champ ``icon`` (Lucide ou chemin ``/muscle-groups/...``).
 * @returns `true` si l'icône doit être affichée comme image.
 */
export function isMuscleGroupImage(icon: string | null | undefined): boolean {
  return typeof icon === 'string' && icon.startsWith('/')
}
