# from django.utils import timezone
# from django.db.models import F
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse, reverse_lazy
# from django.conf import settings
# from django.utils.translation import ugettext as _
# from django.core.exceptions import ObjectDoesNotExist

# from django.views import View
# from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
# from django.http import HttpResponse

from vendor.models import Invoice

# from vendor.models import Offer, OrderItem, Invoice, Payment, Address #Price, Purchase, Refund, CustomerProfile, PurchaseStatus, OrderStatus
# # from vendor.forms import AddToCartForm, AddToCartModelForm, PaymentForm, RequestRefundForm
# from vendor.models.address import Address as GoogleAddress
# from vendor.processors import PaymentProcessor
# from vendor.forms import BillingAddressForm, CreditCardForm


#############
# Admin Views

class AdminDashboardView(LoginRequiredMixin, ListView):
    '''
    List of the most recent invoices generated on the current site.
    '''
    template_name = "vendor/admin_dashboard.html"
    model = Invoice

    def get_queryset(self):
        return self.model.on_site.all()[:10]    # Return the most recent 10


class AdminInvoiceListView(LoginRequiredMixin, ListView):
    '''
    List of all the invoices generated on the current site.
    '''
    template_name = "vendor/invoice_admin_list.html"
    model = Invoice

    def get_queryset(self):
        return self.model.on_site.filter(status__gt=Invoice.InvoiceStatus.CART)  # ignore cart state invoices


class AdminInvoiceDetailView(LoginRequiredMixin, DetailView):
    '''
    Details of an invoice generated on the current site.
    '''
    template_name = "vendor/invoice_admin_detail.html"
    model = Invoice
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
