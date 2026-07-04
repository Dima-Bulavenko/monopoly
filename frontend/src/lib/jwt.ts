import { jwtDecode } from "jwt-decode";

interface JwtPayload {
	sub: string;
	display_name?: string;
	exp?: number;
	[key: string]: unknown;
}

export function decodeJwtPayload(token: string): JwtPayload {
	const payload = jwtDecode<JwtPayload>(token);
	return payload;
}

export function isTokenExpired(token: string): boolean {
	try {
		const payload = decodeJwtPayload(token);
		if (!payload.exp) return false;
		return Date.now() / 1000 > payload.exp;
	} catch {
		return true;
	}
}
