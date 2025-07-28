# tochinalli_project/ixcaui_app/middleware.py

from .managers import set_current_request, clear_current_request

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request) # Guarda el request en el hilo
        try:
            response = self.get_response(request)
        finally:
            clear_current_request() # Limpia el request al finalizar la solicitud
        return response