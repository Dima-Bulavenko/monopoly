import { useRouter } from "@tanstack/react-router";
import { api } from "#/lib/api";
import { useAuthStore } from "#/stores/auth.store";
import type {
	AccessTokenResponse,
	LoginRequest,
	RegisterRequest,
} from "#/types/api";

export function useLogin() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return async (data: LoginRequest) => {
		const resp = await api.post<AccessTokenResponse>("/auth/login", data);
		setAuth(resp.data.access_token);
		await router.navigate({ to: "/games" });
	};
}

export function useRegister() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return async (data: RegisterRequest) => {
		const resp = await api.post<AccessTokenResponse>("/auth/register", data);
		setAuth(resp.data.access_token);
		await router.navigate({ to: "/games" });
	};
}

export function useLogout() {
	const clearAuth = useAuthStore((s) => s.clearAuth);
	const router = useRouter();

	return async () => {
		try {
			await api.post("/auth/logout", undefined, { withCredentials: true });
		} catch {
			// ignore errors on logout
		}
		clearAuth();
		await router.navigate({ to: "/auth/login" });
	};
}
