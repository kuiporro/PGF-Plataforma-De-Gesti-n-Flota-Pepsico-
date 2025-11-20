/**
 * Tests para la página de timeline de OT
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { useRouter, useParams } from 'next/navigation';
import { useToast } from '@/components/ToastContainer';
import { useAuth } from '@/store/auth';
import TimelineOTPage from '@/app/workorders/[id]/timeline/page';

// Mocks
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  useParams: vi.fn(),
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

describe('TimelineOTPage', () => {
  const mockToast = {
    success: vi.fn(),
    error: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useToast as any).mockReturnValue(mockToast);
    // useParams ya está mockeado en setup.ts, solo necesitamos sobrescribir el valor
    vi.mocked(useParams).mockReturnValue({ id: 'test-ot-id' } as any);
    (useAuth as any).mockReturnValue({
      user: { id: '1', username: 'test', rol: 'MECANICO' },
      hasRole: () => true,
      isLogged: () => true,
      refreshMe: vi.fn(() => Promise.resolve()),
    });
  });

  it('debe renderizar el título de timeline', () => {
    render(<TimelineOTPage />);
    expect(screen.getByText(/Timeline de la OT/i)).toBeInTheDocument();
  });

  it('debe mostrar estado de carga inicialmente', () => {
    render(<TimelineOTPage />);
    // El componente debe mostrar loading state
  });
});

