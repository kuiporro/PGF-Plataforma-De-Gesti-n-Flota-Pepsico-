/**
 * Componente PasswordInput con funcionalidad de mostrar/ocultar contraseña
 * 
 * Características:
 * - Botón para alternar visibilidad de la contraseña
 * - Iconos de ojo abierto/cerrado
 * - Diseño consistente con el resto del sistema
 */

"use client";

import { useState } from "react";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";

interface PasswordInputProps {
  id?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  required?: boolean;
  autoComplete?: string;
  label?: string;
  error?: string;
  minLength?: number;
}

export default function PasswordInput({
  id = "password",
  value,
  onChange,
  placeholder = "Ingresa tu contraseña",
  className = "",
  required = false,
  autoComplete = "current-password",
  label,
  error,
  minLength,
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          id={id}
          type={showPassword ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          minLength={minLength}
          autoComplete={autoComplete}
          className={`w-full px-4 py-3 pr-12 border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-[#003DA5] focus:border-[#003DA5] dark:bg-gray-700 dark:text-white transition-all ${className} ${
            error ? "border-red-500 focus:ring-red-500 focus:border-red-500" : ""
          }`}
        />
        <button
          type="button"
          onClick={togglePasswordVisibility}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 focus:outline-none transition-colors"
          aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
        >
          {showPassword ? (
            <EyeSlashIcon className="h-5 w-5" />
          ) : (
            <EyeIcon className="h-5 w-5" />
          )}
        </button>
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
    </div>
  );
}

