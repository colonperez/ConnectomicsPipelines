#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 11:47:22 2018

@author: Luis M. Colon-Perez, PhD

Analyze dwi data with Amico

"""
import amico
import os
from os.path import join as opj
import shutil
from nipype.interfaces.fsl import ImageMaths

# Select NODDI ("NODDI") or ActiveAX ("CylinderZeppelinBall") model to calculate scalars
amico_model="CylinderZeppelinBall"
# Directory to work inout and outputs
experiment_dir="/home/luiscp/Documents/Data/ADRC_90Plus/output/dwi_analysis/preproc/"
# Subject identofiers
#subject_list = ['259']
subject_list = ['233','234','235','236','237','238','239','240','242','243','244','245','246','248','249','250','251','253','254','256','257','259']


amico.core.setup()
count=0
while count < len(subject_list):
    
    sub='sub_'+subject_list[count]
    print 'working '+sub
    os.chdir(experiment_dir+'/'+sub)
    #location/directory containing all the data for this study/subject
    ae = amico.Evaluation(experiment_dir,sub)

    #load data
    if amico_model=="NODDI":
        mask_file="data_brain_mask.nii.gz"
        # generate scheme file from the bvals/bvecs
        amico.util.fsl2scheme('data.bval', 'data.bvec')
        amico_dir = opj(experiment_dir,sub,amico_model)
        if not os.path.exists(amico_dir):
            os.mkdir(amico_dir)
        os.rename('data.scheme', amico_dir+'/noddi.scheme')

    if amico_model=="CylinderZeppelinBall":
        threshL = ImageMaths(op_string= '-thr 2 -uthr 2')
        threshL.inputs.in_file = experiment_dir+sub+'/aseg_trans.nii.gz'
        threshL.inputs.out_file = experiment_dir+sub+'/wmL_mask.nii.gz'
        threshL.run()
        threshR = ImageMaths(op_string= '-thr 41 -uthr 41')
        threshR.inputs.in_file = experiment_dir+sub+'/aseg_trans.nii.gz'
        threshR.inputs.out_file = experiment_dir+sub+'/wmR_mask.nii.gz'
        threshR.run()
        add_string = '-add '+experiment_dir+sub+'/wmR_mask.nii.gz'
        wm = ImageMaths(op_string= add_string)
        wm.inputs.in_file = experiment_dir+sub+'/wmL_mask.nii.gz'
        wm.inputs.out_file = experiment_dir+sub+'/wm_mask.nii.gz'
        wm.run()
        mask_file="wm_mask.nii.gz" 
        os.remove('wmR_mask.nii.gz')
        os.remove('wmL_mask.nii.gz')
        
    ae.load_data(dwi_filename = 'data.nii.gz', scheme_filename = amico_dir+"/scheme.scheme", mask_filename = mask_file, b0_thr = 0)
    ae.set_model(amico_model)
    ae.generate_kernels()
    ae.load_kernels()
    ae.fit()
    ae.save_results()
    
    if amico_model=="NODDI":
        os.rename('AMICO/NODDI/config.pickle', 'NODDI/config.pickle')
        os.rename('AMICO/NODDI/FIT_dir.nii.gz', 'NODDI/noddi_dir.nii.gz')
        os.rename('AMICO/NODDI/FIT_ICVF.nii.gz', 'NODDI/noddi_ICVF.nii.gz')
        os.rename('AMICO/NODDI/FIT_ISOVF.nii.gz', 'NODDI/noddi_ISOVF.nii.gz')
        os.rename('AMICO/NODDI/FIT_OD.nii.gz', 'NODDI/noddi_OD.nii.gz')
        shutil.rmtree('AMICO')
    
    count+=1