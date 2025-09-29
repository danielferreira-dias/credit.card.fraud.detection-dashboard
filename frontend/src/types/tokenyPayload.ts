export interface TokenPayload {
  id: number;
  sub: string;
  email: string;
  name: string;
  exp: number; // Expiration timestamp
}