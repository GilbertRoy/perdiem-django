"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from __future__ import unicode_literals
import math

from django.conf import settings
from django.db import models
from django.db.models import Count, Sum
from django.utils import timezone

from pinax.stripe.models import Charge

from artist.models import Artist


class Campaign(models.Model):

    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(help_text='The amount of money the artist wishes to raise')
    reason = models.CharField(max_length=40, help_text='The reason why the artist is raising money, in a few words')
    value_per_share = models.PositiveIntegerField(default=1, help_text='The value (in dollars) per share the artist wishes to sell')
    start_datetime = models.DateTimeField(db_index=True, default=timezone.now, help_text='When the campaign will start accepting investors')
    end_datetime = models.DateTimeField(db_index=True, null=True, blank=True, help_text='When the campaign ends and will no longer accept investors (no end date if blank)')
    use_of_funds = models.TextField(null=True, blank=True, help_text='A description of how the funds will be used')
    fans_percentage = models.PositiveSmallIntegerField(help_text='The percentage of revenue that goes back to the fans (a value from 0-100)')

    def __unicode__(self):
        return u'{artist}: ${amount} {reason}'.format(
            artist=unicode(self.artist),
            amount=self.amount,
            reason=self.reason
        )

    def value_per_share_cents(self):
        return self.value_per_share * 100

    def total(self, num_shares):
        subtotal = num_shares * self.value_per_share
        total = (settings.PERDIEM_FEE + subtotal) * 1.029 + 0.3 # Stripe 2.9% + $0.30 fee
        return math.ceil(total * 100.0) / 100.0

    def num_shares(self):
        return self.amount / self.value_per_share

    def total_shares_purchased(self):
        return self.investment_set.filter(charge__paid=True).aggregate(total_shares=Sum('num_shares'))['total_shares'] or 0

    def num_shares_remaining(self):
        return self.num_shares() - self.total_shares_purchased()

    def amount_raised(self):
        return self.total_shares_purchased() * self.value_per_share

    def percentage_funded(self):
        try:
            return "{0:.0f}".format((float(self.amount_raised()) / self.amount) * 100)
        except ZeroDivisionError:
            return '100'

    def days_remaining(self):
        if self.end_datetime:
            return max(0, (self.end_datetime - timezone.now()).days)

    def open(self):
        started = self.start_datetime is None or self.start_datetime < timezone.now()
        ended = self.end_datetime and self.end_datetime < timezone.now()
        return started and not ended and self.amount_raised() < self.amount

    def artist_percentage(self):
        return 100 - self.fans_percentage

    def revenue_to_2x(self):
        return self.amount * (100/self.fans_percentage) * 2

    def generated_revenue(self):
        return self.revenuereport_set.all().aggregate(gr=models.Sum('amount'))['gr'] or 0

    def generated_revenue_fans(self):
        return self.generated_revenue() * (float(self.fans_percentage) / 100)

    def generated_revenue_fans_per_share(self):
        return self.generated_revenue_fans() / self.num_shares()

    def investors(self):
        investors = {}
        investments = self.investment_set.filter(charge__paid=True).select_related('charge', 'charge__customer', 'charge__customer__user')

        for investment in investments:
            investor = investment.investor()
            if investor.id not in investors:
                investors[investor.id] = {
                    'name': investor.userprofile.get_display_name(),
                    'total_investment': 0,
                }
            investors[investor.id]['total_investment'] += investment.num_shares * self.value_per_share
        return investors.values()


class Expense(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    expense = models.CharField(max_length=30, help_text='A description of one of the expenses for the artist (eg. Studio cost)')

    class Meta:
        unique_together = (('campaign', 'expense',))

    def __unicode__(self):
        return u'{campaign} ({expense})'.format(
            campaign=unicode(self.campaign),
            expense=self.expense
        )


class Investment(models.Model):

    charge = models.OneToOneField(Charge, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    transaction_datetime = models.DateTimeField(db_index=True, auto_now_add=True)
    num_shares = models.PositiveSmallIntegerField(default=1, help_text='The number of shares an investor made in a transaction')

    def __unicode__(self):
        return u'{num_shares} shares in {campaign} to {investor}'.format(
            num_shares=self.num_shares,
            campaign=unicode(self.campaign),
            investor=unicode(self.investor())
        )

    def investor(self):
        return self.charge.customer.user


class RevenueReport(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(help_text='The amount of revenue generated (in dollars) being reported (since last report)')
    reported_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'${amount} for {campaign}'.format(
            amount=self.amount,
            campaign=unicode(self.campaign)
        )
