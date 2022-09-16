from planar_Navigation import planarNav

t = 0
myNavi = planarNav();
myNavi.set_init(lat0=24.997959, lon0=121.422696, hei0=100, head0=0)

for i in range(100):
	lat, lon = myNavi.track(t=t, wz=0.0, speed=10, hei=100)
	print(lat, end=', ')
	print(lon)
	t += 1