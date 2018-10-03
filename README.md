# Odoo Cluster
Open Source Odoo Cluster implement


architecture;
===
<img  src="https://github.com/openliu/Odoo-Cluster/blob/master/OdooCluster-openliu.jpeg?raw=true" />


libs
----------------------------
		Redis - Session Storage & Orm cache  ;  --Must
		pgpool II- used in posgresql cluster ;  --Optional

usage
----------------------------
		1.prepare more than two servers, one is the master ,the others are slave(s)
		2.copy the files to the odoo server directory, and replace the old files;
		3.modify the master odoo.conf file:
			session_redis_url=redis://@redis-ip:6379/0
			ormcache_redis_url=redis://@redis-ip:6379/0      ;strongly recommand the redis instance used in ormchace is not previous one
			max_cron_threads = x                             ;(x>1)
		4.modify all the slave(s) odoo.conf file:
			session_redis_url=redis://@redis-ip:6379/0       ;same as master
			ormcache_redis_url=redis://@redis-ip:6379/0      ;same as master
			max_cron_threads = 0
