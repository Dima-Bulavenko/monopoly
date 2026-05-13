import type { JSX } from "react";
import { cn } from "#/lib/utils";
import { BOARD_SQUARES } from "./board-data";
import { BoardSquare } from "./board-square";

interface PlayerToken {
	playerId: string;
	name: string;
	colorIndex: number;
}

interface PropertyState {
	owner_id: string | null;
	houses: number;
	hotel: boolean;
	mortgaged: boolean;
}

interface BoardProps {
	playerPositions: Record<string, number>; // playerId → squareIndex
	playerNames: Record<string, string>; // playerId → name
	properties: Record<string, PropertyState>; // squareIndex (string) → state
	freeParkingPot: number;
	lastRoll: number[];
	phase: string;
	currentPlayerName: string | null;
}

// Board layout: 11x11 grid
// Index 0–10: bottom row (right→left), corners at [0,10]
// Index 11–19: left col (bottom→top)
// Index 20–30: top row (left→right), corners at [20,30]
// Index 31–39: right col (top→bottom)
//
// Grid positions (row, col), 0-indexed, row 0 = top
// Bottom row: row=10, col=10-i  (i=0..10)
// Left col:   col=0,  row=10-(i-10) = 20-i  (i=11..19)
// Top row:    row=0,  col=i-20  (i=20..30)
// Right col:  col=10, row=i-30  (i=31..39)

function squareGridPosition(index: number): {
	row: number;
	col: number;
	rotation: 0 | 90 | 180 | 270;
	isCorner: boolean;
} {
	if (index <= 10) {
		// bottom row, right→left
		return {
			row: 10,
			col: 10 - index,
			rotation: 180,
			isCorner: index === 0 || index === 10,
		};
	}
	if (index <= 19) {
		// left col, bottom→top
		return { row: 20 - index, col: 0, rotation: 90, isCorner: false };
	}
	if (index <= 30) {
		// top row, left→right
		return {
			row: 0,
			col: index - 20,
			rotation: 0,
			isCorner: index === 20 || index === 30,
		};
	}
	// right col, top→bottom
	return { row: index - 30, col: 10, rotation: 270, isCorner: false };
}

export function Board({
	playerPositions,
	playerNames,
	properties,
	freeParkingPot,
	lastRoll,
	phase,
	currentPlayerName,
}: BoardProps) {
	// Build token list per square
	const tokensBySquare: Record<number, PlayerToken[]> = {};
	const playerIds = Object.keys(playerPositions);
	for (const [idx, playerId] of playerIds.entries()) {
		const pos = playerPositions[playerId];
		if (pos === undefined) continue;
		if (!tokensBySquare[pos]) tokensBySquare[pos] = [];
		tokensBySquare[pos].push({
			playerId,
			name: playerNames[playerId] ?? "?",
			colorIndex: idx,
		});
	}

	// 11x11 grid cells
	const cells: JSX.Element[] = [];

	for (const sq of BOARD_SQUARES) {
		const { row, col, rotation, isCorner } = squareGridPosition(sq.index);
		const tokens = tokensBySquare[sq.index] ?? [];
		const propState = properties[String(sq.index)];

		cells.push(
			<div
				key={sq.index}
				className={cn(
					"overflow-hidden",
					isCorner ? "col-span-1 row-span-1" : "",
				)}
				style={{
					gridRow: row + 1,
					gridColumn: col + 1,
				}}
			>
				<BoardSquare
					square={sq}
					propertyState={propState}
					playerTokens={tokens}
					rotation={rotation}
					isCorner={isCorner}
				/>
			</div>,
		);
	}

	// Center panel occupies rows 2–10, cols 2–10 (1-indexed) = 9×9 inner
	const diceSum = lastRoll.length === 2 ? lastRoll[0] + lastRoll[1] : null;

	return (
		<div className="w-full overflow-auto rounded-xl border border-gray-300 bg-white p-1 shadow">
			<div
				className="grid"
				style={{
					display: "grid",
					gridTemplateRows: "repeat(11, 1fr)",
					gridTemplateColumns: "repeat(11, 1fr)",
					width: "min(90vw, 680px)",
					height: "min(90vw, 680px)",
					minWidth: "320px",
					minHeight: "320px",
				}}
			>
				{cells}

				{/* Center panel */}
				<div
					className="flex flex-col items-center justify-center gap-1 bg-green-50 p-2 text-center"
					style={{ gridRow: "2 / 11", gridColumn: "2 / 11" }}
				>
					<span className="text-xs font-bold text-green-800 uppercase tracking-wider">
						Monopoly
					</span>

					{diceSum !== null && diceSum > 0 && (
						<div className="flex items-center gap-1.5">
							{lastRoll.map((d, i) => (
								<div
									// biome-ignore lint/suspicious/noArrayIndexKey: static pair
									key={i}
									className="flex h-7 w-7 items-center justify-center rounded border-2 border-gray-400 bg-white text-base font-bold text-gray-800 shadow"
								>
									{d}
								</div>
							))}
						</div>
					)}

					{freeParkingPot > 0 && (
						<p className="text-[0.65rem] text-gray-600">
							Free Parking:{" "}
							<span className="font-semibold">${freeParkingPot}</span>
						</p>
					)}

					{currentPlayerName && (
						<p className="text-[0.65rem] text-gray-700">
							Turn: <span className="font-semibold">{currentPlayerName}</span>
						</p>
					)}

					<p className="text-[0.6rem] text-gray-500 capitalize">
						Phase: {phase.replace(/_/g, " ")}
					</p>
				</div>
			</div>
		</div>
	);
}
