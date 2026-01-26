from django import forms
from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from api_auth.models import UserProfile


@login_required
def user_profile(request):
    """
    Отображает профиль пользователя с аватаром.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profiles/profile.html', {
        'profile': profile,
    })

@login_required
def update_avatar(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    """
    Форма для загрузки/обновления аватара.
    """
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аватар успешно обновлён!')
            return redirect('user_profile')  # перенаправляем на профиль
    else:
        form = UserProfileForm(instance=profile)


    return render(request, 'profiles/update_avatar.html', {
        'form': form,
    })

class UserProfileForm(forms.ModelForm):
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Проверка размера (например, до 5 МБ)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 5 МБ.')
            # Проверка формата
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = avatar.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Поддерживаются только форматы: JPG, JPEG, PNG, GIF.')
        return avatar

    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }