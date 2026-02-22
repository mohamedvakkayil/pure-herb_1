from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('records/', views.EntryListView.as_view(), name='entry_list'),
    path('records/export/', views.RecordsExportView.as_view(), name='records_export'),
    path('entry/sales/new/', views.SaleFormView.as_view(), name='sales_form'),
    path('entry/expense/new/', views.ExpenseFormView.as_view(), name='expense_form'),
    path('entry/<int:pk>/', views.EntryDetailView.as_view(), name='entry_detail'),
    path('entry/new/', views.EntryCreateView.as_view(), name='entry_create'),
    path('entry/<int:pk>/edit/', views.EntryUpdateView.as_view(), name='entry_update'),
    path('entry/<int:pk>/delete/', views.EntryDeleteView.as_view(), name='entry_delete'),
    path('approval/pending/', views.ApprovalPendingView.as_view(), name='approval_pending'),
    path('approval/queue/', views.ApprovalQueueView.as_view(), name='approval_queue'),
    path('approval/<int:pk>/action/', views.ApprovalRequestApproveView.as_view(), name='approval_action'),
    path('user-request/new/', views.UserRequestCreateView.as_view(), name='user_request_create'),
    path('user-request/pending/', views.UserRequestPendingView.as_view(), name='user_request_pending'),
    path('user-request/approval/', views.UserRequestApprovalView.as_view(), name='user_request_approval'),
    path('user-request/<int:pk>/action/', views.UserRequestApproveView.as_view(), name='user_request_action'),
    path('users/', views.UserManagementListView.as_view(), name='user_management'),
    path('users/<int:pk>/reset-password/', views.UserResetPasswordView.as_view(), name='user_reset_password'),
    path('users/<int:pk>/lock/', views.UserToggleLockView.as_view(), name='user_toggle_lock'),
]
