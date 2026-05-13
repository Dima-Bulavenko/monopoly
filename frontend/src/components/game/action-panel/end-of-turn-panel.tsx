import { useState } from "react";
import { BOARD_SQUARES } from "#/components/game/board/board-data";
import { TradeDialog } from "#/components/game/trade-dialog";
import { Button } from "#/components/ui/button";
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

interface EndOfTurnPanelProps {
	userId: string | null;
	properties: Record<string, PropertyState>;
	players: Player[];
	sendAction: (msg: InboundMessage) => void;
}

export function EndOfTurnPanel({
	userId,
	properties,
	players,
	sendAction,
}: EndOfTurnPanelProps) {
	const [tradeOpen, setTradeOpen] = useState(false);

	const myProperties = Object.values(properties).filter(
		(p) => p.owner_id === userId,
	);

	const buildable = myProperties.filter((p) => !p.hotel && !p.mortgaged);
	const hotelable = myProperties.filter(
		(p) => p.houses === 4 && !p.hotel && !p.mortgaged,
	);
	const sellableHouses = myProperties.filter((p) => p.houses > 0);
	const sellableHotels = myProperties.filter((p) => p.hotel);
	const mortgageable = myProperties.filter(
		(p) => !p.mortgaged && p.houses === 0 && !p.hotel,
	);
	const unmortgageable = myProperties.filter((p) => p.mortgaged);

	const [selectedBuildHouse, setSelectedBuildHouse] = useState<number | null>(
		null,
	);
	const [selectedBuildHotel, setSelectedBuildHotel] = useState<number | null>(
		null,
	);
	const [selectedSellHouse, setSelectedSellHouse] = useState<number | null>(
		null,
	);
	const [selectedSellHotel, setSelectedSellHotel] = useState<number | null>(
		null,
	);
	const [selectedMortgage, setSelectedMortgage] = useState<number | null>(null);
	const [selectedUnmortgage, setSelectedUnmortgage] = useState<number | null>(
		null,
	);

	function squareName(idx: number) {
		return BOARD_SQUARES[idx]?.name ?? `Square ${idx}`;
	}

	const otherPlayers = players.filter((p) => p.player_id !== userId);

	return (
		<div className="flex flex-col gap-3">
			{buildable.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">
							Build house on
						</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedBuildHouse ?? ""}
							onChange={(e) =>
								setSelectedBuildHouse(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{buildable.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)} ({p.houses} 🏠)
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						disabled={selectedBuildHouse === null}
						onClick={() => {
							if (selectedBuildHouse !== null)
								sendAction({
									action: "build_house",
									property_index: selectedBuildHouse,
								});
						}}
					>
						Build 🏠
					</Button>
				</div>
			)}

			{hotelable.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">
							Build hotel on
						</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedBuildHotel ?? ""}
							onChange={(e) =>
								setSelectedBuildHotel(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{hotelable.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)}
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						disabled={selectedBuildHotel === null}
						onClick={() => {
							if (selectedBuildHotel !== null)
								sendAction({
									action: "build_hotel",
									property_index: selectedBuildHotel,
								});
						}}
					>
						Build 🏨
					</Button>
				</div>
			)}

			{sellableHouses.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">
							Sell house on
						</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedSellHouse ?? ""}
							onChange={(e) =>
								setSelectedSellHouse(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{sellableHouses.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)} ({p.houses} 🏠)
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						variant="outline"
						disabled={selectedSellHouse === null}
						onClick={() => {
							if (selectedSellHouse !== null)
								sendAction({
									action: "sell_house",
									property_index: selectedSellHouse,
								});
						}}
					>
						Sell 🏠
					</Button>
				</div>
			)}

			{sellableHotels.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">
							Sell hotel on
						</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedSellHotel ?? ""}
							onChange={(e) =>
								setSelectedSellHotel(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{sellableHotels.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)}
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						variant="outline"
						disabled={selectedSellHotel === null}
						onClick={() => {
							if (selectedSellHotel !== null)
								sendAction({
									action: "sell_hotel",
									property_index: selectedSellHotel,
								});
						}}
					>
						Sell 🏨
					</Button>
				</div>
			)}

			{mortgageable.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">Mortgage</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedMortgage ?? ""}
							onChange={(e) =>
								setSelectedMortgage(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{mortgageable.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)}
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						variant="outline"
						disabled={selectedMortgage === null}
						onClick={() => {
							if (selectedMortgage !== null)
								sendAction({
									action: "mortgage_property",
									property_index: selectedMortgage,
								});
						}}
					>
						Mortgage
					</Button>
				</div>
			)}

			{unmortgageable.length > 0 && (
				<div className="flex gap-2 items-end">
					<label className="flex-1">
						<span className="text-xs text-gray-500 mb-1 block">Unmortgage</span>
						<select
							className="w-full rounded-md border border-gray-200 px-2 py-1 text-xs"
							value={selectedUnmortgage ?? ""}
							onChange={(e) =>
								setSelectedUnmortgage(
									e.target.value ? Number(e.target.value) : null,
								)
							}
						>
							<option value="">Select property…</option>
							{unmortgageable.map((p) => (
								<option key={p.square_index} value={p.square_index}>
									{squareName(p.square_index)}
								</option>
							))}
						</select>
					</label>
					<Button
						size="sm"
						disabled={selectedUnmortgage === null}
						onClick={() => {
							if (selectedUnmortgage !== null)
								sendAction({
									action: "unmortgage_property",
									property_index: selectedUnmortgage,
								});
						}}
					>
						Unmortgage
					</Button>
				</div>
			)}

			{otherPlayers.length > 0 && (
				<Button variant="outline" onClick={() => setTradeOpen(true)}>
					🤝 Propose Trade
				</Button>
			)}
			{otherPlayers.length > 0 && (
				<TradeDialog
					open={tradeOpen}
					onOpenChange={setTradeOpen}
					userId={userId}
					myProperties={myProperties}
					players={players}
					allProperties={properties}
					sendAction={sendAction}
				/>
			)}

			<Button
				variant="destructive"
				size="sm"
				onClick={() => sendAction({ action: "declare_bankruptcy" })}
			>
				💀 Declare Bankruptcy
			</Button>

			<Button
				className="w-full"
				onClick={() => sendAction({ action: "end_turn" })}
			>
				⏭ End Turn
			</Button>
		</div>
	);
}
