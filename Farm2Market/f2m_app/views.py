from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FarmerProfile, BuyerProfile, Product, Category, Cart, CartItem
from django.db.models import Count, Q


# REGISTER VIEW
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        # Basic Validation
        if not password or password != confirm_password:
            messages.error(request, "Passwords are required and must match.")
            return redirect("register_view")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register_view")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register_view")

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Profile Based on Role
        if role == "farmer":
            farm_name = request.POST.get("farm_name")
            farm_location = request.POST.get("farm_location")
            bio = request.POST.get("bio")

            if not farm_name or not farm_location:
                messages.error(request, "Farm name and location are required.")
                user.delete()
                return redirect("register_view")

            FarmerProfile.objects.create(
                user=user,
                farm_name=farm_name,
                farm_location=farm_location,
                bio=bio
            )

        elif role == "buyer":
            delivery_address = request.POST.get("delivery_address")

            if not delivery_address:
                messages.error(request, "Delivery address is required.")
                user.delete()
                return redirect("register_view")

            BuyerProfile.objects.create(
                user=user,
                delivery_address=delivery_address
            )
        else:
            user.delete()
            messages.error(request, "Invalid role selected.")
            return redirect("register_view")

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login_view")

    return render(request, "F2M/register.html")



# LOGIN VIEW
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Merge session cart into database cart
            session_cart = request.session.get('cart', {})
            if session_cart and hasattr(user, 'buyer_profile'):
                buyer_profile = user.buyer_profile
                cart, created = Cart.objects.get_or_create(buyer=buyer_profile)
                
                for product_id, quantity in session_cart.items():
                    try:
                        product = Product.objects.get(product_id=product_id)
                        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
                        if not item_created:
                            cart_item.quantity = min(cart_item.quantity + quantity, product.stock_quantity)
                        else:
                            cart_item.quantity = min(quantity, product.stock_quantity)
                        cart_item.save()
                    except Product.DoesNotExist:
                        continue
                
                # Clear session cart after merging
                del request.session['cart']

            if hasattr(user, 'farmer_profile'):
                return redirect("farmer_dashboard_view")
            else:
                return redirect("home_view")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login_view")

    return render(request, "F2M/login.html")


# LOGOUT VIEW
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("home_view")


# HOME VIEW
def home_view(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, "F2M/home.html", context)


# PRODUCT LIST VIEW
def product_list_view(request):
    products = Product.objects.select_related('farmer', 'category').all().order_by('-created_at')
    categories = Category.objects.all()
    selected_category = None
    
    category_id = request.GET.get('category')
    if category_id:
        try:
            selected_category = Category.objects.get(category_id=category_id)
            products = products.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, "F2M/products.html", context)


# DASHBOARD VIEWS
@login_required
def farmer_dashboard_view(request):
    try:
        farmer_profile = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "You must be a farmer to view this page.")
        return redirect('home_view')

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_product":
            category_id = request.POST.get("category")
            name = request.POST.get("name")
            description = request.POST.get("description")
            price_per_unit = request.POST.get("price_per_unit")
            stock_quantity = request.POST.get("stock_quantity")
            unit = request.POST.get("unit")
            image = request.FILES.get("image")
            
            try:
                category = Category.objects.get(category_id=category_id)
                Product.objects.create(
                    farmer=farmer_profile,
                    category=category,
                    name=name,
                    description=description,
                    price_per_unit=price_per_unit,
                    stock_quantity=stock_quantity,
                    unit=unit,
                    image=image
                )
                messages.success(request, "Product added successfully!")
            except Exception as e:
                messages.error(request, f"Error adding product: {str(e)}")
            
            return redirect('farmer_dashboard_view')

    products = Product.objects.select_related('category').filter(farmer=farmer_profile).order_by('-created_at')
    categories = Category.objects.all()

    stats = products.aggregate(
        in_stock=Count('product_id', filter=Q(stock_quantity__gt=0)),
        out_stock=Count('product_id', filter=Q(stock_quantity=0))
    )
    in_stock_count = stats['in_stock'] or 0
    out_of_stock_count = stats['out_stock'] or 0

    context = {
        'products': products,
        'categories': categories,
        'in_stock_count': in_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, "F2M/farmer_dashboard.html", context)


@login_required
def edit_product_view(request, product_id):
    try:
        farmer_profile = request.user.farmer_profile
    except FarmerProfile.DoesNotExist:
        messages.error(request, "You must be a farmer to edit products.")
        return redirect('home_view')
        
    try:
        product = Product.objects.get(product_id=product_id, farmer=farmer_profile)
    except Product.DoesNotExist:
        messages.error(request, "Product not found or you don't have permission to edit it.")
        return redirect('farmer_dashboard_view')
        
    if request.method == "POST":
        product.name = request.POST.get("name")
        
        category_id = request.POST.get("category")
        if category_id:
            try:
                product.category = Category.objects.get(category_id=category_id)
            except Category.DoesNotExist:
                pass
                
        product.price_per_unit = request.POST.get("price_per_unit")
        product.stock_quantity = request.POST.get("stock_quantity")
        product.unit = request.POST.get("unit")
        product.description = request.POST.get("description")
        
        if "image" in request.FILES:
            product.image = request.FILES.get("image")
        
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('farmer_dashboard_view')
        
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories
    }
    return render(request, "F2M/edit_product.html", context)


@login_required
def buyer_dashboard_view(request):
    return render(request, "F2M/buyer_dashboard.html")

