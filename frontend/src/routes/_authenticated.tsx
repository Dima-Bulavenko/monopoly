import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useAuthStore } from "#/stores/auth.store";

export const Route = createFileRoute("/_authenticated")({
	beforeLoad() {
		const token = useAuthStore.getState().accessToken;
		if (!token) {
			throw redirect({ to: "/auth/login" });
		}
	},
	component: () => <Outlet />,
});
