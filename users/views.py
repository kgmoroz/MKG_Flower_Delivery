from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:product_list')
    else:
        form = UserCreationForm()

    # подключаем crispy helper, чтобы появилась кнопка
    helper = FormHelper()
    helper.form_method = 'post'
    helper.add_input(Submit('submit', 'Зарегистрироваться'))

    return render(request, 'registration/signup.html',
                  {'form': form, 'helper': helper})
