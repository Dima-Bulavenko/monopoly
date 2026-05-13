import { createFileRoute, Link, redirect } from "@tanstack/react-router";
import { useAuthStore } from "#/stores/auth.store";

export const Route = createFileRoute("/")({
	beforeLoad() {
		const token = useAuthStore.getState().accessToken;
		if (token) {
			throw redirect({ to: "/games" });
		}
	},
	component: Home,
});

function Home() {
	return (
		<div className="flex min-h-[80vh] flex-col items-center justify-center gap-6 text-center">
			<h1 className="text-5xl font-bold text-gray-900">🎩 Monopoly</h1>
			<p className="max-w-sm text-gray-500">
				Create or join a game and start building your empire.
			</p>
			<div className="flex gap-3">
				<Link
					to="/auth/login"
					className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white shadow hover:bg-blue-700"
				>
					Sign in
				</Link>
				<Link
					to="/auth/register"
					className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 font-medium text-gray-700 shadow hover:bg-gray-50"
				>
					Register
				</Link>
			</div>
		</div>
	);
}
