from .models import SystemSetting

def global_system_settings(request):
    """Makes configuration rules available globally to all templates."""
    return {
        'config': SystemSetting.load()
    }