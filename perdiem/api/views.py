"""
:Created: 29 May 2016
:Author: Lucas Connors

"""

import decimal

from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from pinax.stripe.actions import charges, customers, sources
from pinax.stripe.models import Card
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe

from api.forms import CoordinatesFromAddressForm
from artist.models import Artist, Update
from campaign.forms import PaymentChargeForm
from campaign.models import Campaign, Investment


class AddArtistPermission(permissions.DjangoModelPermissions):

    def get_required_permissions(self, method, model_cls):
        return 'artist.add_artist'


class ArtistAdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            update = Update.objects.select_related('artist').get(id=view.kwargs['update_id'])
        except Update.DoesNotExist:
            return False
        return update.artist.has_permission_to_submit_update(user=request.user)


class CoordinatesFromAddress(APIView):

    permission_classes = (AddArtistPermission,)
    queryset = Artist.objects.none()

    def get(self, request, *args, **kwargs):
        # Validate request
        form = CoordinatesFromAddressForm(request.GET)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        address = form.cleaned_data['address']

        # Return lat/lon for address
        geolocator = Nominatim()
        try:
            location = geolocator.geocode(address)
        except GeocoderTimedOut:
            return Response(
                "Geocoder service currently unavailable. Please try again later.",
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response({
            'latitude': float("{0:.4f}".format(location.latitude)),
            'longitude': float("{0:.4f}".format(location.longitude)),
        })


class PaymentCharge(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, campaign_id, *args, **kwargs):
        # Validate request and campaign status
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(
                "Campaign with ID {campaign_id} does not exist.".format(campaign_id=campaign_id),
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if not campaign.open():
                return Response(
                    "This campaign is no longer accepting investments.",
                    status=status.HTTP_400_BAD_REQUEST
                )
        form = PaymentChargeForm(request.data, campaign=campaign)
        if not form.is_valid():
            return Response(str(form.errors), status=status.HTTP_400_BAD_REQUEST)
        d = form.cleaned_data

        # Get card and customer
        card = d['card']
        customer = customers.get_customer_for_user(request.user)
        if not customer:
            customer = customers.create(request.user, card=card, plan=None, charge_immediately=False)
            card = Card.objects.get(customer=customer)
        else:
            # Check if we have the card the user is using
            # and if not, create it
            card_fingerprint = stripe.Token.retrieve(card)['card']['fingerprint']
            cards_with_fingerprint = Card.objects.filter(customer=customer, fingerprint=card_fingerprint)
            if cards_with_fingerprint.exists():
                card = cards_with_fingerprint[0]
            else:
                card = sources.create_card(customer=customer, token=card)

        # Create charge
        num_shares = d['num_shares']
        amount = decimal.Decimal(campaign.total(num_shares))
        try:
            charge = charges.create(amount=amount, customer=customer.stripe_id, source=card)
        except stripe.CardError as e:
            return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
        Investment.objects.create(charge=charge, campaign=campaign, num_shares=num_shares)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class DeleteUpdate(APIView):

    permission_classes = (permissions.IsAuthenticated, ArtistAdminPermission,)

    def delete(self, request, *args, **kwargs):
        Update.objects.get(id=self.kwargs['update_id']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
