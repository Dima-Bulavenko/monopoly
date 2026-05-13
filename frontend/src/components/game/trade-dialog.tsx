import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import { BOARD_SQUARES } from "#/components/game/board/board-data";
import { Button } from "#/components/ui/button";
import { Input } from "#/components/ui/input";
import { Label } from "#/components/ui/label";
import type { InboundMessage } from "#/types/ws";

interface PropertyState {
	owner_id: string | null;
	houses: number;
	hotel: boolean;
	mortgaged: boolean;
	square_index: number;
}

interface Player {
	player_id: string;
	name: string;
	balance: number;
}

interface TradeDialogProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
	userId: string | null;
	myProperties: PropertyState[];
	players: Player[];
	allProperties: Record<string, PropertyState>;
	sendAction: (msg: InboundMessage) => void;
}

export function TradeDialog({
	open,
	onOpenChange,
	userId,
	myProperties,
	players,
	allProperties,
	sendAction,
}: TradeDialogProps) {
	const [targetPlayerId, setTargetPlayerId] = useState("");
	const [offerMoney, setOfferMoney] = useState(0);
	const [requestMoney, setRequestMoney] = useState(0);
	const [offerProps, setOfferProps] = useState<number[]>([]);
	const [requestProps, setRequestProps] = useState<number[]>([]);

	const otherPlayers = players.filter((p) => p.player_id !== userId);
	const targetProperties = Object.values(allProperties).filter(
		(p) => p.owner_id === targetPlayerId,
	);

	function toggleOffer(idx: number) {
		setOfferProps((prev) =>
			prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx],
		);
	}

	function toggleRequest(idx: number) {
		setRequestProps((prev) =>
			prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx],
		);
	}

	function handleSubmit() {
		if (!targetPlayerId) return;
		sendAction({
			action: "propose_trade",
			target_player_id: targetPlayerId,
			offer_money: offerMoney,
			offer_property_indices: offerProps,
			request_money: requestMoney,
			request_property_indices: requestProps,
		});
		onOpenChange(false);
	}

	return (
		<Dialog.Root open={open} onOpenChange={onOpenChange}>
			<Dialog.Portal>
				<Dialog.Overlay className="fixed inset-0 bg-black/40 z-40" />
				<Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-xl border border-gray-200 bg-white p-6 shadow-xl">
					<Dialog.Title className="mb-4 text-lg font-bold text-gray-900">
						🤝 Propose Trade
					</Dialog.Title>

					{/* Target player */}
					<div className="mb-4 space-y-1">
						<Label>Trade with</Label>
						<select
							className="w-full rounded-md border border-gray-200 px-3 py-2 text-sm"
							value={targetPlayerId}
							onChange={(e) => {
								setTargetPlayerId(e.target.value);
								setRequestProps([]);
							}}
						>
							<option value="">Select player…</option>
							{otherPlayers.map((p) => (
								<option key={p.player_id} value={p.player_id}>
									{p.name}
								</option>
							))}
						</select>
					</div>

					<div className="grid grid-cols-2 gap-4">
						{/* Offer side */}
						<div>
							<h3 className="mb-2 text-sm font-semibold text-gray-700">
								Your Offer
							</h3>
							<div className="mb-2 space-y-1">
								<Label className="text-xs">Cash ($)</Label>
								<Input
									type="number"
									min={0}
									value={offerMoney}
									onChange={(e) => setOfferMoney(Number(e.target.value))}
								/>
							</div>
							<p className="mb-1 text-xs text-gray-500">Properties</p>
							<div className="space-y-1">
								{myProperties.length === 0 ? (
									<p className="text-xs text-gray-400 italic">
										No properties owned
									</p>
								) : (
									myProperties.map((p) => {
										const sq = BOARD_SQUARES[p.square_index];
										return (
											<label
												key={p.square_index}
												className="flex items-center gap-2 cursor-pointer"
											>
												<input
													type="checkbox"
													checked={offerProps.includes(p.square_index)}
													onChange={() => toggleOffer(p.square_index)}
													className="rounded"
												/>
												<span className="text-xs">
													{sq?.name ?? p.square_index}
												</span>
											</label>
										);
									})
								)}
							</div>
						</div>

						{/* Request side */}
						<div>
							<h3 className="mb-2 text-sm font-semibold text-gray-700">
								Your Request
							</h3>
							<div className="mb-2 space-y-1">
								<Label className="text-xs">Cash ($)</Label>
								<Input
									type="number"
									min={0}
									value={requestMoney}
									onChange={(e) => setRequestMoney(Number(e.target.value))}
								/>
							</div>
							<p className="mb-1 text-xs text-gray-500">Properties</p>
							<div className="space-y-1">
								{!targetPlayerId ? (
									<p className="text-xs text-gray-400 italic">
										Select a player first
									</p>
								) : targetProperties.length === 0 ? (
									<p className="text-xs text-gray-400 italic">
										They own no properties
									</p>
								) : (
									targetProperties.map((p) => {
										const sq = BOARD_SQUARES[p.square_index];
										return (
											<label
												key={p.square_index}
												className="flex items-center gap-2 cursor-pointer"
											>
												<input
													type="checkbox"
													checked={requestProps.includes(p.square_index)}
													onChange={() => toggleRequest(p.square_index)}
													className="rounded"
												/>
												<span className="text-xs">
													{sq?.name ?? p.square_index}
												</span>
											</label>
										);
									})
								)}
							</div>
						</div>
					</div>

					<div className="mt-6 flex justify-end gap-2">
						<Button variant="outline" onClick={() => onOpenChange(false)}>
							Cancel
						</Button>
						<Button onClick={handleSubmit} disabled={!targetPlayerId}>
							Send Trade
						</Button>
					</div>
				</Dialog.Content>
			</Dialog.Portal>
		</Dialog.Root>
	);
}
