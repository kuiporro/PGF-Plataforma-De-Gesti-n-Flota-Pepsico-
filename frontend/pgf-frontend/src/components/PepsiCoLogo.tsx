/**
 * Componente de Logo PepsiCo
 * 
 * Muestra el logo de PepsiCo de forma profesional.
 * Soporta diferentes tamaños y variantes.
 */

"use client";

import Image from "next/image";

interface PepsiCoLogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  variant?: "default" | "white" | "dark";
  className?: string;
  showText?: boolean;
}

const sizeClasses = {
  sm: "h-8 w-8",
  md: "h-12 w-12",
  lg: "h-16 w-16",
  xl: "h-24 w-24",
};

export default function PepsiCoLogo({
  size = "md",
  variant = "default",
  className = "",
  showText = false,
}: PepsiCoLogoProps) {
  // SVG del logo PepsiCo (globo con bandas de colores) - Alta resolución
  const logoPath = (
    <svg
      viewBox="0 0 400 400"
      className={`${sizeClasses[size]} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        {/* Gradientes para profundidad */}
        <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#00B4E6" stopOpacity="1" />
          <stop offset="100%" stopColor="#0099CC" stopOpacity="1" />
        </linearGradient>
        <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FF6B35" stopOpacity="1" />
          <stop offset="100%" stopColor="#FF5500" stopOpacity="1" />
        </linearGradient>
        <linearGradient id="greenGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#00A859" stopOpacity="1" />
          <stop offset="100%" stopColor="#008744" stopOpacity="1" />
        </linearGradient>
        <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#E60012" stopOpacity="1" />
          <stop offset="100%" stopColor="#CC0010" stopOpacity="1" />
        </linearGradient>
      </defs>
      
      {/* Fondo del globo - líneas de meridiano y paralelo más detalladas */}
      <g stroke="#003DA5" strokeWidth="1.5" fill="none" opacity="0.25">
        {/* Meridianos verticales - más precisos */}
        <path d="M 200 40 Q 240 100 200 160 Q 160 100 200 40" />
        <path d="M 200 40 Q 260 120 200 200 Q 140 120 200 40" />
        <path d="M 200 40 Q 280 140 200 240 Q 120 140 200 40" />
        <path d="M 200 40 Q 300 160 200 280 Q 100 160 200 40" />
        <path d="M 200 40 Q 320 180 200 320 Q 80 180 200 40" />
        <path d="M 200 40 Q 340 200 200 360 Q 60 200 200 40" />
        
        {/* Paralelos horizontales - más precisos */}
        <ellipse cx="200" cy="120" rx="60" ry="20" />
        <ellipse cx="200" cy="200" rx="80" ry="30" />
        <ellipse cx="200" cy="280" rx="70" ry="24" />
        <ellipse cx="200" cy="360" rx="50" ry="16" />
      </g>
      
      {/* Bandas de colores con gradientes y sombras */}
      {/* Banda azul claro (superior) */}
      <path
        d="M 100 120 Q 200 80 300 120 Q 200 160 100 120"
        fill="url(#blueGradient)"
        stroke="#003DA5"
        strokeWidth="0.5"
        opacity="0.95"
      />
      <path
        d="M 100 120 Q 200 80 300 120"
        fill="none"
        stroke="#00B4E6"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Banda naranja */}
      <path
        d="M 90 200 Q 200 170 310 200 Q 200 230 90 200"
        fill="url(#orangeGradient)"
        stroke="#FF6B35"
        strokeWidth="0.5"
        opacity="0.95"
      />
      <path
        d="M 90 200 Q 200 170 310 200"
        fill="none"
        stroke="#FF6B35"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Banda verde */}
      <path
        d="M 80 280 Q 200 250 320 280 Q 200 310 80 280"
        fill="url(#greenGradient)"
        stroke="#00A859"
        strokeWidth="0.5"
        opacity="0.95"
      />
      <path
        d="M 80 280 Q 200 250 320 280"
        fill="none"
        stroke="#00A859"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Banda roja (inferior) */}
      <path
        d="M 70 360 Q 200 330 330 360 Q 200 390 70 360"
        fill="url(#redGradient)"
        stroke="#E60012"
        strokeWidth="0.5"
        opacity="0.95"
      />
      <path
        d="M 70 360 Q 200 330 330 360"
        fill="none"
        stroke="#E60012"
        strokeWidth="1"
        opacity="0.3"
      />
      
      {/* Efectos de brillo sutiles */}
      <ellipse cx="200" cy="120" rx="40" ry="8" fill="white" opacity="0.2" />
      <ellipse cx="200" cy="200" rx="50" ry="10" fill="white" opacity="0.15" />
      <ellipse cx="200" cy="280" rx="45" ry="9" fill="white" opacity="0.15" />
    </svg>
  );

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {logoPath}
      {showText && (
        <span
          className={`font-bold ${
            variant === "white"
              ? "text-white"
              : variant === "dark"
              ? "text-gray-900 dark:text-white"
              : "text-[#003DA5] dark:text-white"
          } ${
            size === "sm"
              ? "text-sm"
              : size === "md"
              ? "text-base"
              : size === "lg"
              ? "text-xl"
              : "text-2xl"
          }`}
        >
          PepsiCo
        </span>
      )}
    </div>
  );
}

