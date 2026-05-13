import { Button } from "#/components/ui/button";
import type { InboundMessage } from "#/types/ws";

interface JailPanelProps {
	jailTurns: number;
	getOutOfJailCards: number;
	sendAction: (msg: InboundMessage) => void;
}

export function JailPanel({
	jailTurns,
	getOutOfJailCards,
	sendAction,
}: JailPanelProps) {
	return (
		<div className="flex flex-col gap-3">
			<p className="text-sm text-orange-700 font-semibold">
				⛓ You are in Jail ({jailTurns} turn{jailTurns !== 1 ? "s" : ""}{" "}
				remaining)
			</p>
			<div className="flex flex-col gap-2">
				<Button onClick={() => sendAction({ action: "roll_dice" })}>
					🎲 Roll for Doubles
				</Button>
				<Button
					variant="outline"
					onClick={() => sendAction({ action: "pay_jail_fine" })}
				>
					💵 Pay $50 Fine
				</Button>
				{getOutOfJailCards > 0 && (
					<Button
						variant="outline"
						onClick={() => sendAction({ action: "use_jail_card" })}
					>
						🃏 Use Get Out of Jail Card ({getOutOfJailCards})
					</Button>
				)}
			</div>
		</div>
	);
}
