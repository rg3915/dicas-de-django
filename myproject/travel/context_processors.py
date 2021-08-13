from .models import Travel


def travel_count(request):
    travel = Travel.objects.all()
    context = {'total_travel': travel.count()}
    return context
