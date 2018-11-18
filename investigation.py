# ua: update all (based on instance_id, and also by IPs)
# uaa: update all (as above) and also add to "special IPs" list
# ui: update only based on instance_id
# i: investigate


ips = {}
for q in bad:
    instance_id = q[0][0]
    modes = tuple(set(t[1] for t in q))
    ip_addresses = tuple(set(t[2] for t in q))
    countries = tuple(set(t[3] for t in q))
    pingbacks = Instance.objects.get(instance_id=instance_id).pingbacks.all()
    last_seen = [str(pingbacks.filter(mode=mode).order_by("saved_at").last().saved_at.date()) for mode in modes]
    counts = [pingbacks.filter(mode=mode).count() for mode in modes]
    ips[instance_id] = {"modes": modes, "counts": counts, "last_seen": last_seen, "ips": ip_addresses, "countries": countries, "action": ""}
    
print(json.dumps(ips, indent=4))





for i, d in recs.items():
    if d["action"].startswith("u"):
        mode = [m for m in d["modes"] if m][0]
        Pingback.objects.filter(instance_id=i, mode="").update(mode=mode)
        if d["action"].startswith("ua"):
            for ip in d["ips"]:
                ps = Pingback.objects.exclude(instance_id=i).filter(mode="", ip_id=ip)
                instances = set([p.instance for p in ps])
                for ins in instances:
                    if not ins.last_mode:
                        ins.last_mode = mode
                        ins.save()
                ps.update(mode=mode)
                if d["action"] == "uaa":
                    print('    "{}": "{}",'.format(ip, mode))




def printer(indent=0):

    def p(msg, ind=0):
        print("\t" * (indent + ind) + msg)

    return p


def print_instance(instance, indent=0):

    p = printer(indent)
        
    p(instance.instance_id)
    p("database_id: " + instance.database_id, ind=1)
    p("platform:    " + instance.platform, ind=1)
    p("node_id:     " + instance.node_id, ind=1)
    p("first_seen:  " + str(instance.first_seen), ind=1)
    p("last_seen:   " + str(instance.last_seen), ind=1)
    p("last_mode:   " + instance.last_mode, ind=1)


pp = printer(indent=2)

for i, d in recs.items():
    if d["action"] == "i":
        instance = Instance.objects.get(instance_id=i)
        print_instance(instance)

        for p in instance.pingbacks.order_by("saved_at"):
            pp(str(p.saved_at.date()))
            pp("ver:       " + p.kolibri_version, ind=1)
            pp("mode:      " + p.mode, ind=1)
            pp("ip:        " + p.ip_id, ind=1)
            pp("city:      " + p.ip.city, ind=1)
            pp("country:   " + p.ip.country_name, ind=1)
            pp("instances: " + str(Instance.objects.filter(pingbacks__ip_id=p.ip_id).distinct().count()))



# find all instances that have the same node_id or database_id
p = printer(indent=0)
for i in Instance.objects.filter(pingbacks__ip_id="137.110.111.190", last_mode="").distinct():
    p(i.instance_id)
    for ins in (Instance.objects.filter(node_id=i.node_id).exclude(instance_id=i.instance_id) | Instance.objects.filter(database_id=i.database_id).exclude(instance_id=i.instance_id)).distinct():
        print_instance(ins, indent=1)
