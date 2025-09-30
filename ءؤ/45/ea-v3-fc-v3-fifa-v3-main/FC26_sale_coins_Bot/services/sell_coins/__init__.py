# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 FC26 COIN SELLING SERVICE - خدمة بيع الكوينز             ║
# ║                     Coin Selling Service Package                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Import only when telegram is available
def _import_telegram_components():
    """Import telegram-dependent components"""
    try:
        from .sell_handler import SellCoinsHandler
        from .sell_keyboards import SellKeyboards
        from .sell_conversation_handler import SellConversationHandler
        from .sell_conversation_functions import get_sell_conversation_handler, sell_command
        from .sell_callbacks import handle_sell_callbacks
        return SellCoinsHandler, SellKeyboards, SellConversationHandler, get_sell_conversation_handler, sell_command, handle_sell_callbacks
    except ImportError:
        return None, None, None, None, None, None

# Always available imports (no telegram dependency)
from .sell_pricing import CoinSellPricing, Platform
from .sell_messages import SellMessages

# Conditional imports
SellCoinsHandler, SellKeyboards, SellConversationHandler, get_sell_conversation_handler, sell_command, handle_sell_callbacks = _import_telegram_components()

__all__ = [
    'CoinSellPricing',
    'Platform', 
    'SellMessages'
]

# Add telegram-dependent components if available
if SellCoinsHandler is not None:
    __all__.extend([
        'SellCoinsHandler', 
        'SellKeyboards', 
        'SellConversationHandler', 
        'get_sell_conversation_handler', 
        'sell_command', 
        'handle_sell_callbacks'
    ])