#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 16:44:13 2018

@author: luiscp
"""
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
from os.path import join as opj
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node 
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.ants import (RegistrationSynQuick)
experiment_dir = '/home/luiscp/Documents/Data/ADRC_90Plus/output'
output_dir = 'seg_analysis'

subject_list = ['233','234','235','236','237','238','239','240','242','243','244','245','246','248','249','250','251','253','254','256','257','259']
#subject_list = ['259']
###############################
#specify nodes
###############################
reg = Node(RegistrationSynQuick(dimension=3,
                        transform_type=u's'),
                        name="reg")

###############################
#specify input output
###############################
# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

dwi_file   = opj('dwi_analysis','preproc','sub_{subject_id}','data_brain.nii.gz')
t1_file    = opj('seg_analysis','preproc','sub_{subject_id}','brain.nii.gz')

templates = {'dwi': dwi_file,
             't1': t1_file}

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
                 (selectfiles, reg, [('dwi', 'moving_image'),
                                     ('t1','fixed_image')]),
                 (reg,datasink,[('forward_warp_field','preproc.@forward_warp_field'),
                                ('inverse_warp_field','preproc.@inverse_warp_field'),
                                ('inverse_warped_image','preproc.@inverse_warped_image'),
                                ('out_matrix','preproc.@out_matrix'),
                                ('warped_image','preproc.@warped_image')]),
                 ])
#preproc.write_graph(graph2use='colored', format='png', simple_form=True)

preproc.run('MultiProc', plugin_args={'n_procs': 22})