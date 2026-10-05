import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'serve-campus-customs-products',
      configureServer(server) {
        server.middlewares.use('/products', (request, response, next) => {
          const filename = path.basename(decodeURIComponent(request.url ?? ''))
          const imagePath = path.resolve(__dirname, '..', 'products', filename)
          if (!filename || !fs.existsSync(imagePath)) return next()
          response.setHeader('Content-Type', 'image/jpeg')
          fs.createReadStream(imagePath).pipe(response)
        })
      },
    },
  ],
  server: {
    port: 5173,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
