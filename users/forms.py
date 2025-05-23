from django import forms
from ewaste_management.models import University, Organization, User

class UserRegisteration(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'university', 'organization', 'phone_number', 'password', 'role', 'bio']



# class UniRegistration(forms.ModelForm):
#     class Meta:
#         model = UniversityCommunityMember
#         fields = ['email', 'phone_number', 'role', 'password', 'account_name', 'phone_number', 'role', 'profile_picture', 'university', 'status', 'personal_bio']

# class EwasteOrganizationRegistration(forms.ModelForm):
#     class Meta:
#         model = EwasteOrganization
#         fields = ['organization_name', 'address', 'website', 'bio']

# class EwasteRepresentativeRegistration(forms.ModelForm):
#     class Meta:
#         model = EwasteOrganizationRepresentative
#         fields = ['email', 'phone_number', 'role', 'password', 'account_name', 'phone_number', 'role', 'profile_picture', 'organization_name']
