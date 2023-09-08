# Data processing pipeline

import subprocess
import os
import numpy as np
import pandas as pd


# Three part, fmriprep, ciftify, and HCP Pipeline
class Pipeline(object):

    def __init__(self, data_inpath, data_outpath, prep_workdir, ciftify_workdir, fsf_dir, subject_id, task='action'):
        self.data_inpath = data_inpath
        self.data_outpath = data_outpath
        self.prep_workdir = prep_workdir
        self.subject_id = subject_id
        self.task = task
        self.ciftify_workdir = ciftify_workdir
        self.fsf_dir = fsf_dir

    def _decompose_ev(self, subj_id, ses_id, run_id, ev_cond):
        """
        -------------------
        Decompose paradigm into different conditions
        we promise:
        1: const_edge_number
        2: const_obj_number
        3: const_symbolic_number
        4: dist3_edge_number
        5: dist3_obj_number
        6: dist3_symbolic_number
        7: prog_edge_number
        8: prog_obj_number
        9: prog_symbolic_number
        10: visual_stimuli

        Parameters:
        -----------
        ev_cond[pd.DataFrame]: experimental variable paradigm
        """
        labeldict = {1:'const_edge_number', 2:'const_obj_number', 3:'const_symbolic_number', 4:'dist3_edge_number', 5:'dist3_obj_number', 
                     6:'dist3_symbolic_number', 7:'prog_edge_number', 8:'prog_obj_number', 9:'prog_symbolic_number', 10:'visual_stimuli'}
        #print(np.unique(ev_cond['trial_type']))
        #print(np.arange(len(labeldict)))
        assert (
            np.all(np.unique(ev_cond['trial_type']) == np.arange(1, len(labeldict) + 1))), "Conditions are not complete."
        for lbl in labeldict.keys():
            ev_cond_tmp = ev_cond[ev_cond['trial_type'] == lbl]
            ev_cond_decomp = np.zeros((3, len(ev_cond_tmp)))
            ev_cond_decomp[0, :] = np.array(ev_cond_tmp['onset'])
            ev_cond_decomp[1, :] = np.array(ev_cond_tmp['duration'])
            ev_cond_decomp[2, :] = np.ones(len(ev_cond_tmp))
            ev_cond_decomp = ev_cond_decomp.T
            outpath = os.path.join(self.ciftify_workdir, subj_id, 'MNINonLinear', 'Results',
                                   ses_id + '_' + 'task-' + self.task + '_' + 'run-' + run_id, 'EVs/')
            if not os.path.isdir(outpath):
                subprocess.call('mkdir ' + outpath, shell=True)
                
            np.savetxt(os.path.join(outpath, labeldict[lbl] + '.txt'), ev_cond_decomp, fmt='%-6.1f', delimiter='\t',
                       newline='\n')

    def prepare_EVs(self):
        """
        """
        '''
        for subj_id in self.subject_id:
            # Load ses_id
            session_id = os.listdir(os.path.join(self.data_inpath, subj_id))
            for ses_id in session_id:
                # Load run_id
                with open(os.path.join(self.data_inpath, subj_id,
                                       ses_id, 'tmp', 'run_info',
                                       self.task + '.rlf'), 'r') as f:
                    runs_id = f.read().splitlines()
        '''
        
        runs_id = ['01','02','03','04','05','06','07','08']
        ciftify_run_id = ['1','2','3','4','5','6','7','8']
        subj_id = self.subject_id[0]
        ses_id = 'ses-raven'
        for i in range(len(runs_id)):
            ev_cond = pd.read_csv(os.path.join(self.data_inpath, subj_id, ses_id, 'func',
                                                subj_id + '_' + ses_id + '_' + 'task-' + self.task + '_' + 'run-' + runs_id[i] + '_events.tsv'),
                                    sep='\t')
            self._decompose_ev(subj_id, ses_id, ciftify_run_id[i], ev_cond)

    def _modify_fsf1(self, fsfpath, to_runid, from_runid='run-a'):
        """
        """
        sedfsf1_command = " ".join(['sed', '-i',
                                    '\'s#{0}#{1}#g\''.format(from_runid, to_runid), fsfpath])
        subprocess.call(sedfsf1_command, shell=True)
            
    def prepare_fsf(self):
        """
        """
        fsflevel1_indir = os.path.join(self.fsf_dir, 'level1.fsf')
        fsflevel2_indir = os.path.join(self.fsf_dir, 'level2.fsf')
        for subj_id in self.subject_id:
            result_dir = os.path.join(self.ciftify_workdir, subj_id,
                                      'MNINonLinear', 'Results')
            # Load ses_id
            session_id = os.listdir(os.path.join(self.data_inpath, subj_id))
            #此时的session_id是ses-raven
            #print(session_id)
            for ses_id in session_id:
                #with open(os.path.join(self.data_inpath, subj_id,
                #                       ses_id, 'tmp', 'run_info',
                #                       self.task + '.rlf'), 'r') as f:
                #    runs_id = f.read().splitlines()
                #if len(runs_id) != 6:
                #    continue

                #这里自己写了runID，覆盖了之前读这个rlf文件的
                runs_id = ['1','2','3','4','5','6','7','8']

                fsflevel2_outdir = os.path.join(result_dir,
                                                ses_id + '_' + 'task-' + self.task)
                print(fsflevel2_outdir)
                if not os.path.isdir(fsflevel2_outdir):
                    os.makedirs(fsflevel2_outdir)

                #将fsflevel2复制到对应路径下 
                cpfsf2_command = ' '.join(['cp', fsflevel2_indir, os.path.join(fsflevel2_outdir,
                                                                               ses_id + '_' + 'task-' + self.task + '_hp200_s4_level2.fsf')])
                
                self.cpfsf2_commmand = cpfsf2_command
                subprocess.call(cpfsf2_command, shell=True)
                
                for run_id in runs_id:
                    fsflevel1_outdir = os.path.join(result_dir,
                                                    ses_id + '_' + 'task-' + self.task + '_' + 'run-' + run_id)
                    print(fsflevel1_outdir)
                    if not os.path.isdir(fsflevel1_outdir):
                        os.makedirs(fsflevel1_outdir)
                    cpfsf1_command = ' '.join(['cp', fsflevel1_indir, os.path.join(fsflevel1_outdir,
                                                                                   ses_id + '_' + 'task-' + self.task + '_' + 'run-' + run_id + '_hp200_s4_level1.fsf')])
                    subprocess.call(cpfsf1_command, shell=True)
                    self._modify_fsf1(os.path.join(fsflevel1_outdir,
                                                   ses_id + '_' + 'task-' + self.task + '_' + 'run-' + run_id + '_hp200_s4_level1.fsf'),
                                      'run-' + run_id)

    def run_taskglm(self):
        """
        """
        lowres = '32'
        grayres = '2'
        origFWHM = '2'
        confound = 'NONE'
        finalFWHM = '4'
        vba = 'NO'
        regname = 'NONE'
        parcellation = 'NONE'
        parcefile = 'NONE'
        for subj_id in self.subject_id:
            # Load ses_id
            session_id = os.listdir(os.path.join(self.data_inpath, subj_id))
            lvl2task_list = []
            for ses_id in session_id:
                lvl2task_list.append(ses_id + '_' + 'task-' + self.task)
                # Load run_id
                #with open(os.path.join(self.data_inpath, subj_id,
                #                       ses_id, 'tmp', 'run_info',
                #                       self.task + '.rlf'), 'r') as f:
                #    runs_id = f.read().splitlines()

                #这里自己写了runID，覆盖了之前读这个rlf文件的
                runs_id = ['1','2','3','4','5','6','7','8']
                
                lvl1tasks_list = []
                for run_id in runs_id:
                    # prepare lvl1tasks
                    lvl1tasks_list.append(ses_id + '_' + 'task-' + self.task + '_' + 'run-' + run_id)
                lvl1tasks = '@'.join(lvl1tasks_list)
                lvl1fsfs = lvl1tasks
            lvl2task = '@'.join(lvl2task_list)
            lvl2fsf = 'ses-raven_task-raven_'

            enter_setup_scriptdir_command = ' '.join(['cd',
                                                      '/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/HCPpipelines/HCPpipelines-master/Examples/Scripts/'])
            #source_command =' '.join(['source',
            #                          'SetUpHCPPipeline.sh'])
            #source_command = 'source SetUpHCPPipeline.sh'
            #subprocess.check_output(['bash', '-c', source_command])
            #source_command = './source_script.sh'

            enter_hcp_pipeline_task_analysis_command = ' '.join (['cd',
                                                                  '/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/HCPpipelines/HCPpipelines-master/TaskfMRIAnalysis/'])
            
            export_HCPPIPEDIR_command = ' '.join(['export',
                                                  'HCPPIPEDIR=/nfs/h1/userhome/liyifan/workingdir/Raven-fmri/HCPpipelines/HCPpipelines-master'])

            taskglm_command = ' '.join(['./TaskfMRIAnalysis.sh',
                                        '--study-folder=' + self.ciftify_workdir,
                                        '--subject=' + subj_id,
                                        '--lvl1tasks=' + lvl1tasks,
                                        '--lvl1fsfs=' + lvl1fsfs,
                                        '--lvl2task=' + lvl2task,
                                        '--lvl2fsf=' + lvl2fsf,
                                        '--lowresmesh=' + lowres,
                                        '--grayordinatesres=' + grayres,
                                        '--origsmoothingFWHM=' + origFWHM,
                                        '--confound=' + confound,
                                        '--finalsmoothingFWHM=' + finalFWHM,
                                        #'--temporalfilter=' + tempfilter,
                                        '--vba=' + vba,
                                        '--regname=' + regname,
                                        '--parcellation=' + parcellation,
                                        '--parcellationfile=' + parcefile])
            # self.taskglm_command = taskglm_command
            try:
                #subprocess.run('source ~/.bashrc',shell=True)
                subprocess.check_call(enter_setup_scriptdir_command, shell=True)
                subprocess.check_call(export_HCPPIPEDIR_command, shell=True)
                #subprocess.check_call(source_command, shell=True)

                subprocess.run(['source','SetUpHCPPipeline.sh'])
                subprocess.check_call(enter_hcp_pipeline_task_analysis_command, shell=True)
                #print(taskglm_command)
                subprocess.check_call(taskglm_command, shell=True)
                


            except subprocess.CalledProcessError:
                raise Exception('TASKGLM: Error happened in subject {}'.format(subj_id))

    def run_pipeline(self):
        #self.run_fmriprep()
        #self.run_fslreg()
        #self.run_ciftify()
        self.prepare_EVs()
        self.prepare_fsf()
        self.run_taskglm()