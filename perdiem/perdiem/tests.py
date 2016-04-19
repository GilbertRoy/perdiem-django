"""
:Created: 5 March 2016
:Author: Lucas Connors

"""

import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from artist.models import Genre, Artist, Update
from campaign.models import Campaign, Investment, RevenueReport


class PerDiemTestCase(TestCase):

    USER_USERNAME = 'jsmith'
    USER_EMAIL = 'jsmith@example.com'
    USER_PASSWORD = 'abc123'
    ORDINARY_USER_USERNAME = 'jdoe'
    ORDINARY_USER_EMAIL = 'jdoe@example.com'

    GENRE_NAME = 'Progressive Rock'
    ARTIST_NAME = 'Rush'
    ARTIST_LATITUDE = 43.7689
    ARTIST_LONGITUDE = -79.4138
    ARTIST_LOCATION = 'Willowdale, Toronto, Ontario, Canada'
    ARTIST_UPDATE = 'North American Tour This Year!'

    CAMPAIGN_AMOUNT = 10000
    CAMPAIGN_REASON = 'to record a new album'
    CAMPAIGN_FANS_PERCENTAGE = 20
    CAMPAIGN_REVENUE_REPORT_AMOUNT = 500

    @staticmethod
    def strip_query_params(url):
        return url.split('?')[0]

    def assertResponseRenders(self, url, status_code=200, method='GET', data={}, **kwargs):
        request_method = getattr(self.client, method.lower())
        follow = status_code == 302
        response = request_method(url, data=data, follow=follow, **kwargs)

        if status_code == 302:
            redirect_url, response_status_code = response.redirect_chain[0]
        else:
            response_status_code = response.status_code
        self.assertEquals(
            response_status_code,
            status_code,
            "URL {url} returned with status code {actual_status} when {expected_status} was expected.".format(
                url=url,
                actual_status=response_status_code,
                expected_status=status_code
            )
        )
        return response

    def assertJsonResponseRenders(self, url, status_code=200, method='GET', data={}, **kwargs):
        response = self.assertResponseRenders(url, status_code=status_code, method=method, data=data, **kwargs)
        self.assertTrue(isinstance(response, JsonResponse))
        return response.json()

    def assertResponseRedirects(self, url, redirect_url, method='GET', data={}, **kwargs):
        response = self.assertResponseRenders(url, status_code=302, method=method, data=data, **kwargs)
        redirect_url_from_response, _ = response.redirect_chain[0]
        self.assertEquals(self.strip_query_params(redirect_url_from_response), redirect_url)
        self.assertEquals(response.status_code, 200)

    def get200s(self):
        return []

    def setup_users(self):
        self.user = User.objects.create_user(
            self.USER_USERNAME,
            email=self.USER_EMAIL,
            password=self.USER_PASSWORD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(
            username=self.USER_USERNAME,
            password=self.USER_PASSWORD
        )

        self.ordinary_user = User.objects.create_user(
            self.ORDINARY_USER_USERNAME,
            email=self.ORDINARY_USER_EMAIL,
            password=self.USER_PASSWORD
        )

    def create_first_instances(self):
        self.genre = Genre.objects.create(name=self.GENRE_NAME)
        self.artist = Artist.objects.create(
            name=self.ARTIST_NAME,
            slug=slugify(self.ARTIST_NAME),
            lat=self.ARTIST_LATITUDE,
            lon=self.ARTIST_LONGITUDE,
            location=self.ARTIST_LOCATION
        )
        self.artist.genres.add(self.genre)
        self.update = Update.objects.create(artist=self.artist, text=self.ARTIST_UPDATE)

        self.campaign = Campaign.objects.create(
            artist=self.artist,
            amount=self.CAMPAIGN_AMOUNT,
            reason=self.CAMPAIGN_REASON,
            fans_percentage=self.CAMPAIGN_FANS_PERCENTAGE,
            end_datetime=timezone.now() + datetime.timedelta(days=14)
        )
        self.revenue_report = RevenueReport.objects.create(
            campaign=self.campaign,
            amount=self.CAMPAIGN_REVENUE_REPORT_AMOUNT
        )

    def setUp(self):
        super(PerDiemTestCase, self).setUp()
        self.setup_users()
        self.create_first_instances()

    def tearDown(self):
        RevenueReport.objects.all().delete()
        Campaign.objects.all().delete()
        Update.objects.all().delete()
        Artist.objects.all().delete()
        Genre.objects.all().delete()
        User.objects.all().delete()
        super(PerDiemTestCase, self).tearDown()

    def testRender200s(self):
        for url in self.get200s():
            self.assertResponseRenders(url)


class AdminWebTestCase(PerDiemTestCase):

    def get200s(self):
        return [
            '/admin/',
        ]

    def testAdminLoginPageRenders(self):
        self.client.logout()
        self.assertResponseRedirects('/admin/', '/admin/login/')
