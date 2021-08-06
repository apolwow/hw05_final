from http import HTTPStatus

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def page_not_found(request, exception):
    context = {'path': request.path}
    return render(
        request, 'misc/404.html', context, status=HTTPStatus.NOT_FOUND
    )


@require_http_methods(['GET'])
def server_error(request):
    return render(
        request, 'misc/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
