"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.template.loader import render_to_string

from pagedown.widgets import AdminPagedownWidget

from artist.models import Genre, Artist, Bio, Photo, SoundCloudPlaylist, \
    Social, Update


class LocationWidget(AdminTextInputWidget):

    template_name = 'widgets/coordinates.html'

    def render(self, name, value, attrs=None):
        html = super(LocationWidget, self).render(name, value, attrs=attrs)
        return html + render_to_string(self.template_name)


class ArtistAdminForm(forms.ModelForm):

    location = forms.CharField(help_text=Artist._meta.get_field('location').help_text, widget=LocationWidget)

    class Meta:
        model = Artist
        fields = ('name', 'genres', 'slug', 'location', 'lat', 'lon',)


class BioAdminForm(forms.ModelForm):

    bio = forms.CharField(help_text=Bio._meta.get_field('bio').help_text, widget=AdminPagedownWidget)

    class Meta:
        model = Bio
        fields = ('bio',)


class BioInline(admin.StackedInline):

    model = Bio
    form = BioAdminForm


class PhotoInline(admin.TabularInline):

    model = Photo


class SoundCloudPlaylistInline(admin.TabularInline):

    model = SoundCloudPlaylist
    extra = 1


class SocialInline(admin.TabularInline):

    model = Social


class ArtistAdmin(admin.ModelAdmin):

    form = ArtistAdminForm
    prepopulated_fields = {'slug': ('name',)}
    inlines = (BioInline, PhotoInline, SoundCloudPlaylistInline, SocialInline,)


admin.site.register(Genre)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Update)
