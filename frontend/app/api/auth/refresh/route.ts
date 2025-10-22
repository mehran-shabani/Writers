import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    // Get cookies from the request
    const cookies = request.headers.get('cookie');
    
    if (!cookies) {
      return NextResponse.json(
        { detail: 'No refresh token found' },
        { status: 401 }
      );
    }

    const response = await fetch(`${BACKEND_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': cookies,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    // Create response
    const nextResponse = NextResponse.json(data, { status: 200 });

    // Forward Set-Cookie headers (new access token)
    const setCookies = response.headers.get('set-cookie');
    if (setCookies) {
      nextResponse.headers.set('Set-Cookie', setCookies);
    }

    return nextResponse;
  } catch (error) {
    console.error('Refresh token proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
