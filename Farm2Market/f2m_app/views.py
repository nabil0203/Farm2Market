from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FarmerProfile, BuyerProfile, Product, Category



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

            # Role-based redirect
            if hasattr(user, "farmer_profile"):
                return redirect("farmer_dashboard_view")

            elif hasattr(user, "buyer_profile"):
                return redirect("home_view")

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
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories
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

    products = Product.objects.filter(farmer=farmer_profile).order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories
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