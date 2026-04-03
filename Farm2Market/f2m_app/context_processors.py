from .models import Cart


def cart_count(request):
    """
    Injects `cart_count` (total number of distinct items in the buyer's cart)
    into every template context. Returns 0 for unauthenticated users or
    users who are not buyers.
    """
    count = 0
    if request.user.is_authenticated:
        try:
            buyer_profile = request.user.buyer_profile
            cart = Cart.objects.filter(buyer=buyer_profile).first()
            if cart:
                count = cart.items.count()
        except Exception:
            pass
    return {'cart_count': count}
