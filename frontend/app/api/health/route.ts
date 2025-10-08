import { NextResponse } from 'next/server';
import type { HealthCheckResponse, BaseAPIResponse } from '@/types/api';

export async function GET(): Promise<NextResponse<HealthCheckResponse | BaseAPIResponse>> {
  try {
    // In Docker environment, we need to use the service name
    // This is a Server Component, so we're making this request from the container
    const apiUrl = 'http://backend:8000';

    console.log(`Checking backend health at: ${apiUrl}`);

    // Attempt to connect to the backend
    const response = await fetch(`${apiUrl}/`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          status: 'error',
          message: `Backend connection failed with status: ${response.status}`,
          backendUrl: apiUrl,
          timestamp: new Date().toISOString(),
        } as BaseAPIResponse,
        { status: 500 }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      status: 'ok',
      backend: data,
      backendUrl: apiUrl,
      timestamp: new Date().toISOString(),
    } as HealthCheckResponse);
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      {
        status: 'error',
        message: error instanceof Error ? error.message : 'Unknown error connecting to backend',
        backendUrl: 'http://backend:8000',
        timestamp: new Date().toISOString(),
      } as BaseAPIResponse,
      { status: 500 }
    );
  }
}
