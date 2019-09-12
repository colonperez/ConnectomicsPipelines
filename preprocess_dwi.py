#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 11:42:21 2018

@author: Luis M. Colon-Perez, PhD

Preprocess DWI data. Includes: motion correction, smoothing, and skull stripping.
 
"""
###############################
#import modules
###############################
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
import os
from shutil import copyfile
from os.path import join as opj
from nipype.interfaces.fsl import (BET, SUSAN, MCFLIRT)
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node 

###############################
#experiment params
###############################
experiment_dir = '/home/luiscp/Documents/Data/ADRC_90Plus/output'
output_dir = 'dwi_analysis'

subject_list = ['233','234','235','236','237','238','239','240','242','243','244','245','246','248','249','250','251','253','254','256','257','259']
#subject_list = ['259']
###############################
#specify nodes
###############################

#Motion Correction (FSL)
motioncor = Node(MCFLIRT(output_type = u'NIFTI_GZ',
                         interpolation=u'spline',
                         mean_vol=True,
                         cost=u'mutualinfo'), 
               name="motioncor")

#Smoothing (FSL)
smooth = Node(SUSAN(fwhm = 1.0,
                    output_type =u'NIFTI_GZ',
                    brightness_threshold=10),
                    name="smooth")

#Skull remove (FSL)
skullstrip = Node(BET(frac = 0.4,
                      output_type =u'NIFTI_GZ',
                      robust = True,
                      mask = True),
                      name="skullstrip")

###############################
#specify input output
###############################
# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

dwi_file = opj('sub_{subject_id}','data.nii.gz')

templates = {'dwi': dwi_file}

selectfiles = Node(SelectFiles(templates,
                               base_directory='/home/luiscp/Documents/Data/ADRC_90Plus'),
                   name="selectfiles")

datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")
substitutions = [('_subject_id_', 'sub_'),
                 ('_mcf_smooth', '')]
datasink.inputs.substitutions = substitutions

###############################
#Specify workflow
###############################

preproc = Workflow(name='preproc')
preproc.base_dir = experiment_dir
                 
preproc.connect([(infosource, selectfiles, [('subject_id','subject_id')]),
                 (selectfiles, motioncor, [('dwi', 'in_file')]),
                 (motioncor, smooth, [('out_file', 'in_file')]),
                 (smooth, skullstrip, [('smoothed_file', 'in_file')]),
                 (smooth, datasink, [('smoothed_file', 'preproc.@susan')]),
                 (skullstrip, datasink,[('mask_file','preproc.@mask'),
                                        ('out_file','preproc.@sst')]),
                 ])
#preproc.write_graph(graph2use='colored', format='png', simple_form=True)

preproc.run('MultiProc', plugin_args={'n_procs': 16})

os.chdir(experiment_dir)
count = 0
while count < len(subject_list):
    sub='sub_'+subject_list[count]
    filen = opj('..',sub,'data.bval')
    fileo = opj('dwi_analysis','preproc',sub,'data.bval')
    copyfile(filen, fileo)
    filen = opj('..',sub,'data.bvec')
    fileo = opj('dwi_analysis','preproc',sub,'data.bvec')
    copyfile(filen, fileo)
    count += 1