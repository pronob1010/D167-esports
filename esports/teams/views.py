from django.shortcuts import render

# Create your views here.
def teams(request):
    
    return render(request, 'team/staff.html', {})

def teamdetails(request):
    return render(request, 'team/teamdetails.html', {})