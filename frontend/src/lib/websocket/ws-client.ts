import type { InboundMessage, OutboundMessage } from "#/types/ws";
import { OutboundMessageSchema } from "#/types/ws";

type MessageHandler = (msg: OutboundMessage) => void;

const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 5;

export class WsClient {
	private ws: WebSocket | null = null;
	private token = "";
	private reconnectAttempts = 0;
	private intentionalClose = false;
	private handlers: Set<MessageHandler> = new Set();

	connect(token: string) {
		this.token = token;
		this.intentionalClose = false;
		this.reconnectAttempts = 0;
		this._open();
	}

	private _open() {
		const url = `/ws?token=${encodeURIComponent(this.token)}`;
		this.ws = new WebSocket(url);

		this.ws.onmessage = (event: MessageEvent<string>) => {
			let raw: unknown;
			try {
				raw = JSON.parse(event.data);
			} catch {
				return;
			}
			const result = OutboundMessageSchema.safeParse(raw);
			if (result.success) {
				for (const h of this.handlers) h(result.data);
			}
		};

		this.ws.onclose = () => {
			if (this.intentionalClose) return;
			if (this.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
				this.reconnectAttempts++;
				setTimeout(() => this._open(), RECONNECT_DELAY_MS);
			}
		};
	}

	send(msg: InboundMessage) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(msg));
		}
	}

	addHandler(handler: MessageHandler) {
		this.handlers.add(handler);
	}

	removeHandler(handler: MessageHandler) {
		this.handlers.delete(handler);
	}

	disconnect() {
		this.intentionalClose = true;
		this.ws?.close();
		this.ws = null;
	}

	get isConnected() {
		return this.ws?.readyState === WebSocket.OPEN;
	}
}
