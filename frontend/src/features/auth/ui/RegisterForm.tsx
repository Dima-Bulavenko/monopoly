import { formOptions } from "@tanstack/react-form";
import * as z from "zod";
import { Field, FieldGroup } from "#/components/ui/field";
import { useAppForm } from "#/hooks/form";

const registerFormSchema = z.object({
	username: z.string().min(3, "Username must be at least 3 characters"),
	email: z.email("Invalid email address"),
	password: z.string().min(6, "Password must be at least 6 characters"),
});

const defaultValues: z.infer<typeof registerFormSchema> = {
	username: "",
	email: "",
	password: "",
};

const registerFormOpts = formOptions({
	defaultValues,
	validators: {
		onBlur: registerFormSchema,
	},
});

export default function RegisterForm() {
	const form = useAppForm({
		...registerFormOpts,
		onSubmit: (values) => {
			console.log(values);
		},
	});
	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				form.handleSubmit();
			}}
		>
			<FieldGroup>
				<form.AppField name="username">
					{(field) => <field.TextField id="username_id" label="Username" />}
				</form.AppField>
				<form.AppField name="email">
					{(field) => <field.EmailField id="email_id" label="Email" />}
				</form.AppField>
				<form.AppField name="password">
					{(field) => <field.PasswordField id="password_id" label="Password" />}
				</form.AppField>
				<Field>
					<form.AppForm>
						<form.SubmitButton label="Submit" />
					</form.AppForm>
				</Field>
			</FieldGroup>
		</form>
	);
}
