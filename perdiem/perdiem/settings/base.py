"""
:Created: 26 July 2015
:Author: Lucas Connors

"""

import os

from cbsettings import DjangoDefaults
import raven


class BaseSettings(DjangoDefaults):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TOP_DIR = os.path.dirname(BASE_DIR)

    DEBUG = True
    ALLOWED_HOSTS = []

    # Application definition
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'whitenoise.runserver_nostatic',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django.contrib.humanize',
        'raven.contrib.django.raven_compat',
        'sorl.thumbnail',
        'storages',
        'social.apps.django_app.default',
        'pinax.stripe',
        'accounts.apps.AccountsConfig',
        'artist.apps.ArtistConfig',
        'campaign.apps.CampaignConfig',
        'emails.apps.EmailsConfig',
    )
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'accounts.middleware.LoginFormMiddleware',
    )
    ROOT_URLCONF = 'perdiem.urls'
    SITE_ID = 1

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(TOP_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'social.apps.django_app.context_processors.backends',
                    'social.apps.django_app.context_processors.login_redirect',
                ],
            },
        },
    ]
    WSGI_APPLICATION = 'perdiem.wsgi.application'

    # Cache and Database
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'perdiem',
            'USER': 'postgres',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    # Internationalization
    TIME_ZONE = 'UTC'
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    MEDIA_ROOT = os.path.join(TOP_DIR, 'media')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATIC_ROOT = os.path.join(TOP_DIR, 'staticfiles')
    STATICFILES_DIRS = (
        os.path.join(TOP_DIR, 'static'),
    )
    MEDIAFILES_LOCATION = 'media'
    STATICFILES_LOCATION = 'static'
    AWS_HEADERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'Cache-Control': 'max-age=94608000',
    }
    MAXIMUM_AVATAR_SIZE = 2 * 1024 * 1024 # 2MB

    @property
    def MEDIA_URL(self):
        if not hasattr(self, 'AWS_S3_CUSTOM_URL'):
            return '/media/'
        return '{aws_s3}/{media}/'.format(
            aws_s3=self.AWS_S3_CUSTOM_URL,
            media=self.MEDIAFILES_LOCATION
        )

    @property
    def STATIC_URL(self):
        if not hasattr(self, 'AWS_S3_CUSTOM_URL'):
            return '/static/'
        return '{aws_s3}/{static}/'.format(
            aws_s3=self.AWS_S3_CUSTOM_URL,
            static=self.STATICFILES_LOCATION
        )

    # Authentication
    AUTHENTICATION_BACKENDS = (
        'social.backends.google.GoogleOAuth2',
        'social.backends.facebook.FacebookOAuth2',
        'django.contrib.auth.backends.ModelBackend',
    )
    SOCIAL_AUTH_PIPELINE = (
        'social.pipeline.social_auth.social_details',
        'social.pipeline.social_auth.social_uid',
        'social.pipeline.social_auth.auth_allowed',
        'social.pipeline.social_auth.social_user',
        'social.pipeline.user.get_username',
        'social.pipeline.social_auth.associate_by_email',
        'accounts.pipeline.require_email',
        'social.pipeline.user.create_user',
        'accounts.pipeline.save_avatar',
        'social.pipeline.social_auth.associate_user',
        'social.pipeline.social_auth.load_extra_data',
        'social.pipeline.user.user_details',
    )
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email',]
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
        'fields': ', '.join(['id', 'name', 'email', 'picture',]),
    }
    LOGIN_URL = '/'

    # Sentry
    @property
    def RAVEN_CONFIG(self):
        if not hasattr(self, 'RAVEN_SECRET_KEY'):
            return {}
        return {
            'dsn': 'https://{public_key}:{secret_key}@app.getsentry.com/{project_id}'.format(
                public_key=self.RAVEN_PUBLIC_KEY,
                secret_key=self.RAVEN_SECRET_KEY,
                project_id=self.RAVEN_PROJECT_ID
            ),
            'release': raven.fetch_git_sha(self.TOP_DIR),
        }

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = '/tmp/perdiem/email'
    TEMPLATED_EMAIL_TEMPLATE_DIR = 'email/'
    DEFAULT_FROM_EMAIL = 'noreply@investperdiem.com'

    # Stripe
    PERDIEM_FEE = 1 # $1
    PINAX_STRIPE_SEND_EMAIL_RECEIPTS = False
