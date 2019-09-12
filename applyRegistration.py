#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 15:43:08 2018

@author: luiscp
"""
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
from os.path import join as opj
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.ants import (ApplyTransforms)
experiment_dir = '/home/luiscp/Documents/Data/ADRC_90Plus/output'
output_dir = 'dwi_analysis'

subject_list = ['233','234','235','236','237','238','239','240','242','243','244','245','246','248','249','250','251','253','254','256','257','259']
#subject_list = ['259']
###############################
#specify nodes
###############################
appRegAp = Node(ApplyTransforms(dimension=3,
                                  interpolation=u'NearestNeighbor'),
                        name="appRegAp")

appRegAseg = Node(ApplyTransforms(dimension=3,
                                  interpolation=u'NearestNeighbor'),
                        name="appRegAseg")

appRegDTK = Node(ApplyTransforms(dimension=3,
                                  interpolation=u'NearestNeighbor'),
                        name="appRegDTK")

appReg2009 = Node(ApplyTransforms(dimension=3,
                                  interpolation=u'NearestNeighbor'),
                        name="appReg2009")


###############################
#specify input output
###############################
# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

dwi_file   = opj('seg_analysis','preproc','sub_{subject_id}','transformInverseWarped.nii.gz')
mat_file   = opj('seg_analysis','preproc','sub_{subject_id}','transform1InverseWarp.nii.gz')
aparc_file = opj('seg_analysis','preproc','sub_{subject_id}','aparc+aseg.nii.gz')
aseg_file  = opj('seg_analysis','preproc','sub_{subject_id}','aseg.nii.gz')
a2009_file = opj('seg_analysis','preproc','sub_{subject_id}','aparc.a2009s+aseg.nii.gz')
DKT_file   = opj('seg_analysis','preproc','sub_{subject_id}','aparc.DKTatlas+aseg.nii.gz')

templates = {'dwi': dwi_file,
             'mat': mat_file,
             'aparc': aparc_file,
             'aseg': aseg_file,
             'a2009':a2009_file,
             'DKT':DKT_file}

selectfiles = Node(SelectFiles(templates,
                               base_directory='/home/luiscp/Documents/Data/ADRC_90Plus/output/'),
                   name="selectfiles")

datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")
substitutions = [('_subject_id_', 'sub_'),
                 ]
datasink.inputs.substitutions = substitutions

###############################
#Specify workflow
###############################
preproc = Workflow(name='preproc')
preproc.base_dir = experiment_dir
                 
preproc.connect([(infosource, selectfiles, [('subject_id','subject_id')]),
                 (selectfiles, appRegAp, [('aparc', 'input_image'),
                                     ('dwi','reference_image'),
                                     ('mat','transforms')]),
                 (appRegAp,datasink,[('output_image','preproc.@aparc+aseg')]),
                 (selectfiles, appRegAseg, [('aseg', 'input_image'),
                                     ('dwi','reference_image'),
                                     ('mat','transforms')]),
                 (appRegAseg,datasink,[('output_image','preproc.@aseg')]),
                 (selectfiles, appRegDTK, [('a2009', 'input_image'),
                                     ('dwi','reference_image'),
                                     ('mat','transforms')]),
                 (appRegDTK,datasink,[('output_image','preproc.@DKTatlas')]),
                 (selectfiles, appReg2009, [('DKT', 'input_image'),
                                     ('dwi','reference_image'),
                                     ('mat','transforms')]),
                 (appReg2009,datasink,[('output_image','preproc.@a2009')]),
                 ])
#preproc.write_graph(graph2use='colored', format='png', simple_form=True)

preproc.run('MultiProc', plugin_args={'n_procs': 22})