from skimage import io
from matplotlib import pyplot as plt

img = io.imread('./AnnexinV.tif')

plt.imshow(img, interpolation=None, cmap='gray')
plt.show()
