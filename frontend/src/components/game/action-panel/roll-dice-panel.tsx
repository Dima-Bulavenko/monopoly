import { Button } from "#/components/ui/button";
import type { InboundMessage } from "#/types/ws";

interface RollDicePanelProps {
	sendAction: (msg: InboundMessage) => void;
}

export function RollDicePanel({ sendAction }: RollDicePanelProps) {
	return (
		<div className="flex flex-col gap-3">
			<p className="text-sm text-gray-600">Roll the dice to take your turn.</p>
			<Button onClick={() => sendAction({ action: "roll_dice" })}>
				🎲 Roll Dice
			</Button>
		</div>
	);
}
