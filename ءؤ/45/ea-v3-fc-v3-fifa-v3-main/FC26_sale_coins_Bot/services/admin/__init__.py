# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              👑 FC26 ADMIN SERVICE - خدمة الادارة                       ║
# ║                     Admin Service Package                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def _import_admin_components():
    """Import admin components safely"""
    try:
        from .admin_handler import AdminHandler
        from .admin_keyboards import AdminKeyboards
        from .admin_messages import AdminMessages
        from .price_management import PriceManagement
        return AdminHandler, AdminKeyboards, AdminMessages, PriceManagement
    except ImportError:
        return None, None, None, None

# Import components
AdminHandler, AdminKeyboards, AdminMessages, PriceManagement = _import_admin_components()

__all__ = []

# Add components if available
if AdminHandler is not None:
    __all__.extend(['AdminHandler', 'AdminKeyboards', 'AdminMessages', 'PriceManagement'])