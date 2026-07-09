type GamePlayerProps = {
	playerName: string;
};

export function GamePlayer({ playerName }: GamePlayerProps) {
	return <div className="w-40 h-40 bg-red-700">{playerName}</div>;
}
