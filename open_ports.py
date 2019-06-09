from argparse import ArgumentParser
from librouteros import connect

parser = ArgumentParser(description='Add addresses to Firewall list on router. Listname is FWKNOP_PROTO_PORT')
parser.add_argument('--routerip', help='IP address of router', default="192.168.1.1")
parser.add_argument('--routeruser', help='Username of API user on router', default="apiuser")
parser.add_argument('--routerpass', help='Password of API user on router', default="abc123")
parser.add_argument('--email', help='Email to send message to', default=None)
parser.add_argument('clientip', help='IP address of client, i.e the IP to add to address list')
parser.add_argument('protocol', help='Protocol, 6=tcp, 17=udp')
parser.add_argument('port', help='Port')
parser.add_argument('time', help='Length of time (in seconds) to keep address in list')
args = parser.parse_args()


api = connect(host=args.routerip, username=args.routeruser, password=args.routerpass)

time = int(args.time)

days = (time/(60*60*24))
hours = (time/(60*60) % 24)
mins = (time/60 % 60)
secs = (time % 60)

api(cmd='/ip/firewall/address-list/add', list="FWKNOP_{0}_{1}".format(args.protocol, args.port), address=args.clientip, timeout="{0}d {1:02d}:{2:02d}:{3:02d}".format(days,hours,mins,secs))

if(args.email != None):
    proto_string = ""
    if(args.protocol == "6"):
        proto_string = "tcp"
    elif(args.protocol == "17"):
        proto_string = "udp"
    api(cmd='/tool/e-mail/send', to=args.email, subject='Router: Port Opened', body='Given IP: {4} access to {5}:{6} for {0}d {1:02d}:{2:02d}:{3:02d}'.format(days,hours,mins,secs, args.clientip, proto_string, args.port))