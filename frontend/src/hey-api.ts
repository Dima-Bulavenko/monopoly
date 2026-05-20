import axios from "axios";
import { useAuthStore } from "#/stores/auth.store";
import type { CreateClientConfig } from "./client/client.gen";

const axiosInstance = axios.create();

let isRefreshing = false;
let refreshQueue: Array<(token: string | null) => void> = [];

function onRefreshDone(token: string | null) {
	for (const cb of refreshQueue) cb(token);
	refreshQueue = [];
}

axiosInstance.interceptors.response.use(
	(res) => res,
	async (error) => {
		const original = error.config;
		if (
			error.response?.status !== 401 ||
			original._retry ||
			original.url?.includes("/auth/")
		) {
			return Promise.reject(error);
		}
		original._retry = true;

		if (isRefreshing) {
			return new Promise((resolve, reject) => {
				refreshQueue.push((token) => {
					if (token) {
						original.headers.Authorization = `Bearer ${token}`;
						resolve(axiosInstance(original));
					} else {
						reject(error);
					}
				});
			});
		}

		isRefreshing = true;
		try {
			const resp = await axios.post<{ access_token: string }>(
				"/api/v1/auth/refresh",
				undefined,
				{ withCredentials: true },
			);
			const newToken = resp.data.access_token;
			useAuthStore.getState().setAuth(newToken);
			onRefreshDone(newToken);
			original.headers.Authorization = `Bearer ${newToken}`;
			return axiosInstance(original);
		} catch {
			onRefreshDone(null);
			useAuthStore.getState().clearAuth();
			return Promise.reject(error);
		} finally {
			isRefreshing = false;
		}
	},
);

export const createClientConfig: CreateClientConfig = (config) => ({
	...config,
	auth: () => useAuthStore.getState().accessToken ?? undefined,
	baseURL: "/api/v1",
	withCredentials: true,
	axios: axiosInstance,
});
