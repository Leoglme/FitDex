import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import sharp from 'sharp'

const publicDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'public')
const svg = readFileSync(join(publicDir, 'favicon.svg'))

const icons = [
  { name: 'apple-touch-icon.png', size: 180 },
  { name: 'icon-192.png', size: 192 },
  { name: 'icon-512.png', size: 512 },
  { name: 'icon-512-maskable.png', size: 512 },
]

await Promise.all(
  icons.map(({ name, size }) => sharp(svg).resize(size, size).png().toFile(join(publicDir, name))),
)

console.log(`Generated ${icons.length} PWA icons in public/`)
