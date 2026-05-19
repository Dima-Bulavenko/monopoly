import { heyApiPlugin } from "@hey-api/vite-plugin";
import babel from "@rolldown/plugin-babel";
import tailwindcss from "@tailwindcss/vite";
import { devtools } from "@tanstack/devtools-vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact, { reactCompilerPreset } from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const config = defineConfig({
	resolve: { tsconfigPaths: true },
	server: {
		proxy: {
			"/api/v1": "http://localhost:8000",
			"/ws": { target: "ws://localhost:8000", ws: true },
		},
	},
	plugins: [
		heyApiPlugin(),
		devtools(),
		tailwindcss(),
		tanstackStart({
			spa: { enabled: true },
		}),
		viteReact(),
		babel({ presets: [reactCompilerPreset()] }),
	],
});

export default config;
