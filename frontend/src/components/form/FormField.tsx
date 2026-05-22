import { useStore } from "@tanstack/react-form";
import { useFieldContext } from "#/hooks/form-context";
import { Field, FieldDescription, FieldError, FieldLabel } from "../ui/field";

export type FormFieldBaseProps = {
	label: string;
	id: string;
	description?: string;
};

type FormFieldProps = FormFieldBaseProps & {
	children: React.ReactNode;
};

export default function FormField({
	label,
	id,
	description,
	children,
}: FormFieldProps) {
	const field = useFieldContext<unknown>();
	const errors = useStore(field.store, (state) => state.meta.errors);
	const isValid = useStore(field.store, (state) => state.meta.isValid);

	return (
		<Field data-invalid={!isValid}>
			<FieldLabel htmlFor={id}>{label}</FieldLabel>
			{children}
			{description && <FieldDescription>{description}</FieldDescription>}
			<FieldError>
				{!isValid &&
					errors.map((error, _i) => (
						<div key={error.message}>{error.message}</div>
					))}
			</FieldError>
		</Field>
	);
}
