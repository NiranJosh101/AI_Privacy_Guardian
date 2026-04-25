import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig(({ mode }) => ({
  base: "./",
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
  },
  plugins: [
    react(),
    mode === "development" && componentTagger(),
    // This is the missing piece: it forces the manifest into dist
    viteStaticCopy({
      targets: [
        {
          src: 'public/manifest.json',
          dest: '.'
        }
      ]
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
        background: path.resolve(__dirname, "public/background.js"),
      },
      output: {
        entryFileNames: (chunkInfo) => {
          return chunkInfo.name === "background" ? "[name].js" : "assets/[name]-[hash].js";
        },
      },
    },
  },
}));