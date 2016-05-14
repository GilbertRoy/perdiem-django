"""
:Created: 5 April 2015
:Author: Lucas Connors

"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators

from accounts.models import UserAvatar


class RegisterAccountForm(UserCreationForm):

    email = forms.EmailField(required=True)
    subscribe_news = forms.BooleanField(required=False, label='Subscribe to general updates about PerDiem')

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2',)

    def save(self, commit=True):
        user = super(RegisterAccountForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EditNameForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                ('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ]
    )
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    invest_anonymously = forms.BooleanField(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EditNameForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.user.id).filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


class EditAvatarForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(EditAvatarForm, self).__init__(*args, **kwargs)
        self.fields['avatar'] = forms.ChoiceField(choices=self.get_avatar_choices(user), required=False, widget=forms.RadioSelect)

    def get_avatar_choices(self, user):
        user_avatars = UserAvatar.objects.filter(user=user)
        return [('', 'Default',)] + [(avatar.id, avatar.get_provider_display(),) for avatar in user_avatars]

    def clean_avatar(self):
        avatar_id = self.cleaned_data['avatar']
        if avatar_id:
            return UserAvatar.objects.get(id=avatar_id)


class EmailPreferencesForm(forms.Form):

    subscription_news = forms.BooleanField(required=False, label='Subscribe to general updates about PerDiem')
    subscription_all = forms.BooleanField(required=False, label='Uncheck this box to unsubscribe from all emails from PerDiem')

    def clean(self):
        d = self.cleaned_data
        if d['subscription_news'] and not d['subscription_all']:
            raise forms.ValidationError("You cannot subscribe to general updates if you are unsubscribed from all emails.")
        return d


class ContactForm(forms.Form):

    INQUIRY_CHOICES = (
        ('Support', 'Support',),
        ('Feedback', 'Feedback',),
        ('General Inquiry',  'General Inquiry',),
    )

    inquiry = forms.ChoiceField(choices=INQUIRY_CHOICES)
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)
