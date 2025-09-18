// utils/auth.ts
import type { TokenPayload } from "../types/tokenyPayload";

export function decodeJWT(token: string): TokenPayload | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload) return true;
  
  const currentTime = Date.now() / 1000; // Convert to seconds
  return payload.exp < currentTime;
}

export function isUserLoggedIn(): boolean {
  const token = localStorage.getItem('access_token');
  
  if (!token) return false;
  if (isTokenExpired(token)) {
    // Clean up expired token
    localStorage.removeItem('access_token');
    return false;
  }
  return true;
}

export function getCurrentUser(): TokenPayload | null {
  const token = localStorage.getItem('access_token');
  if (!token || isTokenExpired(token)) return null;
  return decodeJWT(token);
}

export async function verifyTokenWithAPI(): Promise<TokenPayload | null> {
  const token = localStorage.getItem('access_token');
  if (!token) return null;

  try {
    const response = await fetch('/auth/verify-token', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      localStorage.removeItem('access_token');
      return null;
    }

    const data = await response.json();
    return data.user;
  } catch {
    localStorage.removeItem('access_token');
    return null;
  }
}