import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AuthProvider, useAuth } from '@/contexts/AuthContext';

// Mock fetch
global.fetch = jest.fn();

// Test component
function TestComponent() {
  const { user, login, logout, isAuthenticated, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>
      <div data-testid="user-email">{user?.email || 'No user'}</div>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

describe('Authentication', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should login successfully', async () => {
    const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', email: 'test@example.com' }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'token' }),
      } as Response);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    await userEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });
  });

  test('should handle login error', async () => {
    const mockFetch = fetch as jest.MockedFunction<typeof fetch>;
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
    } as Response);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');

    // Should not throw error, but handle gracefully
    await userEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });
  });
});
