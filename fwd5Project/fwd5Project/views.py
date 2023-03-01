from django.http import HttpResponse 

def handler404(request, exception):
    return HttpResponse("404: Page not Found!")
    # return HttpResponse("404: Page not Found! <br><br> <button onclick="" href="https://google.com'";>Go to Homepage")