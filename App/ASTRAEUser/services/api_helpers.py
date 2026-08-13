"""JSON API helpers for ASTRAE."""
import json
from django.http import JsonResponse


def api_success(data=None, message=''):
    return JsonResponse({'success': True, 'data': data or {}, 'message': message})


def api_error(message, status=400, data=None):
    return JsonResponse({'success': False, 'error': message, 'data': data or {}}, status=status)
