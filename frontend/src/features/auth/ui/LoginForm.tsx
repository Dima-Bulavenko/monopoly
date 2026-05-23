import { formOptions } from "@tanstack/react-form";
import { Link } from "@tanstack/react-router";
import z from "zod";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "#/components/ui/card.tsx";
import {
	Field,
	FieldDescription,
	FieldGroup,
	FieldSeparator,
} from "#/components/ui/field.tsx";
import { useAppForm } from "#/hooks/form";
import { cn } from "#/lib/utils.ts";
import { useLogin } from "../hooks/use-login.ts";
import { AppleAuthButton } from "./AppleAuthButton.tsx";
import { GoogleAuthButton } from "./GoogleAuthButton.tsx";

const loginFormSchema = z.object({
	email: z.email("Invalid email address"),
	password: z.string().min(1, "Password required"),
});

const defaultValues: z.infer<typeof loginFormSchema> = {
	email: "",
	password: "",
};

const formOpts = formOptions({
	defaultValues,
	validators: {
		onSubmit: loginFormSchema,
	},
});

export function LoginForm({
	className,
	...props
}: React.ComponentProps<"div">) {
	const login = useLogin();
	const form = useAppForm({
		...formOpts,
		onSubmit: ({ value }) => {
			return login
				.mutateAsync({
					email: value.email,
					password: value.password,
				})
				.catch(() => {});
		},
	});
	return (
		<div className={cn("flex flex-col gap-6", className)} {...props}>
			<Card>
				<CardHeader className="text-center">
					<CardTitle className="text-xl">Welcome back</CardTitle>
					<CardDescription>
						Login with your Apple or Google account
					</CardDescription>
				</CardHeader>
				<CardContent>
					<form
						onSubmit={(e) => {
							e.preventDefault();
							form.handleSubmit();
						}}
					>
						<FieldGroup>
							<Field>
								<AppleAuthButton onClick={() => {}} />
								<GoogleAuthButton onClick={() => {}} />
							</Field>
							<FieldSeparator className="*:data-[slot=field-separator-content]:bg-card">
								Or continue with
							</FieldSeparator>
							<form.AppField name="email">
								{(field) => <field.EmailField id="email" label="Email" />}
							</form.AppField>
							<form.AppField name="password">
								{(field) => (
									<div>
										<field.PasswordField id="password" label="Password" />
										<a
											href="notimplemented"
											className="ml-auto text-sm underline-offset-4 hover:underline"
										>
											Forgot your password?
										</a>
									</div>
								)}
							</form.AppField>
							<Field>
								<form.AppForm>
									<form.SubmitButton label="Login" />
								</form.AppForm>
								<FieldDescription className="text-center">
									Don&apos;t have an account?{" "}
									<Link to="/auth/register">Sign up</Link>
								</FieldDescription>
							</Field>
						</FieldGroup>
					</form>
				</CardContent>
			</Card>
			<FieldDescription className="px-6 text-center">
				By clicking continue, you agree to our{" "}
				<a href="notimplemented">Terms of Service</a> and{" "}
				<a href="notimplemented">Privacy Policy</a>.
			</FieldDescription>
		</div>
	);
}
