import xmlrpclib
import scipy as sp
import matplotlib.pyplot as plt
import sys

# parse args
if len(sys.argv) > 2 : proxy = xmlrpclib.ServerProxy("http://"+sys.argv[1]+":"+sys.argv[2])
else : proxy = xmlrpclib.ServerProxy("http://localhost:5020")

# read in image
img = plt.imread("moonlanding.png")
imglist = img.tolist()

# use remote rpc calls to modify images
distorted1 = sp.array(proxy.image_distort_1(imglist))
distorted2 = sp.array(proxy.image_distort_2(imglist))
distorted3 = sp.array(proxy.image_distort_3(imglist))

# save distorted images
plt.imshow(distorted1).set_cmap("Greys")
plt.savefig("distorted1.png")
plt.imshow(distorted2).set_cmap("Greys")
plt.savefig("distorted2.png")
plt.imshow(distorted3).set_cmap("Greys")
plt.savefig("distorted3.png")

# recover the original images
fixed1 = distorted1 * 2.0
fixed2 = sp.append(distorted2[2*sp.shape(distorted2)[0]/3:],distorted2[:2*sp.shape(distorted2)[0]/3],0)
fixed3 = distorted3 - sp.append(sp.append(img[::2,::2],img[::2,::2],0),sp.append(img[::2,::2],img[::2,::2],0),1)

# save the restored images
plt.imshow(fixed1).set_cmap("Greys")
plt.savefig("fixed1.png")
plt.imshow(fixed2).set_cmap("Greys")
plt.savefig("fixed2.png")
plt.imshow(fixed3).set_cmap("Greys")
plt.savefig("fixed3.png")


