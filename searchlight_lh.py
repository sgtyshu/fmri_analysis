import pandas as pd
from nilearn import datasets
import numpy as np
import os
from os.path import join as pjoin
from magicbox.io.io import CiftiReader
# We fetch 2nd subject from haxby datasets (which is default)
import raven_module
from nilearn import datasets, surface
from sklearn import neighbors
from nilearn.decoding.searchlight import search_light
from sklearn.linear_model import Lasso
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.svm import SVC
import multiprocessing

template_brain = '/nfs/t2/raven/data/bold/derivatives/ciftify/sub-01/MNINonLinear/Results/ses-raven_task-action/ses-raven_task-action_hp200_s4_level2.feat/sub-01_ses-raven_task-action_level2_cope_const_obj_number_hp200_s4.dscalar.nii'
lh_mapping = CiftiReader(template_brain).get_stru_pos('CIFTI_STRUCTURE_CORTEX_LEFT')[3]
# lh_mapping is the mapping list from 32494(including corpus callosum) to 29696 (excluding corpus callosum)
cope_path = '../result/level2_cope/'
cope = raven_module.sort_cope_list(os.listdir(cope_path))
cope_path = []
sub_flag = raven_module.get_raven_sub_flag()

for i in cope:
    path = pjoin('../result/level2_cope',i)
    cope_path.append(path)


# Average voxels 5 mm close to the 3d pial surface

# To define the :term:`BOLD` responses
# to be included within each searchlight "sphere"
# we define an adjacency matrix based on the inflated surface vertices such
# that nearby surfaces are concatenated within the same searchlight.
infl_mesh = '/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/mesh/left.inflated_32k_fs_LR.surf.gii'
coords, _ = surface.load_surf_mesh(infl_mesh)
# This is the radius of searchlight
radius = 3.0
nn = neighbors.NearestNeighbors(radius=radius)
adjacency = nn.fit(coords).radius_neighbors_graph(coords).tolil()

def mysearchlight(sub):
    print ('processing ' + sub)
    X,y,groups = raven_module.mvpa_attributes_get_one_sub_run_cope_list(sub)
    X = X[:29696,:].T
    lh = np.zeros((72,32492))
    for index,data in enumerate(X):
        lh[index][lh_mapping] = X[index] 
    X = lh
    print (X.shape,y.shape,groups.shape)

    # Simple linear estimator preceded by a normalization step
    estimator = make_pipeline(StandardScaler(), SVC(kernel='linear',C=1))

    # Define cross-validation scheme
    cv = LeaveOneGroupOut()

    # Cross-validated search light
    scores = search_light(X, y, estimator, adjacency, cv=cv, n_jobs=1, groups=groups)
    scores = scores[lh_mapping]
    raven_module.save_lh_as_dscalar(scores,'../result/searchlight_result',sub + '_searchlight_attributes_lh.dscalar.nii')
    print ('done with ' + sub)

processes = []
for sub in sub_flag:
    process = multiprocessing.Process(target=mysearchlight, args=(sub,))
    processes.append(process)
    process.start()

for process in processes:
    process.join()