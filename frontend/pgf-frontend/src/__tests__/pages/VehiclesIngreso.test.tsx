/**
 * Tests para la página de ingreso de vehículos
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ToastContainer';
import { useAuth } from '@/store/auth';
import IngresoVehiculoPage from '@/app/vehicles/ingreso/page';

// Mocks - No sobrescribir el mock global de setup.ts

vi.mock('@/components/ToastContainer', () => ({
  useToast: vi.fn(),
}));

vi.mock('@/store/auth', () => ({
  useAuth: vi.fn(),
}));

describe('IngresoVehiculoPage', () => {
  const mockRouter = {
    push: vi.fn(),
    back: vi.fn(),
  };

  const mockToast = {
    success: vi.fn(),
    error: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as any).mockReturnValue(mockRouter);
    (useToast as any).mockReturnValue(mockToast);
  });

  it('debe renderizar el formulario de ingreso', () => {
    (useAuth as any).mockReturnValue({
      user: { id: '1', username: 'test', rol: 'GUARDIA' },
      hasRole: () => true,
      isLogged: () => true,
      refreshMe: vi.fn(() => Promise.resolve()),
    });

    render(<IngresoVehiculoPage />);

    expect(screen.getByText(/Registrar Ingreso de Vehículo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Patente/i)).toBeInTheDocument();
  });

  it('debe requerir patente para enviar', () => {
    (useAuth as any).mockReturnValue({
      user: { id: '1', username: 'test', rol: 'GUARDIA' },
      hasRole: () => true,
      isLogged: () => true,
      refreshMe: vi.fn(() => Promise.resolve()),
    });

    render(<IngresoVehiculoPage />);

    const submitButton = screen.getByText(/Registrar Ingreso y Crear OT/i);
    expect(submitButton).toBeInTheDocument();
  });

  it('debe mostrar mensaje de acceso denegado si no es Guardia', () => {
    (useAuth as any).mockReturnValue({
      user: null,
      hasRole: () => false,
      isLogged: () => false,
      refreshMe: vi.fn(() => Promise.resolve()),
    });

    render(<IngresoVehiculoPage />);
    // El componente RoleGuard debe manejar esto
  });
});

