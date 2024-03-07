import os
import numpy as np
from skimage import io
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from lmfit.models import GaussianModel

def subtract_background(img) -> "flatten img":
    th = threshold_otsu(img)
    mask = img > th
    ind_bg = np.nonzero(~mask)
    dat_bg = np.transpose([
        ind_bg[0], #y
        ind_bg[1], #x
        np.ones(ind_bg[0].shape[0]),
        img[~mask].flatten(), #z
        ])

    # plane function: z = plane[0]*y + plane[1]*x + plane[2]
    plane = np.linalg.inv(np.transpose(dat_bg[:,:3])@dat_bg[:,:3])@np.transpose(dat_bg[:,:3])@dat_bg[:,3]
    yy, xx = np.meshgrid(np.arange(img.shape[0]), np.arange(img.shape[1]))
    bg = plane[0]*yy + plane[1]*xx + plane[2]

    return img - bg

def align_by_centroid(mov) -> "aligned mov":
    x_list = []
    y_list = []
    for i in range(mov.shape[0]):
        img = mov[i]

        th = threshold_otsu(img)
        mask = img > th
        region = regionprops(label(mask))

        area = [r['area'] for r in region]
        y,x = region[np.argmax(area)]['centroid']
        x_list.append(x)
        y_list.append(y)

    dx_list = np.array(x_list) - np.mean(x_list)
    dy_list = np.array(y_list) - np.mean(y_list)
    dx_list = dx_list.astype(int)
    dy_list = dy_list.astype(int)

    pad_y_before = np.max(np.abs(dy_list))
    pad_y_after = np.max(np.abs(dy_list))
    pad_x_before = np.max(np.abs(dx_list))
    pad_x_after = np.max(np.abs(dx_list))

    mov_pad = np.zeros_like(mov)
    mov_pad = np.pad(mov_pad, pad_width=((0,0), (pad_y_before, pad_y_after), (pad_x_before, pad_x_after)))

    for i in range(mov.shape[0]):
        img = mov[i]
        dx = dx_list[i]
        dy = dy_list[i]

        img_pad = np.pad(img, ((pad_y_before-dy, pad_y_after+dy),(pad_x_before-dx, pad_x_after+dx)), constant_values=np.nan)
        mov_pad[i] = img_pad.copy()

    return mov_pad

def flatten_align(mov) -> "processed mov":
    mov_flatten = np.zeros_like(mov)
    for i in range(mov.shape[0]):
        mov_flatten[i] = subtract_background(mov[i])
    mov_aligned = align_by_centroid(mov_flatten)

    return mov_aligned

def projection(img):
    th = threshold_otsu(img[~np.isnan(img)])
    mask = img > th
    ind = np.nonzero(mask)
    dat = np.transpose([
            ind[0], #y
            ind[1], #x
            ])
    z = img[mask].flatten() #z
    X = StandardScaler(with_std=False).fit_transform(dat)
    pca = PCA(n_components=2)
    comp = pca.fit_transform(X)
    
    return comp, z

def fit_height(img):
    c, z = projection(img)
    x = c[:,1]

    mod = GaussianModel()
    par = mod.make_params(amplitude=10,center=0,sigma=1)
    out = mod.fit(z, par, x=x)
    return out.params['height'].value

if __name__ == "__main__":
    import sys
    import os
    cwd = os.path.dirname(os.path.realpath(__file__))
    file_path = str(sys.argv[1])

    mov = io.imread(os.path.join(cwd, file_path))
    mov = flatten_align(mov)
    img = np.mean(mov, axis=0)
    height = fit_height(img)

    print(f"height: {np.around(height, 2)} nm")
