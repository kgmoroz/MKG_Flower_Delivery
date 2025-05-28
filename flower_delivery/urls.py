"""
URL configuration for flower_delivery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView


# --- 1. View, разрешающая GET-выход -----------------------------
class LogoutGetView(LogoutView):
    http_method_names = ["get", "post", "head", "options"]
    # куда перенаправлять после выхода
    next_page = "catalog:product_list"


# --- 2. Маршруты -------------------------------------------------
urlpatterns = [
    path("admin/", admin.site.urls),

    # Публичные разделы
    path("", include("catalog.urls", namespace="catalog")),
    path("orders/", include("orders.urls", namespace="orders")),

    # Выход по GET (должен быть ДО подключения auth.urls)
    path("accounts/logout/", LogoutGetView.as_view(), name="logout"),

    # Стандартные auth-URL-ы: login, logout (POST), password_reset …
    path("accounts/", include("django.contrib.auth.urls")),

    # Регистрация (signup)
    path("accounts/", include("users.urls", namespace="users")),
]

# --- 3. Медиафайлы в режиме разработки ---------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
