from django.contrib import admin
from django.urls import include, path
from store import views  # 'core' o'rniga ilovangiz nomini yozing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # Agar bosh sahifa bo'lsa
    path('cart/add/', views.add_selected_to_cart, name='add_selected_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('order/create/', views.create_order, name='create_order'),
    path('receipt/<int:order_id>/', views.receipt_view, name='receipt'),
    path('api/', include('store.urls')),  # yoki DRF routerlar uchun
    path('dashboard/', views.dashboard_view, name='dashboard'),
]