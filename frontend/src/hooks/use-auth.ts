import { useRouter } from "@tanstack/react-router";
import { login, logout, register } from "#/client/sdk.gen";
import type { LoginRequest, RegisterRequest } from "#/client/types.gen";
import { useAuthStore } from "#/stores/auth.store";

export function useLogin() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return async (data: LoginRequest) => {
		const { data: resp } = await login({ body: data, throwOnError: true });
		setAuth(resp.access_token);
		await router.navigate({ to: "/games" });
	};
}

export function useRegister() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return async (data: RegisterRequest) => {
		const { data: resp } = await register({ body: data, throwOnError: true });
		setAuth(resp.access_token);
		await router.navigate({ to: "/games" });
	};
}

export function useLogout() {
	const clearAuth = useAuthStore((s) => s.clearAuth);
	const router = useRouter();

	return async () => {
		try {
			await logout();
		} catch {
			// ignore errors on logout
		}
		clearAuth();
		await router.navigate({ to: "/auth/login" });
	};
}