# PROFILE VIEW
@login_required
def profile_view(request):
    user = request.user

    # Compute initials from first+last name, or username
    full_name = user.get_full_name()
    if full_name.strip():
        parts = full_name.split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
    else:
        initials = user.username[:2].upper()

    # Detect role
    is_farmer = hasattr(user, 'farmer_profile')
    farmer_profile = None
    total_products = in_stock_products = out_of_stock_products = 0

    if is_farmer:
        farmer_profile = user.farmer_profile
        products_qs = Product.objects.filter(farmer=farmer_profile)
        
        stats = products_qs.aggregate(
            total=Count('product_id'),
            in_stock=Count('product_id', filter=Q(stock_quantity__gt=0)),
            out_stock=Count('product_id', filter=Q(stock_quantity=0))
        )
        total_products = stats['total'] or 0
        in_stock_products = stats['in_stock'] or 0
        out_of_stock_products = stats['out_stock'] or 0

    # Active tab is driven by the URL query param — default to 'profile'
    active_tab = request.GET.get('tab', 'profile')
    valid_tabs = ['profile', 'farm'] if is_farmer else ['profile', 'orders']
    if active_tab not in valid_tabs:
        active_tab = 'profile'

    context = {
        'initials': initials,
        'is_farmer': is_farmer,
        'farmer_profile': farmer_profile,
        'total_products': total_products,
        'in_stock_products': in_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'active_tab': active_tab,
    }
    return render(request, "F2M/profile.html", context)


# CART VIEWS
def cart_view(request):
    if request.user.is_authenticated:
        try:
            buyer_profile = request.user.buyer_profile
        except BuyerProfile.DoesNotExist:
            messages.error(request, "Only buyers can access the cart.")
            return redirect('home_view')

        cart, created = Cart.objects.get_or_create(buyer=buyer_profile)
        cart_items = cart.items.select_related('product', 'product__farmer').all()
        total_price = sum(item.subtotal() for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
    else:
        # Handle session-based cart for anonymous users
        session_cart = request.session.get('cart', {})
        cart_items = []
        total_price = 0
        
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.select_related('farmer').get(product_id=product_id)
                subtotal = product.price_per_unit * quantity
                total_price += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': subtotal,
                    'is_session': True,
                    'cart_item_id': product_id  # Use product_id as item_id for sessions
                })
            except Product.DoesNotExist:
                continue
        
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'is_anonymous': True
        }
        
    return render(request, "F2M/cart.html", context)


def add_to_cart_view(request, product_id):
    if request.method != "POST":
        return redirect('product_list_view')
        
    try:
        product = Product.objects.get(product_id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('product_list_view')

    if product.stock_quantity <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return redirect('product_list_view')

    if request.user.is_authenticated:
        try:
            buyer_profile = request.user.buyer_profile
        except BuyerProfile.DoesNotExist:
            messages.error(request, "Please create a buyer account to add items to cart.")
            return redirect('product_list_view')

        cart, created = Cart.objects.get_or_create(buyer=buyer_profile)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not item_created:
            if cart_item.quantity < product.stock_quantity:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, f"Added another {product.name} to your cart.")
            else:
                messages.warning(request, f"Not enough stock to add more {product.name}.")
        else:
            messages.success(request, f"{product.name} added to your cart.")
    else:
        # Session-based cart for anonymous users
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            if cart[product_id_str] < product.stock_quantity:
                cart[product_id_str] += 1
                messages.success(request, f"Added another {product.name} to your cart.")
            else:
                messages.warning(request, f"Not enough stock to add more {product.name}.")
        else:
            cart[product_id_str] = 1
            messages.success(request, f"{product.name} added to your cart.")
            
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('product_list_view')


def update_cart_view(request, item_id):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if request.user.is_authenticated:
            try:
                buyer_profile = request.user.buyer_profile
                cart_item = CartItem.objects.get(cart_item_id=item_id, cart__buyer=buyer_profile)
            except (BuyerProfile.DoesNotExist, CartItem.DoesNotExist):
                messages.error(request, "Item not found in your cart.")
                return redirect('cart_view')

            if action == 'increase':
                if cart_item.quantity < cart_item.product.stock_quantity:
                    cart_item.quantity += 1
                    cart_item.save()
                else:
                    messages.warning(request, f"Not enough stock to add more {cart_item.product.name}.")
            elif action == 'decrease':
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
                    messages.success(request, f"{cart_item.product.name} removed from cart.")
            elif action == 'remove':
                cart_item.delete()
                messages.success(request, f"{cart_item.product.name} removed from cart.")
        else:
            # Session-based cart update
            cart = request.session.get('cart', {})
            product_id = str(item_id)
            
            if product_id in cart:
                try:
                    product = Product.objects.get(product_id=product_id)
                    if action == 'increase':
                        if cart[product_id] < product.stock_quantity:
                            cart[product_id] += 1
                        else:
                            messages.warning(request, f"Not enough stock to add more {product.name}.")
                    elif action == 'decrease':
                        if cart[product_id] > 1:
                            cart[product_id] -= 1
                        else:
                            del cart[product_id]
                            messages.success(request, f"{product.name} removed from cart.")
                    elif action == 'remove':
                        del cart[product_id]
                        messages.success(request, f"{product.name} removed from cart.")
                except Product.DoesNotExist:
                    if product_id in cart: del cart[product_id]
            
            request.session['cart'] = cart
            request.session.modified = True
            
    return redirect('cart_view')


@login_required
def checkout_view(request):
    """
    Entry point for checkout. Requires login.
    If anonymous, @login_required will redirect to login page.
    """
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        messages.error(request, "Only buyers can proceed to checkout.")
        return redirect('home_view')
        
    # For now, just a placeholder or redirect to a success/order page
    # In a real app, this would lead to address/payment selection
    messages.info(request, "Checkout process started. (Implementation pending)")
    return redirect('cart_view')