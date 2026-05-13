import { Link } from "@tanstack/react-router";
import { LogOut, Trophy } from "lucide-react";
import { Button } from "#/components/ui/button";
import { useLogout } from "#/hooks/use-auth";
import { useAuthStore } from "#/stores/auth.store";

export function Header() {
	const displayName = useAuthStore((s) => s.displayName);
	const accessToken = useAuthStore((s) => s.accessToken);
	const logout = useLogout();

	return (
		<header className="border-b border-gray-200 bg-white px-4 py-3">
			<div className="mx-auto flex max-w-screen-xl items-center justify-between">
				<Link
					to="/"
					className="flex items-center gap-2 font-bold text-gray-900"
				>
					<Trophy size={20} className="text-yellow-500" />
					<span>Monopoly</span>
				</Link>

				{accessToken && (
					<div className="flex items-center gap-3">
						<span className="text-sm text-gray-600">
							{displayName ?? "Player"}
						</span>
						<Button
							variant="outline"
							size="sm"
							onClick={logout}
							className="flex items-center gap-1.5"
						>
							<LogOut size={14} />
							Logout
						</Button>
					</div>
				)}
			</div>
		</header>
	);
}
