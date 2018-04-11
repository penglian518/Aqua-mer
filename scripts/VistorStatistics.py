from ipware import get_client_ip
from datetime import datetime
from cyshg.models import StatisticsData


def clientStatistics(request):
    IP = clientIP(request)
    url = vistingPage(request)

    u = StatisticsData.objects.create()
    u.IP = IP[0]
    u.IPType = IP[1]
    u.PagesVisted = url
    u.Date = datetime.now()
    u.save()

    return


def clientIP(request):
    ip, is_routable = get_client_ip(request)
    if ip is None:
        # Unable to get the client's IP address
        IP = ('-', 'None')
    else:
        # We got the client's IP address
        if is_routable:
            # The client's IP address is publicly routable on the Internet
            IP = (ip, 'public')
        else:
            # The client's IP address is private
            IP = (ip, 'private')
    return IP

def vistingPage(request):
    urls = {
        'ABSOLUTE_ROOT_URL': request.build_absolute_uri(),
    }
    return urls['ABSOLUTE_ROOT_URL']
