import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { logoutOptions } from "#/features/auth/api/queryOptions";
import { useAuthStore } from "#/stores/auth.store";

export function useLogout() {
	const clearAuth = useAuthStore((s) => s.clearAuth);
	const router = useRouter();

	return useMutation({
		...logoutOptions(),
		onSettled: () => {
			clearAuth();
			router.navigate({ to: "/auth/login" });
		},
	});
}
