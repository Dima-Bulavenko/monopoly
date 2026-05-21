import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { registerOptions } from "#/features/auth/api/queryOptions";
import { useAuthStore } from "#/stores/auth.store";

export function useRegister() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return useMutation({
		...registerOptions(),
		onSuccess: (data) => {
			setAuth(data.access_token);
			router.navigate({ to: "/games" });
		},
	});
}
