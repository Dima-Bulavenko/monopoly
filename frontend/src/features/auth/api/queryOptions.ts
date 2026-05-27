import { mutationOptions } from "@tanstack/react-query";
import { login, logout, register } from "#/client/sdk.gen";
import type { LoginRequest, RegisterRequest } from "#/client/types.gen";

export const authKeys = {
	all: ["auth"] as const,
	login: () => [...authKeys.all, "login"] as const,
	logout: () => [...authKeys.all, "logout"] as const,
	register: () => [...authKeys.all, "register"] as const,
} as const;

export function loginOptions() {
	return mutationOptions({
		mutationKey: authKeys.login(),
		mutationFn: (body: LoginRequest) =>
			login({ body, throwOnError: true }).then((res) => res.data),
	});
}

export function registerOptions() {
	return mutationOptions({
		mutationKey: authKeys.register(),
		mutationFn: (body: RegisterRequest) =>
			register({ body, throwOnError: true }).then((res) => res.data),
	});
}

export function logoutOptions() {
	return mutationOptions({
		mutationKey: authKeys.logout(),
		mutationFn: () => logout({ throwOnError: true }),
	});
}
