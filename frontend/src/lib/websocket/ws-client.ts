import { type WsMessage, WsMessageSchema } from "./messageSchema";

type MessageListener = (message: WsMessage) => void;
type VoidListener = () => void;
type ErrorListener = (event: Event) => void;

export class WebSocketClient {
	private socket?: WebSocket;

	private messageListeners = new Set<MessageListener>();
	private openListeners = new Set<VoidListener>();
	private closeListeners = new Set<VoidListener>();
	private errorListeners = new Set<ErrorListener>();

	constructor(private readonly url: string) {}

	connect(token: string) {
		if (this.socket?.readyState === WebSocket.OPEN) {
			return;
		}
		const url = `${this.url}?token=${encodeURIComponent(token)}`;

		this.socket = new WebSocket(url);

		this.socket.onopen = () => {
			this.openListeners.forEach((listener) => {
				listener();
			});
		};

		this.socket.onclose = () => {
			this.closeListeners.forEach((listener) => {
				listener();
			});
		};

		this.socket.onerror = (event) => {
			this.errorListeners.forEach((listener) => {
				listener(event);
			});
		};

		this.socket.onmessage = (event) => {
			this.handleMessage(event.data);
		};
	}

	disconnect() {
		this.socket?.close();
	}

	send(message: WsMessage) {
		if (this.socket?.readyState !== WebSocket.OPEN) {
			throw new Error("WebSocket is not connected.");
		}

		this.socket.send(JSON.stringify(message));
	}

	onMessage(listener: MessageListener) {
		this.messageListeners.add(listener);

		return () => {
			this.messageListeners.delete(listener);
		};
	}

	onOpen(listener: VoidListener) {
		this.openListeners.add(listener);

		return () => {
			this.openListeners.delete(listener);
		};
	}

	onClose(listener: VoidListener) {
		this.closeListeners.add(listener);

		return () => {
			this.closeListeners.delete(listener);
		};
	}

	onError(listener: ErrorListener) {
		this.errorListeners.add(listener);

		return () => {
			this.errorListeners.delete(listener);
		};
	}

	private handleMessage(raw: string) {
		let json: unknown;

		try {
			json = JSON.parse(raw);
		} catch {
			console.error("Received invalid JSON.");
			return;
		}
		const parsed = WsMessageSchema.safeParse(json);

		if (!parsed.success) {
			console.error("Invalid websocket message.", parsed.error);
			return;
		}

		this.messageListeners.forEach((listener) => {
			listener(parsed.data);
		});
	}
}
