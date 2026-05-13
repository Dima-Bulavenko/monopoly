import { useState } from "react";
import { BOARD_SQUARES } from "#/components/game/board/board-data";
import { Button } from "#/components/ui/button";
import { Input } from "#/components/ui/input";
import type { InboundMessage } from "#/types/ws";

interface AuctionState {
	property_index: number;
	bids: Record<string, number>;
	current_bidder_index: number;
	passed_player_ids: string[];
}

interface Player {
	player_id: string;
	name: string;
}

interface AuctionPanelProps {
	auction: AuctionState;
	players: Player[];
	userId: string | null;
	sendAction: (msg: InboundMessage) => void;
}

export function AuctionPanel({
	auction,
	players,
	userId,
	sendAction,
}: AuctionPanelProps) {
	const [bidAmount, setBidAmount] = useState(1);
	const currentBidder = players[auction.current_bidder_index];
	const isMyTurn = currentBidder?.player_id === userId;
	const square = BOARD_SQUARES[auction.property_index];
	const highestBid = Object.values(auction.bids).reduce(
		(max, v) => Math.max(max, v),
		0,
	);

	return (
		<div className="flex flex-col gap-3">
			<p className="text-sm font-semibold text-gray-800">
				🔨 Auction: {square?.name ?? `Square ${auction.property_index}`}
			</p>

			{/* Current bids */}
			<div className="rounded-md border border-gray-200 bg-gray-50 p-2 text-xs space-y-1">
				{players.map((p) => {
					const bid = auction.bids[p.player_id];
					const passed = auction.passed_player_ids.includes(p.player_id);
					return (
						<div key={p.player_id} className="flex justify-between">
							<span className="text-gray-700">
								{p.name}
								{passed && <span className="ml-1 text-gray-400">(passed)</span>}
							</span>
							<span className="font-semibold">
								{bid !== undefined ? `$${bid}` : "—"}
							</span>
						</div>
					);
				})}
			</div>

			<p className="text-xs text-gray-500">
				Highest bid: <span className="font-semibold">${highestBid}</span>
				{" · "}Bidder:{" "}
				<span className="font-semibold">{currentBidder?.name ?? "—"}</span>
			</p>

			{isMyTurn ? (
				<div className="flex gap-2">
					<Input
						type="number"
						min={highestBid + 1}
						value={bidAmount}
						onChange={(e) => setBidAmount(Number(e.target.value))}
						className="w-24"
					/>
					<Button
						onClick={() =>
							sendAction({ action: "auction_bid", amount: bidAmount })
						}
					>
						Bid ${bidAmount}
					</Button>
					<Button
						variant="outline"
						onClick={() => sendAction({ action: "auction_pass" })}
					>
						Pass
					</Button>
				</div>
			) : (
				<p className="text-sm text-gray-500 italic">
					Waiting for {currentBidder?.name ?? "bidder"}…
				</p>
			)}
		</div>
	);
}
