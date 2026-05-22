import { useFieldContext } from "#/hooks/form-context";
import { Input } from "../ui/input";
import FormField, { type FormFieldBaseProps } from "./FormField";

export type TextFieldProps = FormFieldBaseProps & {
	placeholder?: string;
};

export default function TextField({
	label,
	id,
	placeholder,
	description,
}: TextFieldProps) {
	const field = useFieldContext<string>();

	return (
		<FormField label={label} id={id} description={description}>
			<Input
				id={id}
				type="text"
				placeholder={placeholder}
				value={field.state.value}
				onChange={(e) => field.handleChange(e.target.value)}
				onBlur={field.handleBlur}
			/>
		</FormField>
	);
}
