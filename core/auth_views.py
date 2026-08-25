from hashlib import sha256

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods


MAX_FAILURES = 5
WINDOW_SECONDS = 15 * 60
LOCK_SECONDS = 30 * 60


def _client_ip(request):
    # O Render entrega este cabeçalho pelo proxy HTTPS. REMOTE_ADDR é o fallback.
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',', 1)[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')


def _key(prefix, request, username):
    value = f'{_client_ip(request)}:{username.casefold()}'
    return f'auth:{prefix}:{sha256(value.encode()).hexdigest()}'


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = AuthenticationForm(request, data=request.POST or None)
    username = request.POST.get('username', '').strip()
    failures_key = _key('failures', request, username)
    lock_key = _key('lock', request, username)
    is_locked = bool(username and cache.get(lock_key))

    if request.method == 'POST':
        if is_locked:
            form.add_error(None, 'Login temporariamente bloqueado. Tente novamente mais tarde.')
        elif form.is_valid():
            user = form.get_user()
            cache.delete(failures_key)
            login(request, user)
            next_url = request.POST.get('next', '')
            if url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
                return redirect(next_url)
            return redirect('index')
        else:
            # Conta apenas falhas reais e mostra sempre a mesma mensagem do Django.
            failures = cache.get(failures_key, 0) + 1
            cache.set(failures_key, failures, WINDOW_SECONDS)
            if failures >= MAX_FAILURES:
                cache.set(lock_key, True, LOCK_SECONDS)
                cache.delete(failures_key)
                form.non_field_errors()
                form.add_error(None, 'Login temporariamente bloqueado. Tente novamente mais tarde.')

    return render(request, 'registration/login.html', {'form': form})
