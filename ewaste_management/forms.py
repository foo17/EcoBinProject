from django import forms
from .models import Incentive, Topic, Comment, User, CEApplication, University, Consultation, Publication, MovementRecord, Component, Organization

class IncentiveFrom(forms.ModelForm):
    class Meta:
        model = Incentive
        fields = ['incentive_picture', 'name', 'description', 'points_required']

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'university', 'organization', 'phone_number', 'password', 'role', 'profile_picture', 'bio']

class CEApplicationForm(forms.ModelForm):
    class Meta:
        model = CEApplication
        fields = ['university']

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'publication_detail', 'publication_location', 'event_start_date', 'event_end_date'
        ]

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['date', 'time', 'location', 'duration_hr']

class UniversityProfileForm(forms.ModelForm):
    class Meta:
        model = University
        fields = ['university_name', 'address', 'bio']

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['date', 'time', 'location']

class MovementRecordForm(forms.ModelForm):
    class Meta:
        model = MovementRecord
        fields = ['supplier', 'transaction_datetime']

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = ['appliance', 'component_name', 'amount', 'status']

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['organization_name', 'address', 'organization_type', 'website', 'additional_information']