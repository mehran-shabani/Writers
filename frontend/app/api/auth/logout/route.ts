import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    // Get cookies from the request
    const cookies = request.headers.get('cookie');
    
    const response = await fetch(`${BACKEND_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(cookies && { 'Cookie': cookies }),
      },
    });

    const data = response.ok ? await response.json() : { detail: 'Logout failed' };

    // Create response
    const nextResponse = NextResponse.json(data, { status: response.status });

    // Forward Set-Cookie headers (to clear cookies)
    const setCookies = response.headers.get('set-cookie');
    if (setCookies) {
      nextResponse.headers.set('Set-Cookie', setCookies);
    }

    return nextResponse;
  } catch (error) {
    console.error('Logout proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
