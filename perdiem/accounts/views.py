"""
:Created: 5 April 2016
:Author: Lucas Connors

"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView

from accounts.forms import (
    RegisterAccountForm, EditNameForm, EditAvatarForm, EmailPreferencesForm,
    ContactForm
)
from accounts.models import UserAvatar, UserAvatarImage
from artist.models import Update
from emails.messages import WelcomeEmail, ContactEmail
from emails.models import EmailSubscription
from perdiem.views import ConstituentFormView, MultipleFormView


class RegisterAccountView(CreateView):

    template_name = 'registration/register.html'
    form_class = RegisterAccountForm

    def get_success_url(self):
        return self.request.GET.get('next') or reverse('profile')

    def form_valid(self, form):
        valid = super(RegisterAccountView, self).form_valid(form)

        # Login the newly-registered user
        d = form.cleaned_data
        username, password = d['username'], d['password1']
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)

        # Create the user's newsletter subscription (if applicable)
        if d['subscribe_news']:
            EmailSubscription.objects.create(user=user, subscription=EmailSubscription.SUBSCRIPTION_NEWS)

        # Send user welcome email
        WelcomeEmail().send(user=user)

        return valid


class EditNameFormView(ConstituentFormView):

    form_class = EditNameForm
    provide_user = True

    def get_initial(self):
        user = self.request.user
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'invest_anonymously': user.userprofile.invest_anonymously,
        }

    def form_valid(self, form):
        user = self.request.user
        d = form.cleaned_data

        # Update username and name
        user.username = d['username']
        user.first_name = d['first_name']
        user.last_name = d['last_name']
        user.save()

        # Update anonymity
        user.userprofile.invest_anonymously = d['invest_anonymously']
        user.userprofile.save()


class EditAvatarFormView(ConstituentFormView):

    form_class = EditAvatarForm
    provide_user = True
    includes_files = True

    def get_initial(self):
        user_profile = self.request.user.userprofile
        return {
            'avatar': user_profile.avatar.id if user_profile.avatar else '',
        }

    def form_valid(self, form):
        user = self.request.user
        d = form.cleaned_data

        # Upload a custom avatar, if provided
        user_avatar = d['avatar']
        custom_avatar = d['custom_avatar']
        if custom_avatar:
            user_avatar, _ = UserAvatar.objects.get_or_create(user=user, provider=UserAvatar.PROVIDER_PERDIEM)
            UserAvatarImage.objects.update_or_create(avatar=user_avatar, defaults={'img': custom_avatar,})

        # Update user's avatar
        user.userprofile.avatar = user_avatar
        user.userprofile.save()


class ChangePasswordFormView(ConstituentFormView):

    form_class = PasswordChangeForm
    provide_user = True

    def form_valid(self, form):
        user = self.request.user
        d = form.cleaned_data

        # Update user's password
        user.set_password(d['new_password1'])
        user.save()


class EmailPreferencesFormView(ConstituentFormView):

    form_class = EmailPreferencesForm

    def get_initial(self):
        initial = {}
        for subscription_type, _ in EmailSubscription.SUBSCRIPTION_CHOICES:
            subscribed = EmailSubscription.objects.is_subscribed(user=self.request.user, subscription_type=subscription_type)
            initial['subscription_{stype}'.format(stype=subscription_type.lower())] = subscribed
        return initial

    def form_valid(self, form):
        user = self.request.user

        # Update user's email subscriptions
        email_subscriptions = {k: v for k, v in form.cleaned_data.iteritems() if k.startswith('subscription_')}
        for subscription_type, is_subscribed in email_subscriptions.iteritems():
            EmailSubscription.objects.update_or_create(
                user=user,
                subscription=getattr(EmailSubscription, subscription_type.upper()),
                defaults={'subscribed': is_subscribed,}
            )


class ProfileView(LoginRequiredMixin, MultipleFormView):

    template_name = 'registration/profile.html'
    constituent_form_views = {
        'edit_name': EditNameFormView,
        'edit_avatar': EditAvatarFormView,
        'change_password': ChangePasswordFormView,
        'email_preferences': EmailPreferencesFormView,
    }

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        # Update context with profile information
        context.update(self.request.user.userprofile.profile_context())
        context['updates'] = Update.objects.filter(artist__in=context['artists']).order_by('-created_datetime')

        # Update context with available avatars
        user_avatars = UserAvatar.objects.filter(user=self.request.user)
        avatars = {
            'Default': UserAvatar.default_avatar_url(),
        }
        avatars.update({avatar.get_provider_display(): avatar.avatar_url() for avatar in user_avatars})
        context['avatars'] = avatars

        return context


class PublicProfileView(TemplateView):

    template_name = 'registration/public_profile.html'

    def get_context_data(self, **kwargs):
        context = super(PublicProfileView, self).get_context_data(**kwargs)
        profile_user = get_object_or_404(User, username=kwargs['username'])
        context.update(profile_user.userprofile.profile_context())
        context.update({
            'profile_user': profile_user,
        })
        return context


class ContactFormView(FormView):

    template_name = 'registration/contact.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('contact_thanks')

    def get_initial(self):
        initial = super(ContactFormView, self).get_initial()
        user = self.request.user
        if user.is_authenticated():
            initial['email'] = user.email
            initial['first_name'] = user.first_name
            initial['last_name'] = user.last_name
        return initial

    def form_valid(self, form):
        # Add user_id to context, if available
        context = form.cleaned_data
        user = self.request.user
        if user.is_authenticated():
            context['user_id'] = user.id

        # Send contact email
        ContactEmail().send_to_email(email='support@investperdiem.com', context=context)

        return super(ContactFormView, self).form_valid(form)
