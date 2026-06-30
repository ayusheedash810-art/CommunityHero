from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("report/", views.report_issue, name="report_issue"),
    path("issue/<int:pk>/", views.issue_detail, name="issue_detail"),
    path("issue/<int:pk>/edit/", views.edit_issue, name="edit_issue"),
    path("issue/<int:pk>/delete/", views.delete_issue, name="delete_issue"),
    path("issue/<int:pk>/status/",views.update_status,name="update_status"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("test-ai/", views.test_ai, name="test_ai"),
    path("issue/<int:pk>/verify/", views.verify_issue, name="verify_issue"),
    path("issue/<int:pk>/verify/",views.verify_issue,name="verify_issue"),
    path("predictive-insights/",views.predictive_insights,name="predictive_insights"
),
]