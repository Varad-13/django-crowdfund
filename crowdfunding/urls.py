from django.urls import path
from core.views import index, user
from . import views

urlpatterns = [
    path('campaigns/user/<slug:author>/<slug:url>', views.detail, name='post_detail'),
    path('campaigns/add', views.create_post, name='create_post'),
    path('campaigns/user/<slug:author>', user, name='user'),
    path('campaigns/user/<slug:author>/paymenthandler/<slug:url>', views.paymenthandler, name='paymenthandler'),
    path('campaigns/edit/<slug:author>/<slug:url>', views.edit_post, name='edit_post'),
    path('campaigns/delete/<slug:url>', views.delete_post, name="delete_post"),
    path('accounts/profile/', views.user_dashboard, name='Dashboard'),
    path('campaigns/<slug:url>', views.post_detail, name='detail'),
]