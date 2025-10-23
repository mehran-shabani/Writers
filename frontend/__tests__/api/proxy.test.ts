/**
 * Integration tests for API proxy routes
 * These tests verify that the Next.js API routes properly proxy requests to FastAPI
 */

import { NextRequest } from 'next/server';
import { POST as loginPost } from '@/app/api/auth/login/route';
import { POST as registerPost } from '@/app/api/auth/register/route';
import { GET as meGet } from '@/app/api/auth/me/route';
import { POST as logoutPost } from '@/app/api/auth/logout/route';

const getSetCookieArray = (headers: Headers): string[] => {
  const extendedHeaders = headers as unknown as {
    getSetCookie?: () => string[];
    raw?: () => Record<string, string[]>;
  };

  if (typeof extendedHeaders.getSetCookie === 'function') {
    return extendedHeaders.getSetCookie();
  }

  const rawCookies = extendedHeaders.raw?.()['set-cookie'];
  if (rawCookies?.length) {
    return rawCookies;
  }

  const singleCookie = headers.get('set-cookie');
  return singleCookie ? [singleCookie] : [];
};

// Mock fetch globally
global.fetch = jest.fn();

describe('API Proxy Routes', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /api/auth/login', () => {
    it('should proxy login request and forward cookies', async () => {
      const headers = new Headers();
      headers.append('set-cookie', 'access_token=abc123; HttpOnly; Secure');
      headers.append('set-cookie', 'refresh_token=def456; HttpOnly; Secure');

      const mockResponse = {
        ok: true,
        status: 200,
        json: async () => ({
          user: { id: 1, email: 'test@example.com', username: 'testuser' },
          token_type: 'bearer',
        }),
        headers,
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'password123' }),
      });

      const response = await loginPost(request);
      const data = await response.json();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
      expect(response.status).toBe(200);
      expect(data).toHaveProperty('user');
      expect(data.user).toHaveProperty('id');
      const forwardedCookies = getSetCookieArray(response.headers);
      expect(forwardedCookies).toEqual(
        expect.arrayContaining([
          expect.stringContaining('access_token=abc123'),
          expect.stringContaining('refresh_token=def456'),
        ])
      );
    });

    it('should handle login errors gracefully', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' }),
        headers: new Headers(),
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'wrong' }),
      });

      const response = await loginPost(request);
      const data = await response.json();

      expect(response.status).toBe(401);
      expect(data.detail).toBe('Invalid credentials');
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const request = new NextRequest('http://localhost:3000/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: 'test@example.com', password: 'password123' }),
      });

      const response = await loginPost(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.detail).toBe('Internal server error');
    });
  });

  describe('POST /api/auth/register', () => {
    it('should proxy register request and forward cookies', async () => {
      const headers = new Headers();
      headers.append('set-cookie', 'access_token=xyz789; HttpOnly; Secure');
      headers.append('set-cookie', 'refresh_token=rst987; HttpOnly; Secure');

      const mockResponse = {
        ok: true,
        status: 201,
        json: async () => ({
          user: { id: 1, email: 'new@example.com', username: 'newuser' },
          token_type: 'bearer',
        }),
        headers,
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const request = new NextRequest('http://localhost:3000/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          email: 'new@example.com',
          username: 'newuser',
          password: 'password123',
        }),
      });

      const response = await registerPost(request);
      const data = await response.json();

      expect(response.status).toBe(201);
      expect(data).toHaveProperty('user');
      expect(data.user).toHaveProperty('id');
      const forwardedCookies = getSetCookieArray(response.headers);
      expect(forwardedCookies).toEqual(
        expect.arrayContaining([
          expect.stringContaining('access_token=xyz789'),
          expect.stringContaining('refresh_token=rst987'),
        ])
      );
    });
  });

  describe('GET /api/auth/me', () => {
    it('should require authentication cookie', async () => {
      const request = new NextRequest('http://localhost:3000/api/auth/me', {
        method: 'GET',
      });

      const response = await meGet(request);
      const data = await response.json();

      expect(response.status).toBe(401);
      expect(data.detail).toBe('Not authenticated');
    });

    it('should proxy authenticated request', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        json: async () => ({ id: 1, email: 'test@example.com', username: 'testuser' }),
        headers: new Headers(),
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const request = new NextRequest('http://localhost:3000/api/auth/me', {
        method: 'GET',
        headers: {
          cookie: 'access_token=abc123',
        },
      });

      const response = await meGet(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data).toHaveProperty('id');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Cookie: 'access_token=abc123',
          }),
        })
      );
    });
  });

  describe('POST /api/auth/logout', () => {
    it('should proxy logout and clear cookies', async () => {
      const headers = new Headers();
      headers.append('set-cookie', 'access_token=; Max-Age=0');
      headers.append('set-cookie', 'refresh_token=; Max-Age=0');

      const mockResponse = {
        ok: true,
        status: 200,
        json: async () => ({ message: 'Logged out successfully' }),
        headers,
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const request = new NextRequest('http://localhost:3000/api/auth/logout', {
        method: 'POST',
        headers: {
          cookie: 'access_token=abc123',
        },
      });

      const response = await logoutPost(request);

      expect(response.status).toBe(200);
      const forwardedCookies = getSetCookieArray(response.headers);
      expect(forwardedCookies).toEqual(
        expect.arrayContaining([
          expect.stringContaining('access_token='),
          expect.stringContaining('refresh_token='),
        ])
      );
    });
  });
});
