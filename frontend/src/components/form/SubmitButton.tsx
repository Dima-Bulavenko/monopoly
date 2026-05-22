import { useFormContext } from "#/hooks/form-context";
import { Button } from "../ui/button";

type SubmitButtonProps = {
	label: string;
};

export default function SubmitButton({ label }: SubmitButtonProps) {
	const form = useFormContext();

	return (
		<form.Subscribe selector={(state) => state.isSubmitting}>
			{(isSubmitting) => (
				<Button type="submit" disabled={isSubmitting}>
					{label}
				</Button>
			)}
		</form.Subscribe>
	);
}
