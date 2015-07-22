# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from future.builtins import str

from decimal import Decimal
import locale
import platform

from django import template

from cartridge.shop.utils import set_locale

from cartridge.shop.models import Product

register = template.Library()


@register.filter
def currency(value):
    """
    Format a value as currency according to locale.
    """
    set_locale()
    if not value:
        value = 0
    value = locale.currency(Decimal(value), grouping=True)
    if platform.system() == 'Windows':
        try:
            value = str(value, encoding=locale.getpreferredencoding())
        except TypeError:
            pass
    return value


def _order_totals(context):
    """
    Add shipping/tax/discount/order types and totals to the template
    context. Use the context's completed order object for email
    receipts, or the cart object for checkout.
    """
    fields = ["shipping_type", "shipping_total", "discount_total",
              "tax_type", "tax_total"]
    if "order" in context:
        for field in fields + ["item_total"]:
            context[field] = getattr(context["order"], field)
    else:
        context["item_total"] = context["request"].cart.total_price()
        if context["item_total"] == 0:
            # Ignore session if cart has no items, as cart may have
            # expired sooner than the session.
            context["tax_total"] = 0
            context["discount_total"] = 0
            context["shipping_total"] = 0
        else:
            for field in fields:
                context[field] = context["request"].session.get(field, None)
    context["order_total"] = context.get("item_total", None)
    if context.get("shipping_total", None) is not None:
        context["order_total"] += Decimal(str(context["shipping_total"]))
    if context.get("discount_total", None) is not None:
        context["order_total"] -= Decimal(str(context["discount_total"]))
    if context.get("tax_total", None) is not None:
        context["order_total"] += Decimal(str(context["tax_total"]))
    return context


@register.inclusion_tag("shop/includes/order_totals.html", takes_context=True)
def order_totals(context):
    """
    HTML version of order_totals.
    """
    return _order_totals(context)


@register.inclusion_tag("shop/includes/order_totals.txt", takes_context=True)
def order_totals_text(context):
    """
    Text version of order_totals.
    """
    return _order_totals(context)


@register.inclusion_tag('includes/product_slide_box.html', takes_context=True)
def latest_products(context, box_name, box_title, limit):
    products = Product.objects.filter(available=True, type=0).order_by("-id")[:limit]

    return {"Products":products, "box_title":box_title, "box_name":box_name, 'MEDIA_URL': context['MEDIA_URL']}


@register.inclusion_tag('includes/product_slide_box.html', takes_context=True)
def latest_special_products(context, box_name, box_title, limit):
    
    products = Product.objects.filter(available=True, type=2).order_by("-id")[:limit]

    return {"Products":products, "box_title":box_title, "box_name":box_name, 'MEDIA_URL': context['MEDIA_URL']}

@register.inclusion_tag('includes/today_offer.html', takes_context=True)
def today_offer(context, box_name, box_title, limit):
    
    products = Product.objects.filter(available=True, type=1).order_by("-id")[:limit]

    return {"Products":products, "box_title":box_title, "box_name":box_name, 'MEDIA_URL': context['MEDIA_URL']}

@register.inclusion_tag('includes/best_seller.html', takes_context=True)
def best_seller(context, box_name, box_title, limit):
    
    products = Product.objects.filter(available=True, type=1).order_by("-id")[:limit]

    return {"Products":products, "box_title":box_title, "box_name":box_name, 'MEDIA_URL': context['MEDIA_URL']}