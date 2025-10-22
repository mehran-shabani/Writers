import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const cookies = request.headers.get('cookie');
    
    if (!cookies) {
      return NextResponse.json(
        { detail: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Forward query parameters
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/api/v1/tasks${
      queryString ? `?${queryString}` : ''
    }`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Cookie': cookies,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Get tasks proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const cookies = request.headers.get('cookie');
    
    if (!cookies) {
      return NextResponse.json(
        { detail: 'Not authenticated' },
        { status: 401 }
      );
    }

    const contentType = request.headers.get('content-type');
    let body;
    let headers: HeadersInit = {
      'Cookie': cookies,
    };

    // Handle both JSON and FormData
    if (contentType?.includes('multipart/form-data')) {
      // For file uploads, pass through the formData
      const formData = await request.formData();
      body = formData;
      // Don't set content-type, let fetch set it with boundary
    } else {
      // For JSON data
      body = JSON.stringify(await request.json());
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${BACKEND_URL}/api/v1/tasks`, {
      method: 'POST',
      headers,
      body,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Create task proxy error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
}
