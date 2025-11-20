/**
 * Tests para el dashboard de Jefe de Taller
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ToastContainer';
import { useAuth } from '@/store/auth';
import JefeTallerDashboardPage from '@/app/jefe-taller/dashboard/page';

// Mocks
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

vi.mock('@/components/ToastContainer', () => ({
  useToast: vi.fn(),
}));

vi.mock('@/store/auth', () => ({
  useAuth: vi.fn(),
}));

vi.mock('@/lib/api.client', () => ({
  withSession: () => ({}),
}));

describe('JefeTallerDashboardPage', () => {
  const mockToast = {
    success: vi.fn(),
    error: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useToast as any).mockReturnValue(mockToast);
    (useAuth as any).mockReturnValue({
      user: { id: '1', username: 'test', rol: 'JEFE_TALLER' },
      hasRole: () => true,
      isLogged: () => true,
      refreshMe: vi.fn(() => Promise.resolve()),
    });
  });

  it('debe renderizar el título del dashboard', () => {
    render(<JefeTallerDashboardPage />);
    expect(screen.getByText(/Dashboard del Taller/i)).toBeInTheDocument();
  });

  it('debe mostrar KPIs del taller', () => {
    render(<JefeTallerDashboardPage />);
    // Verificar que se muestran los KPIs
    expect(screen.getByText(/OTs Abiertas/i)).toBeInTheDocument();
  });
});

