"""
=============================================
Using an automated approach to coregistration
=============================================

This example shows how to use the coregistration functions to perform an
automated MEG-MRI coregistration via scripting.

.. warning:: The quality of the coregistration depends heavily upon the
             quality of the head shape points (HSP) collected during subject
             prepration and the quality of your T1-weighted MRI. Use with
             caution and check the coregistration error.
"""

# Author: Jon Houck <jon.houck@gmail.com>
#         Guillaume Favelier <guillaume.favelier@gmail.com>
#
# License: BSD-3-Clause

import os.path as op
import numpy as np

import mne
from mne.coreg import Coregistration
from mne.io import read_info


data_path = mne.datasets.sample.data_path()
subjects_dir = op.join(data_path, 'subjects')
subject = 'sample'

fname_raw = op.join(data_path, 'MEG', subject, subject + '_audvis_raw.fif')
info = read_info(fname_raw)
plot_kwargs = dict(subject=subject, subjects_dir=subjects_dir,
                   surfaces="head-dense", dig=True, eeg=[],
                   meg='sensors', show_axes=True,
                   coord_frame='meg')
view_kwargs = dict(azimuth=45, elevation=90, distance=0.6,
                   focalpoint=(0., 0., 0.))

# %%
# Set up the coregistration model
fiducials = "estimated"  # get fiducials from fsaverage
coreg = Coregistration(info, subject, subjects_dir, fiducials=fiducials)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# %%
# Do first a coregistration fit using only 3 fiducial points. This allows
# to find a good initial solution before further optimization using
# head shape points. This can also be useful to detect outlier head shape
# points which are too far from the skin surface. One can see for example
# that on this dataset there is one such point and we will omit it from
# the subsequent fit.
coreg.fit_fiducials(verbose=True)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# %%
# Next we refine the transformation using a few iteration of the
# Iterative Closest Point (ICP) algorithm. As the initial fiducials
# are obtained from fsaverage and not from precise manual picking in the
# GUI we do a fit with reduced weight for the nasion.
coreg.fit_icp(n_iterations=6, nasion_weight=2., verbose=True)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)

# %%
# It is now very clear that we have one point that is an outlier
# and that should be removed.
coreg.omit_head_shape_points(distance=5. / 1000)  # distance is in meters

# %%
# Do a final coregistration fit

# sphinx_gallery_thumbnail_number = 4
coreg.fit_icp(n_iterations=20, nasion_weight=10., verbose=True)
fig = mne.viz.plot_alignment(info, trans=coreg.trans, **plot_kwargs)
mne.viz.set_3d_view(fig, **view_kwargs)

dists = coreg.compute_dig_mri_distances() * 1e3  # in mm
print(
    f"Distance between HSP and MRI (mean/min/max):\n{np.mean(dists):.2f} mm "
    f"/ {np.min(dists):.2f} mm / {np.max(dists):.2f} mm"
)
