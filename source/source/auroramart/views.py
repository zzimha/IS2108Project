from django.shortcuts import render, redirect

def home(request):
    """Home page - redirects to storefront index"""
    return redirect('storefront:index')