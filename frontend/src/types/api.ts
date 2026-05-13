// HTTP API types matching backend DTOs

export interface CreateGameRequest {
	max_players: number;
}

export interface GameResponse {
	game_id: string;
	status: string;
	player_count: number;
	max_players: number;
}

export interface GameStatePlayer {
	player_id: string;
	name: string;
	position: number;
	balance: number;
	in_jail: boolean;
	is_bankrupt: boolean;
	consecutive_doubles: number;
	jail_turns: number;
	get_out_of_jail_cards: number;
}

export interface GameStateProperty {
	square_index: number;
	owner_id: string | null;
	houses: number;
	hotel: boolean;
	mortgaged: boolean;
}

export interface GameStateResponse {
	game_id: string;
	status: string;
	phase: string;
	current_player_id: string | null;
	players: GameStatePlayer[];
	properties: Record<string, GameStateProperty>;
	free_parking_pot: number;
}

export interface AccessTokenResponse {
	access_token: string;
	token_type: string;
}

export interface RegisterRequest {
	email: string;
	password: string;
	display_name: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}
