from django.shortcuts import render


def handler400(request, exception):
    """ Error Handler 400 - Bad Request """
    # in views for your home/index page
    # 1) import the following:
    # from django.core.exceptions import SuspiciousOperation
    # 2) add this line to the top of the function loading the home page
    # raise SuspiciousOperation("Test 400 Error")
    return render(request, "errors/400.html", status=400)


def handler403(request, exception):
    """ Error Handler 403 - Forbidden """
    # in views for your home/index page
    # 1) import the following:
    # from django.core.exceptions import PermissionDenied
    # 2) add this line to the top of the function loading the home page
    # raise PermissionDenied("Test 403 Error")
    return render(request, "errors/403.html", status=403)


def handler404(request, exception):
    """ Error Handler 404 - Page Not Found """
    # any fake url, such as: /test
    return render(request, "errors/404.html", status=404)


def handler500(request):
    """ Error Handler 500 - Internal Server Error """
    # 1) add this line to the top of the function loading the home page
    # raise Exception("Test 500 Error")
    return render(request, "errors/500.html", status=500)
