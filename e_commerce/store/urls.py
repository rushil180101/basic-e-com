from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.store, name='store'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('update_item/<int:pk>/<int:update_action>/<int:current_page>/', views.update_item, name='update_item'),
    path('view_product/<int:pk>/', views.view_product, name='view_product'),
    path('process_order', views.process_order, name='process_order'),
    path('register', views.register_page, name='register'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_user, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
