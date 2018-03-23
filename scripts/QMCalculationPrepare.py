from PLg09 import constants, g09prepare, pbsPrepare, g09checkResults, NWprepare, NWcheckResults, Arrowsprepare
import os

class QMCalculationPrepare:
    def __init__(self):
        self.DjangoHome = '/home/p6n/workplace/website/cyshg'
        self.JobLocation = 'media'


    def gen_conf_dict(self, obj):
        '''genearte the conf dict according to obj'''
        step1_qm_conf = {
            # A group of calculation contains many steps
            'Group_name': '%s_%s' % (obj.Name, obj.JobID),

            # the step number of this calculation, starts from 1
            'Step': '1',

            # whether start from previous step, if 'Step' is 1, will NOT able to start from previous
            'Start_from_previous': True,
            'Geom': 'Checkpoint',
            'Guess': 'Read',

            # As 0 means False in Python, all numbers here should be input as string!
            'Charge': obj.QMCharge,

            # if not specified, will calculate it according to odd or even number of electrons
             'Spin': obj.QMMultiplicity,

            # if not specified, use B3LYP and 6-31G(d)
            'functional': obj.QMFunctional,
            'basis_set': obj.QMBasisSet,

            # put all options for Opt and Freq in braces,
            'Opt': '(MaxCyc=100)',
            'Freq': True,

            # 'Pseudo' is a switch to use pseudo potential, set it to 'Read' or True to turn on
            'Pseudo': True,
            # if turned on, should put the elements in a list.
            'Pseudo_elements': ['Hg'],
            # if turned on, default potential is SDD
            'Pseudo_potential': 'SDD',
            # if turned on, the option of Gen should put here and separated by blank. e.g. 'Gen 5D'
            'Pseudo_basis': '',

            # similart to Opt, Freq, put all options in braces for 'SCF'
            'SCF': '(MaxCyc=200, Tight)',
            'Integral': 'UltraFine',
            'NoSymm': True,

            # similart to 'Pseudo', 'SCRF' is a switch
            'SCRF': True,
            'SCRF_model': obj.QMSolvationModel,
            'SCRF_solvent': obj.QMSolvent,
            'SCRF_others': '',
            'SCRF_parameters_nw': 'radii.parm',
            'SCRF_parameters_content_nw': 'Hg 1.55',

            # others options could be put here
            'Others': ''
        }

        # optimzation or frequencies
        if obj.QMCalType in ['Opt-Freq']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = True
        elif obj.QMCalType in ['Opt']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = False
        elif obj.QMCalType in ['Freq']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = True
        elif obj.QMCalType in ['Energy']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = False
            step1_qm_conf['Energy'] = True
            step1_qm_conf['Theory'] = 'dft'

        # solvation model
        if obj.QMCavitySurface in ['Default']:
            step1_qm_conf['SCRF_Read'] = False
            step1_qm_conf['SCRF_parameters_nw'] = ''
        else:
            step1_qm_conf['SCRF_Read'] = True
            step1_qm_conf['SCRF_ReadConf'] = 'Surface=%s\nAlpha=%s' % (obj.QMCavitySurface, str(obj.QMScalingFactor))


        resource_conf = {
            # number of processors to be used
            'NProc': str(obj.QMProcessors),
            # memory
            'Mem': '%sGB' % str(obj.QMMemory),

            # chk file name will be the same as the input file

            # path to access the coordinates in .xyz file,
            # will be read by pybel
            # the filename will be used as the name of .com .chk .log
            'path_to_input_xyz': '%s/%s/%s/jobs/%s/%s-%s.xyz' %
                                 (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, obj.Name, obj.JobID)
        }

        pbs_conf = {

            # required settings
            'PBS_jobname': '',
            'PBS_molname': '',
            'PBS_molname_of_previous_step': '',

            'PBS_queue': 'batch',
            'PBS_nodes': '1',
            'PBS_ppn': '4',
            'PBS_walltime': '24:00:00',
            # 'PBS_qos': 'burst',
            # 'PBS_grouplist': 'cades-user',
            # 'PBS_account': 'bsd-burst',
            'PBS_qos': 'std',
            'PBS_grouplist': 'cades-bsd',
            'PBS_account': 'bsd',
        }

        project_conf = {
            'USENWChem': True,

            'XYZ_folderpath': resource_conf['path_to_input_xyz'],
            'XYZ_foldername': '',

            'Local_pwd': '.',
            'Local_calculation_folder_name': 'calculations',
            'Local_output_folder_name': 'output',

            'Remote_cluster_name': 'condo',
            'Remote_calculation_folder_name': '/home/p6n/workplace/website'
        }

        project_conf_sub1 = {
            'Reaction_foldername': 'reactions',
            'Reaction_dataset': 'logK_ALL.txt'
        }

        # which software to use
        if obj.QMSoftware in ['Gaussian']:
            project_conf['USENWChem'] = False
        if obj.QMSoftware in ['NWChem']:
            project_conf['USENWChem'] = True

        conf = {}
        conf.update(step1_qm_conf)
        conf.update(resource_conf)
        conf.update(pbs_conf)
        conf.update(project_conf)
        conf.update(project_conf_sub1)

        # use Pseudo potential or not
        fcon = open(conf['path_to_input_xyz']).readlines()

        # get the elements
        elements_in_xyz = list(set([i.strip().split()[0] for i in fcon[2:] if len(i.strip().split()) > 0]))
        #print elements_in_xyz

        # common element within conf
        element_common = [i for i in elements_in_xyz if i in conf['Pseudo_elements']]
        #print element_common

        if len(element_common) == 0:
            conf['Pseudo'] = False
        else:
            conf['Pseudo'] = True

        return conf

    def gen_g09input(self, conf):
        g09input, inp_name = g09prepare.genInputFile(conf)
        return g09input

    def gen_NWinput(self, conf):
        NWinput, inp_name = NWprepare.genInputFile(conf)
        return NWinput
    def gen_Arrowsinput(self, conf):
        NWinput = Arrowsprepare.genInputFile(conf)
        return NWinput
