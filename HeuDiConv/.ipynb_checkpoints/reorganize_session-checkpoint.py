#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Vincent (Qing Wang)
# @Date:   2022-4-14 12:00:00
"""
======================================================
Reorganize dataset (PPMI) folder for heudiconv conversion:
Input  dataset folder structure: dataset/modality/date/imageID/*.dcm

Output dataset folder structure: dataset/ses/imageID/*.dcm
Output dataset info table      : mr_proc/tab_data/*_dcminfo.csv
======================================================
"""

import sys
from pathlib import Path
import glob
import os
import shutil

# setting up codes dir and working dir
code_path_str='/data/pd/ppmi/mr_proc'
project_dir_str = '/data/pd/ppmi/'
code_dir = Path(code_path_str)
sys.path.append(code_path_str)

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Input of pamameters: ')
    parser.add_argument('--data', type=str, default = 'data')
    args = parser.parse_args()
    return args

def del_dir_safe(folder_):
    for filename in os.listdir(folder_):
        file_path = os.path.join(folder_, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def main(dataset_name):
    """Entry point"""
    """1. input images"""
    if dataset_name=='PPMI':
        dataset_path = Path(project_dir_str+dataset_name) # change this line according to your local dir
        dataset_out_path    = Path(project_dir_str+dataset_name+'_SessionOrganized')
        ppmi_img_dl_file    = code_dir / 'tab_data'  / 'PPMI_3T_sdMRI_3_07_2022.csv'  # Inormation from download database.
        dataset_out_df_path = Path(code_dir / 'tab_data'  / 'PPMI_3T_sdMRI_3_07_2022_dcminfo.csv')  # save information of dicom dataset
        ppmi_img_dl_data    = pd.read_csv(ppmi_img_dl_file, sep=',')

    elif dataset_name=='ADNI':
        print('To be implemented for '+dataset_name)
    else:
        print('To be implemented for default setting')
        
    # Prepare new organizied dataset_dir
    if not dataset_out_path.exists():
        os.makedirs(dataset_out_path)
    else:  
        del_dir_safe(dataset_out_path)
        print(str(dataset_out_path)+' already exists, cleared!')
        
    # Get subj list from original dataset folder
    sub_list = os.listdir(dataset_path)
    dcm_df = pd.DataFrame(data={'Image Data ID':[], 'Visit':[], 'Subject':[], 'Modality':[], 'Image Date':[]})
    # Organizing dataset according to sessions for each subject
    for subj_ in sub_list:
        image_data_list=[]
        image_tab_df = ppmi_img_dl_data[ppmi_img_dl_data['Subject']==subj_].loc[:,['Image Data ID', 'Visit']].copy()
        # make new subject and session dir 
        sub_dir = dataset_out_path / subj_
        if not (sub_dir).exists():
            os.makedirs(sub_dir)
            else:
                print(subj_+' subject dir already exists!')
        # make new session dir for subj_
        for ses_str in image_tab_df.Visit.unique():
            ses_dir = dataset_out_path / subj_ / str(ses_str)
            if not ses_dir.exists():
                os.makedirs(ses_dir)
            else:
                print(subj_+' '+ 'session dir '+str(ses_str) + ' dir already exists!')
        # copy files from raw dataset folder to the new folder
        for modality_str_ in os.listdir(dataset_path / subj_):
            for date_str_ in os.listdir(dataset_path / subj_ / modality_str_):
                for img_str_ in os.listdir(dataset_path / subj_ / modality_str_ / date_str_):
                    curr_ses=str(image_tab_df[image_tab_df['Image Data ID']==img_str_].iloc[0,1])
                    alldcm = glob.glob(str(dataset_path / subj_ / modality_str_ / date_str_ / img_str_)+'/*')
                    source_dir = str(dataset_path / subj_ / modality_str_ / date_str_ / img_str_)
                    target_dir = str(sub_dir / curr_ses / img_str_)
                    os.makedirs(target_dir)
                    [shutil.copy2(dcm_file_, target_dir) for dcm_file_ in alldcm]
                    print(subj_+' '+modality_str_+' '+date_str_+' '+img_str_+' copied to ', sub_dir, curr_ses, img_str_)
                    subj_dcm_df = {'Image Data ID':[img_str_], 'Visit':[curr_ses], 'Subject':[subj_], 'Modality':[modality_str_], 'Image Date':[date_str_]}
                    dcm_df=dcm_df.append(pd.DataFrame(data=subj_dcm_df))
                    
    # save dcm info dataframe to csv 
    if not dataset_out_df_path.exists():
        dcm_df.to_csv(dataset_out_df_path)
    else:
        os.unlink(dataset_out_df_path)
        dcm_df.to_csv(dataset_out_df_path)
    return 1

if __name__ == '__main__':
    args=get_args()
    dataset_name_=args.data;    
    print("The input data folder: ", DATA_DIR, type(DATA_DIR))
    main(dataset_name_)
