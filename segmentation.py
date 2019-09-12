#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 15:19:21 2018

@author: luiscp
"""
#testing Github
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
from os.path import join as opj
from nipype.interfaces.fsl import SUSAN
from nipype.interfaces.freesurfer import (ReconAll, MRIConvert)
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.io import SelectFiles, DataSink
from nipype import Workflow, Node, MapNode

experiment_dir = '/home/luiscp/Documents/Data/ADRC_90Plus/output'
output_dir = 'seg_analysis'

subject_list = ['233','234','235','236','237','238','239','240','242','243','244','245','246','248','249','250','251','253','254','256','257','259']
#subject_list = ['259']
###############################
#specify nodes
###############################
smooth = Node(SUSAN(fwhm = 8.0,
                    output_type =u'NIFTI_GZ',
                    brightness_threshold=20),
                    name="smooth")

#freesurfer recon-all segmentation
recon_all = Node(ReconAll(subject_id ='subject_id',
                 directive = u'all'),
                 name="recon_all")

mr_convertT1=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertT1")
mr_convertaseg=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertaseg")
mr_convertaparc_aseg=MapNode(MRIConvert(out_type=u'niigz'),
                name="mr_convertaparc_aseg",iterfield='in_file')
mr_convertbrainmask=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertbrainmask")
mr_convertbrain=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertbrain")
mr_convertwmparc=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertwmparc")
mr_convertwm=Node(MRIConvert(out_type=u'niigz'),
                name="mr_convertwm")
###############################
#specify input output
###############################
# Infosource - a function free node to iterate over the list of subject names
infosource = Node(IdentityInterface(fields=['subject_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list)]

t1_file = opj('sub_{subject_id}','t1_mprage.nii.gz')

templates = {'t1': t1_file}

selectfiles = Node(SelectFiles(templates,
                               base_directory='/home/luiscp/Documents/Data/ADRC_90Plus'),
                   name="selectfiles")

datasink = Node(DataSink(base_directory=experiment_dir,
                         container=output_dir),
                name="datasink")
substitutions = [('_subject_id_', 'sub_'),
                 ('_out',''),
                 ('_mr_convertaparc_aseg0/',''),
                 ('_mr_convertaparc_aseg1/',''),
                 ('_mr_convertaparc_aseg2/','')]

datasink.inputs.substitutions = substitutions

###############################
#Specify workflow
###############################

preproc = Workflow(name='preproc')
preproc.base_dir = experiment_dir

preproc.connect([(infosource, selectfiles, [('subject_id','subject_id')]),
                 (selectfiles, smooth, [('t1', 'in_file')]),
                 (smooth, recon_all, [('smoothed_file', 'T1_files')]),
                 (recon_all, mr_convertT1,[('T1', 'in_file')]),
                 (recon_all, mr_convertaseg,[('aseg','in_file')]),
                 (recon_all, mr_convertaparc_aseg,[('aparc_aseg','in_file')]),
                 (recon_all, mr_convertbrainmask,[('brainmask','in_file')]),
                 (recon_all, mr_convertbrain,[('brain','in_file')]),
                 (recon_all, mr_convertwmparc,[('wmparc','in_file')]),
                 (recon_all, mr_convertwm,[('wm','in_file')]),
                 (mr_convertT1, datasink,[('out_file','preproc.@T1')]),
                 (mr_convertaseg, datasink,[('out_file','preproc.@aseg')]),
                 (mr_convertaparc_aseg, datasink,[('out_file','preproc.@aparc_aseg')]),
                 (mr_convertbrainmask, datasink,[('out_file','preproc.@brainmask')]),
                 (mr_convertbrain, datasink,[('out_file','preproc.@brain')]),
                 (mr_convertwmparc, datasink,[('out_file','preproc.@wmparc')]),
                 (mr_convertwm, datasink,[('out_file','preproc.@wm')]),
                 ])
#preproc.write_graph(graph2use='colored', format='png', simple_form=True)

preproc.run('MultiProc', plugin_args={'n_procs': 22})
