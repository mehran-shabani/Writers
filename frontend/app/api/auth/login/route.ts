import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    // Create response with user data
    const nextResponse = NextResponse.json(data, { status: 200 });

    // Forward Set-Cookie headers from backend
    const responseHeaders = response.headers as unknown as {
      getSetCookie?: () => string[];
      raw?: () => Record<string, string[]>;
    };

    const setCookieHeaders =
      typeof responseHeaders.getSetCookie === 'function'
        ? responseHeaders.getSetCookie()
        : responseHeaders.raw?.()['set-cookie'];

    if (setCookieHeaders?.length) {
      for (const cookie of setCookieHeaders) {
        nextResponse.headers.append('Set-Cookie', cookie);
      }
    } else {
      const singleCookie = response.headers.get('set-cookie');
      if (singleCookie) {
        nextResponse.headers.append('Set-Cookie', singleCookie);
      }
    }

    return nextResponse;
  } catch (error) {
    console.error('Login proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
