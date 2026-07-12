import type { z } from "zod";

type MessageSchema = z.ZodObject<{
	type: z.ZodLiteral<string>;
	payload: z.ZodTypeAny;
}>;

type Handler<T extends MessageSchema> = (message: z.infer<T>) => void;

export class Dispatcher {
	private handlers = new Map<
		string,
		{
			schema: MessageSchema;
			handler: Handler<MessageSchema>;
		}
	>();

	register<T extends MessageSchema>(schema: T, handler: Handler<T>) {
		const type = schema.shape.type.value;

		this.handlers.set(type, {
			schema,
			handler,
		});
	}

	unregister(type: string) {
		this.handlers.delete(type);
	}

	dispatch(message: z.infer<MessageSchema>) {
		const registration = this.handlers.get(message.type);
		if (!registration) {
			console.warn(`No handler registered for message type: ${message.type}`);
			return;
		}

		const parsed = registration.schema.safeParse(message);

		if (!parsed.success) {
			console.error(parsed.error);
			return;
		}

		registration.handler(parsed.data);
	}
}
