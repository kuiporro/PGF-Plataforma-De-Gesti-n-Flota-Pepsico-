# apps/workorders/middleware.py
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
import hashlib

class RateLimitMiddleware:
    """
    Middleware para rate limiting simple basado en IP
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuración: requests por minuto
        self.requests_per_minute = 60
        self.window_seconds = 60

    def __call__(self, request):
        # Solo aplicar rate limiting a endpoints de API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Obtener IP del cliente
        ip = self.get_client_ip(request)
        cache_key = f"ratelimit:{ip}"
        
        # Obtener contador actual
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.requests_per_minute:
            return JsonResponse(
                {"detail": "Rate limit exceeded. Please try again later."},
                status=429
            )
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, self.window_seconds)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def validate_file_upload(file, max_size_mb=10, allowed_types=None):
    """
    Valida un archivo subido
    - max_size_mb: Tamaño máximo en MB
    - allowed_types: Lista de tipos MIME permitidos (ej: ['image/jpeg', 'image/png', 'application/pdf'])
    """
    if allowed_types is None:
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/msword',  # .doc
        ]
    
    errors = []
    
    # Validar tamaño
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        errors.append(f"El archivo excede el tamaño máximo de {max_size_mb}MB")
    
    # Validar tipo MIME
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        errors.append(f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_types)}")
    
    # Validar extensión (backup)
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.doc', '.docx']
    file_name = file.name.lower()
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        errors.append(f"Extensión de archivo no permitida")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

