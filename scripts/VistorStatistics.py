from ipware import get_client_ip
from datetime import datetime
from cyshg.models import StatisticsData

#TODO: get the remote IP from the user, instead of the load balacer's IP. Given the current structure, may not possible.

def clientStatistics(request):
    white_list_IPs = [
        '128.219.164.9',  # netscaler load balancer
    ]

    IP = clientIP(request)
    browser_family = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_family = request.user_agent.os.family
    os_version = request.user_agent.os.version_string
    device_family = request.user_agent.device.family

    browser_info = '%s (%s); %s (%s); %s' % (browser_family, browser_version, os_family, os_version, device_family)

    if IP[0] in white_list_IPs and browser_family == 'Other':
        pass
    else:
        url = vistingPage(request)



        u = StatisticsData.objects.create()
        u.IP = IP[0]
        u.IPType = IP[1]
        u.PagesVisted = url
        u.Browser = browser_info
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
