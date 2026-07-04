import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { refresh } from "#/client/sdk.gen";
import { isTokenExpired } from "#/lib/jwt";
import { useAuthStore } from "#/stores/auth.store";

export const Route = createFileRoute("/_authenticated")({
	beforeLoad: async ({ location, context: { wsClient } }) => {
		const redirectToLogin = () =>
			redirect({
				to: "/auth/login",
				search: location.href,
				replace: true,
			});

		let token = useAuthStore.getState().accessToken;
		if (!token) {
			throw redirectToLogin();
		}
		if (isTokenExpired(token)) {
			try {
				const resp = await refresh({ throwOnError: true });
				token = resp.data.access_token;
				useAuthStore.getState().setAuth(resp.data.access_token);
			} catch {
				throw redirectToLogin();
			}
		}
		wsClient.connect(token);
	},
	component: () => <Outlet />,
});
