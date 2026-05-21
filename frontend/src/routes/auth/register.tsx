import { useForm } from "@tanstack/react-form";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { z } from "zod";
import { Button } from "#/components/ui/button";
import { Input } from "#/components/ui/input";
import { Label } from "#/components/ui/label";
import { useRegister } from "#/features/auth/hooks";

export const Route = createFileRoute("/auth/register")({
	component: RegisterPage,
});

const schema = z.object({
	display_name: z.string().min(2, "Name must be at least 2 characters"),
	email: z.email("Invalid email"),
	password: z.string().min(8, "Password must be at least 8 characters"),
});

function RegisterPage() {
	const register = useRegister();
	const [serverError, setServerError] = useState<string | null>(null);

	const form = useForm({
		defaultValues: { display_name: "", email: "", password: "" },
		validators: { onSubmit: schema },
		onSubmit: async ({ value }) => {
			setServerError(null);
			try {
				await register.mutateAsync(value);
			} catch (err: unknown) {
				const msg =
					err instanceof Error
						? err.message
						: "Registration failed. Please try again.";
				setServerError(msg);
			}
		},
	});

	return (
		<div className="flex min-h-screen items-center justify-center bg-gray-50">
			<div className="w-full max-w-sm rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
				<h1 className="mb-6 text-2xl font-bold text-gray-900">
					Create account
				</h1>

				{serverError && (
					<p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
						{serverError}
					</p>
				)}

				<form
					onSubmit={(e) => {
						e.preventDefault();
						form.handleSubmit();
					}}
					className="space-y-4"
				>
					<form.Field name="display_name">
						{(field) => (
							<div className="space-y-1">
								<Label htmlFor={field.name}>Display name</Label>
								<Input
									id={field.name}
									type="text"
									autoComplete="name"
									value={field.state.value}
									onBlur={field.handleBlur}
									onChange={(e) => field.handleChange(e.target.value)}
								/>
								{field.state.meta.errors[0] && (
									<p className="text-xs text-red-500">
										{field.state.meta.errors[0].message}
									</p>
								)}
							</div>
						)}
					</form.Field>

					<form.Field name="email">
						{(field) => (
							<div className="space-y-1">
								<Label htmlFor={field.name}>Email</Label>
								<Input
									id={field.name}
									type="email"
									autoComplete="email"
									value={field.state.value}
									onBlur={field.handleBlur}
									onChange={(e) => field.handleChange(e.target.value)}
								/>
								{field.state.meta.errors[0] && (
									<p className="text-xs text-red-500">
										{field.state.meta.errors[0].message}
									</p>
								)}
							</div>
						)}
					</form.Field>

					<form.Field name="password">
						{(field) => (
							<div className="space-y-1">
								<Label htmlFor={field.name}>Password</Label>
								<Input
									id={field.name}
									type="password"
									autoComplete="new-password"
									value={field.state.value}
									onBlur={field.handleBlur}
									onChange={(e) => field.handleChange(e.target.value)}
								/>
								{field.state.meta.errors[0] && (
									<p className="text-xs text-red-500">
										{field.state.meta.errors[0].message}
									</p>
								)}
							</div>
						)}
					</form.Field>

					<form.Subscribe selector={(s) => s.isSubmitting}>
						{(isSubmitting) => (
							<Button type="submit" className="w-full" disabled={isSubmitting}>
								{isSubmitting ? "Creating account…" : "Create account"}
							</Button>
						)}
					</form.Subscribe>
				</form>

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
