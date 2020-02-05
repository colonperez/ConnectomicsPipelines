#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 11:47:22 2018

@author: Luis M. Colon-Perez, PhD
         Sergio Ramirez II, Student

Analyze dwi data with MDT

"""
# import amico
import mdt
import os
from os.path import join as opj
#import shutil
#from nipype.interfaces.fsl import ImageMaths

# Select NODDI ("NODDI") or ActiveAX ("CylinderZeppelinBall") model to calculate scalars
mdt_model="ActiveAx"
# Directory to work inout and outputs
experiment_dir="/opt/test/output/dwi_analysis/preproc"
# Subject identofiers
#subject_list = ['259']
subject_list = ['234']


# amico.core.setup()
count=0
while count < len(subject_list):
    
    sub='sub_'+subject_list[count]
    print ('working '+sub)
    os.chdir(experiment_dir+'/'+sub)
    #location/directory containing all the data for this study/subject

    #load data
    if mdt_model=="NODDI_test":
        mask_file="data_brain_mask.nii.gz"
        # generate scheme file from the bvals/bvecs
        protocol = mdt.create_protocol(
                bvecs = 'data.bvec', bvals = 'data.bval',
                out_file = experiment_dir + '/' + sub + '/data.prtcl')
        mdt_dir = opj(experiment_dir,sub,mdt_model)
        if not os.path.exists(mdt_dir):
            os.mkdir(mdt_dir)
            
        input_data = mdt.load_input_data('data.nii.gz', 
                                'data.prtcl', 
                                'data_brain_mask.nii.gz')
        
        test = mdt.get_optimization_inits('NODDI', input_data, 'output')
        mdt.fit_model('NODDI', input_data, 'output')

    if mdt_model=="ActiveAx":
        mask_file = "data_brain_mask.nii.gz"
        
        protocol = mdt.create_protocol(
                bvecs = 'data.bvec', bvals = 'data.bval',
                out_file = experiment_dir + '/' + sub + '/data.prtcl')
        mdt_dir = opj(experiment_dir, sub, mdt_model)
        if not os.path.exists(mdt_dir):
            os.mkdir(mdt_dir)
        
        with open("data.prtcl", 'r') as file:
            vals = file.readlines()
        
        for num in range(len(vals)):
            if ("#" in vals[num]):
                vals[num] = vals[num][:-2] + "G,delta,Delta\n"
            elif ("1.500000000000000000e+09" in vals[num]):
                vals[num] = vals[num][:-26] + "\t37.89" + "\t25.440" + "\t38.040" + "\n"
            elif ("3.000000000000000000e+09" in vals[num]):
                vals[num] = vals[num][:-26] + "\t53.59" + "\t25.440" + "\t38.040" + "\n"
            else:
                vals[num] = vals[num][:-26] + "\t0\t0\t0\n"
                
        file.close()
        
        with open("data.prtcl", "w") as file:
            file.writelines(vals)
            
        file.close()
                
            
        input_data = mdt.load_input_data('data.nii.gz',
                                         'data.prtcl',
                                         'data_brain_mask.nii.gz')
        mdt.fit_model('ActiveAx', input_data, 'output')
        
    
# ***** VERY IMPORTANT ***** GOES WITH LUIS EMAIL DOC
# TE PARAM: 102
# TR PARAM: 3500
# ***** VERY IMPORTANT *****
    
    count+=1