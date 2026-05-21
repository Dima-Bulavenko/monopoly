import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { loginOptions } from "#/features/auth/api/queryOptions";
import { useAuthStore } from "#/stores/auth.store";

export function useLogin() {
	const setAuth = useAuthStore((s) => s.setAuth);
	const router = useRouter();

	return useMutation({
		...loginOptions(),
		onSuccess: (data) => {
			setAuth(data.access_token);
			router.navigate({ to: "/games" });
		},
	});
}
