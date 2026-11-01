from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Partner
from .forms import PartnerForm
@login_required(login_url="messen_login")
def dashboard(request):
    if not request.user.has_perm("partners.view_partner"):raise PermissionDenied
    return render(request,"partners/dashboard.html",{"partners":Partner.objects.all()})
@login_required(login_url="messen_login")
def edit(request,pk=None):
    perm="change_partner" if pk else "add_partner"
    if not request.user.has_perm("partners."+perm):raise PermissionDenied
    obj=get_object_or_404(Partner,pk=pk) if pk else None
    form=PartnerForm(request.POST or None,request.FILES or None,instance=obj)
    if request.method=="POST" and form.is_valid():
        form.save();messages.success(request,"Partner gespeichert.");return redirect("partners_dashboard")
    return render(request,"partners/form.html",{"form":form,"editing":bool(obj)})
@login_required(login_url="messen_login")
def delete(request,pk):
    if not request.user.has_perm("partners.delete_partner"):raise PermissionDenied
    obj=get_object_or_404(Partner,pk=pk)
    if request.method=="POST":obj.delete();messages.success(request,"Partner gelöscht.");return redirect("partners_dashboard")
    return render(request,"partners/delete.html",{"item":obj})
@require_GET
def published(request):
    return JsonResponse([{"id":p.pk,"name":p.name,"country":p.country,"city":p.city,"address":p.address,"phone":p.phone,"email":p.email,"domain":p.domain,"description":p.description,"eyebrow":p.eyebrow,"specialties":p.specialties,"source":p.source_url,"theme":p.theme,"tagline":p.tagline,"brandColor":p.brand_color,"heroImage":p.hero_image,"officialLogo":p.official_logo,"region":p.region,"lat":p.latitude,"lon":p.longitude,"logo":p.logo.url if p.logo else p.logo_url} for p in Partner.objects.filter(published=True)],safe=False)
