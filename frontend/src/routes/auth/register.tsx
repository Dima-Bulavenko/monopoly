import { createFileRoute, Link } from "@tanstack/react-router";
import RegisterForm from "#/features/auth/ui/RegisterForm";

export const Route = createFileRoute("/auth/register")({
	component: RegisterPage,
});

function RegisterPage() {
	return (
		<div className="flex min-h-screen items-center justify-center bg-gray-50">
			<div className="w-full max-w-sm rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
				<h1 className="mb-6 text-2xl font-bold text-gray-900">
					Create account
				</h1>
				<RegisterForm />

				<p className="mt-4 text-center text-sm text-gray-500">
					Already have an account?{" "}
					<Link
						to="/auth/login"
						className="font-medium text-blue-600 hover:underline"
					>
						Sign in
					</Link>
				</p>
			</div>
		</div>
	);
}
