from argparse import ArgumentParser
from librouteros import connect

parser = ArgumentParser(description='Add addresses to Firewall list on router. Listname is FWKNOP_PROTO_PORT')
parser.add_argument('--routerip', help='IP address of router', default="192.168.1.1")
parser.add_argument('--routeruser', help='Username of API user on router', default="apiuser")
parser.add_argument('--routerpass', help='Password of API user on router', default="abc123")
parser.add_argument('clientip', help='IP address of client, i.e the IP to add to address list', required=True)
parser.add_argument('protocol', help='Protocol, 6=tcp, 17=udp', required=True)
parser.add_argument('port', help='Port', required=True)
parser.add_argument('time', help='Length of time (in seconds) to keep address in list', required=True)
args = parser.parse_args()


api = connect(host=args.routerip, username=args.routeruser, password=args.routerpass)

time = int(args.time)

days = (time/(60*60*24))
hours = (time/(60*60) % 24)
mins = (time/60 % 60)
secs = (time % 60)

api(cmd='/ip/firewall/address-list/add', list="FWKNOP_{0}_{1}".format(args.protocol, args.port), address=args.clientip timeout="{0}d {1:02d}:{2:02d}:{3:02d}".format(days,hours,mins,secs))
