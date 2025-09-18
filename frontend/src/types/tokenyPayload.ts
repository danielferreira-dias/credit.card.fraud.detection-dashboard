export interface TokenPayload {
  sub: string;
  email: string;
  name: string;
  exp: number; // Expiration timestamp
}