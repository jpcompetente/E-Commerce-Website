from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from .models import User, Address

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'bio', 'phone', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'full_name', 'phone', 'street', 'city', 'province', 'postal_code', 'country', 'is_default']

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    return render(request, 'users/profile.html', {'profile_user': profile_user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def settings_view(request):
    profile_form = EditProfileForm(instance=request.user)
    address_form = AddressForm()
    addresses = request.user.addresses.all()
    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('users:settings')
        elif 'save_address' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
                return redirect('users:settings')
    return render(request, 'users/settings.html', {
        'profile_form': profile_form,
        'address_form': address_form,
        'addresses': addresses,
    })

@login_required
def delete_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    return redirect('users:settings')

@login_required
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    return redirect('users:settings')
