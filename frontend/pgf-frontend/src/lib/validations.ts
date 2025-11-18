// Validaciones reutilizables para formularios

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export function validateRequired(value: any, fieldName: string): string | null {
  if (!value || (typeof value === "string" && value.trim() === "")) {
    return `${fieldName} es requerido`;
  }
  return null;
}

export function validateEmail(email: string): string | null {
  if (!email) return null; // Si está vacío, se valida con validateRequired
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return "Email inválido";
  }
  return null;
}

export function validateMinLength(value: string, min: number, fieldName: string): string | null {
  if (value && value.length < min) {
    return `${fieldName} debe tener al menos ${min} caracteres`;
  }
  return null;
}

export function validateMaxLength(value: string, max: number, fieldName: string): string | null {
  if (value && value.length > max) {
    return `${fieldName} no puede tener más de ${max} caracteres`;
  }
  return null;
}

export function validateNumber(value: any, fieldName: string, min?: number, max?: number): string | null {
  const num = Number(value);
  if (isNaN(num)) {
    return `${fieldName} debe ser un número`;
  }
  if (min !== undefined && num < min) {
    return `${fieldName} debe ser mayor o igual a ${min}`;
  }
  if (max !== undefined && num > max) {
    return `${fieldName} debe ser menor o igual a ${max}`;
  }
  return null;
}

export function validatePatente(patente: string): string | null {
  if (!patente) return null;
  // Formato chileno: ABC123 o ABC-123 o ABC1234
  const patenteRegex = /^[A-Z]{2,3}[0-9]{3,4}$|^[A-Z]{2,3}-[0-9]{3,4}$/;
  if (!patenteRegex.test(patente.toUpperCase().replace(/\s/g, ""))) {
    return "Formato de patente inválido (ej: ABC123 o ABC-123)";
  }
  return null;
}

export function validateYear(year: string | number): string | null {
  const currentYear = new Date().getFullYear();
  const yearNum = typeof year === "string" ? parseInt(year) : year;
  
  if (isNaN(yearNum)) {
    return "Año inválido";
  }
  if (yearNum < 1900 || yearNum > currentYear + 1) {
    return `Año debe estar entre 1900 y ${currentYear + 1}`;
  }
  return null;
}

// Validación de formulario de vehículo
export function validateVehicle(form: {
  patente: string;
  marca: string;
  modelo: string;
  anio: string | number;
}): ValidationResult {
  const errors: Record<string, string> = {};

  const patenteError = validateRequired(form.patente, "Patente") || validatePatente(form.patente);
  if (patenteError) errors.patente = patenteError;

  const marcaError = validateRequired(form.marca, "Marca");
  if (marcaError) errors.marca = marcaError;

  const modeloError = validateRequired(form.modelo, "Modelo");
  if (modeloError) errors.modelo = modeloError;

  const anioError = validateRequired(form.anio, "Año") || validateYear(form.anio);
  if (anioError) errors.anio = anioError;

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

// Validación de formulario de orden de trabajo
export function validateWorkOrder(form: {
  vehiculo: string | number;
  tipo: string;
  prioridad: string;
  motivo: string;
  items?: Array<{
    tipo: string;
    descripcion: string;
    cantidad: number;
    costo_unitario: number;
  }>;
}): ValidationResult {
  const errors: Record<string, string> = {};

  if (!form.vehiculo || form.vehiculo === "") {
    errors.vehiculo = "Debe seleccionar un vehículo";
  }

  const motivoError = validateRequired(form.motivo, "Motivo");
  if (motivoError) errors.motivo = motivoError;

  if (form.items && form.items.length > 0) {
    form.items.forEach((item, index) => {
      if (!item.descripcion || item.descripcion.trim() === "") {
        errors[`items.${index}.descripcion`] = "La descripción del item es requerida";
      }
      if (item.cantidad <= 0) {
        errors[`items.${index}.cantidad`] = "La cantidad debe ser mayor a 0";
      }
      if (item.costo_unitario < 0) {
        errors[`items.${index}.costo_unitario`] = "El costo no puede ser negativo";
      }
    });
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

