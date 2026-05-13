import { BOARD_SQUARES } from "#/components/game/board/board-data";
import { Button } from "#/components/ui/button";
import type { InboundMessage } from "#/types/ws";

interface BuyDecisionPanelProps {
	squareIndex: number;
	sendAction: (msg: InboundMessage) => void;
}

export function BuyDecisionPanel({
	squareIndex,
	sendAction,
}: BuyDecisionPanelProps) {
	const square = BOARD_SQUARES[squareIndex];
	return (
		<div className="flex flex-col gap-3">
			<p className="text-sm font-semibold text-gray-800">
				{square?.name ?? `Square ${squareIndex}`}
			</p>
			{square?.price !== null && (
				<p className="text-sm text-gray-600">
					Price: <span className="font-semibold">${square.price}</span>
				</p>
			)}
			<div className="flex gap-2">
				<Button onClick={() => sendAction({ action: "buy_property" })}>
					🏦 Buy
				</Button>
				<Button
					variant="outline"
					onClick={() => sendAction({ action: "pass_property" })}
				>
					⏭ Pass to Auction
				</Button>
			</div>
		</div>
	);
}
