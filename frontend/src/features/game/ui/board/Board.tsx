import { useSuspenseQuery } from "@tanstack/react-query";
import { getBoardOptions } from "#/features/game/api/queryOptions";
import { BoardSquare } from "./Square";

type Side = "bottom" | "top" | "left" | "right" | "corner";
type SquarePosition = { col: number; row: number; side: Side };

function squarePosition(index: number): SquarePosition {
	if (index === 0) return { col: 11, row: 11, side: "corner" };
	if (index >= 1 && index <= 9)
		return { col: 10 - (index - 1), row: 11, side: "bottom" };
	if (index === 10) return { col: 1, row: 11, side: "corner" };
	if (index >= 11 && index <= 19)
		return { col: 1, row: 10 - (index - 11), side: "left" };
	if (index === 20) return { col: 1, row: 1, side: "corner" };
	if (index >= 21 && index <= 29)
		return { col: 1 + (index - 20), row: 1, side: "top" };
	if (index === 30) return { col: 11, row: 1, side: "corner" };
	// squares 31–39: right column, top to bottom
	return { col: 11, row: 1 + (index - 30), side: "right" };
}

export function Board() {
	const { data } = useSuspenseQuery(getBoardOptions());

	return (
		<div
			className="aspect-square w-full max-h-screen border-2 border-black"
			style={{
				display: "grid",
				gridTemplateColumns: "2fr repeat(9, 1fr) 2fr",
				gridTemplateRows: "2fr repeat(9, 1fr) 2fr",
			}}
		>
			{/* Center area */}
			<div
				className="bg-emerald-100 flex items-center justify-center"
				style={{ gridColumn: "2 / 11", gridRow: "2 / 11" }}
			>
				<span
					className="font-extrabold tracking-widest text-emerald-800"
					style={{ fontSize: "clamp(12px, 4cqi, 48px)" }}
				>
					MONOPOLY
				</span>
			</div>

			{data.board.map((square) => {
				const { col, row, side } = squarePosition(square.index);
				return (
					<BoardSquare
						key={square.index}
						square={square}
						side={side}
						style={{ gridColumn: col, gridRow: row }}
					/>
				);
			})}
		</div>
	);
}
