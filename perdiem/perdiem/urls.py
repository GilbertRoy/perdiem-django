"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve

from artist.views import CoordinatesFromAddressView, ArtistListView, \
    ArtistDetailView
from campaign.views import PaymentChargeView
from emails.views import UnsubscribeView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^unsubscribe/(?P<username>[\w.@+-]+)/(?P<token>[\w.:\-_=]+)/$', UnsubscribeView.as_view(), name='unsubscribe'),
    url(r'^payments/charge/(?P<campaign_id>\d+)/?$', PaymentChargeView.as_view(), name='pinax_stripe_charge'),
    url(r'^payments/', include('pinax.stripe.urls')),
    url(r'^api/coordinates/?$', CoordinatesFromAddressView.as_view(), name='coordinates'),

    url(r'^artists/?$', ArtistListView.as_view(), name='artists'),
    url(r'^artist/(?P<slug>[\w_-]+)/?$', ArtistDetailView.as_view(), name='artist'),

    url(r'^privacty/?$', TemplateView.as_view(template_name='extra/privacy.html'), name='privacy'),
    url(r'^faq/?$', TemplateView.as_view(template_name='extra/faq.html'), name='faq'),
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
]

# Add media folder to urls when DEBUG = True
if settings.DEBUG:
    urlpatterns.append(
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    )
