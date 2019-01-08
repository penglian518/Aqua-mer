from PLg09 import constants, g09prepare, pbsPrepare, g09checkResults, NWprepare, NWcheckResults, Arrowsprepare
import os, logging, subprocess
from copy import deepcopy
import pybel

class QMCalculationPrepare:
    def __init__(self):
        self.DjangoHome = '/home/p6n/workplace/website/cyshg'
        self.JobLocation = 'media'
        # get the element table
        self.ele_Table = pybel.ob.OBElementTable()

    def gen_conf_dict(self, obj):
        '''
        genearte the conf dict according to obj. If obj.Name in pka or logk, return dict for each molecule,
        otherwise, return only one dict
        '''
        if obj.Name in ['pka']:
            # prepare for conf_A
            conf_A = self.obj_to_dict(obj=obj)

            conf_HA = self.obj_to_dict_HA(obj=obj)

            return conf_A, conf_HA
        elif obj.Name in ['logk']:
            # prepare for conf_L
            conf_L = self.obj_to_dict(obj=obj)

            conf_ML = self.obj_to_dict_HA(obj=obj)

            conf_M = self.obj_to_dict_M(obj=obj)

            return conf_L, conf_ML, conf_M
        else:
            conf = self.obj_to_dict(obj=obj)
            conf_gas = self.obj_to_dict_gas(obj=obj)
            return conf, conf_gas

    def obj_to_dict(self, obj):
        if obj.Name in ['pka']:
            complex_name = 'A'
        elif obj.Name in ['logk']:
            complex_name = 'L'

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

        resource_conf = {
            # number of processors to be used
            'NProc': str(obj.QMProcessors),
            # memory
            'Mem': '%sGB' % str(obj.QMMemory),

            # chk file name will be the same as the input file

            # path to access the coordinates in .xyz file,
            # will be read by pybel
            # the filename will be used as the name of .com .chk .log
            #'path_to_input_xyz': '%s/%s/%s/jobs/%s/%s-%s.xyz' %
            #                     (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, obj.Name, obj.JobID)

            'path_to_input_xyz': '%s/%s/%s/jobs/%s/%s_%s-%s.xyz' %
                                 (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, complex_name, obj.Name,
                                  obj.JobID)
        }

        # read the coordinates
        mol = pybel.readfile('xyz', resource_conf['path_to_input_xyz']).next()
        # get all elements and all metals
        all_elements_metal = list(set([self.ele_Table.GetSymbol(i.atomicnum) for i in mol if i.OBAtom.IsMetal()]))


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

            # if there is metal in the molecule, should list them explicitly.
            scrf_str = 'Surface=%s\nAlpha=%s\n' % (obj.QMCavitySurface, str(obj.QMScalingFactor))
            if len(all_elements_metal) > 0:
                scrf_str += 'ModifySph\n'
                for ele in all_elements_metal:
                    if ele == 'Hg':
                        scrf_str += '\nHg 1.55 %s' % str(obj.QMScalingFactor)
                    else:
                        scrf_str += '\n%s %s %s' % \
                                    (ele, self.ele_Table.GetCovalentRad(self.ele_Table.GetAtomicNum(ele)), str(obj.QMScalingFactor))
            step1_qm_conf['SCRF_ReadConf'] = scrf_str


        if obj.Name in ['pka', 'logk']:
            resource_conf['path_to_input_xyz'] = '%s/%s/%s/jobs/%s/%s_%s-%s.xyz' % (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, complex_name, obj.Name, obj.JobID)

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
        # print elements_in_xyz

        # common element within conf
        element_common = [i for i in elements_in_xyz if i in conf['Pseudo_elements']]
        # print element_common

        if len(element_common) == 0:
            conf['Pseudo'] = False
        else:
            conf['Pseudo'] = True

        # for logk calculations, always use Gen keyword to generate basis set
        if obj.Name in ['logk']:
            conf['Pseudo'] = True

        return conf

    def obj_to_dict_HA(self, obj):

        if obj.Name in ['pka']:
            complex_name = 'HA'
        elif obj.Name in ['logk']:
            complex_name = 'ML'

        # prepare for conf_HA
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
            'Charge': obj.QMChargeP1,

            # if not specified, will calculate it according to odd or even number of electrons
            'Spin': obj.QMMultiplicityP1,

            # if not specified, use B3LYP and 6-31G(d)
            'functional': obj.QMFunctionalP1,
            'basis_set': obj.QMBasisSetP1,

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
            'SCRF_model': obj.QMSolvationModelP1,
            'SCRF_solvent': obj.QMSolventP1,
            'SCRF_others': '',
            'SCRF_parameters_nw': 'radii.parm',
            'SCRF_parameters_content_nw': 'Hg 1.55',

            # others options could be put here
            'Others': ''
        }

        resource_conf = {
            # number of processors to be used
            'NProc': str(obj.QMProcessorsP1),
            # memory
            'Mem': '%sGB' % str(obj.QMMemoryP1),

            # chk file name will be the same as the input file

            # path to access the coordinates in .xyz file,
            # will be read by pybel
            # the filename will be used as the name of .com .chk .log
            'path_to_input_xyz': '%s/%s/%s/jobs/%s/%s_%s-%s.xyz' %
                                 (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, complex_name, obj.Name, obj.JobID)
        }

        # read the coordinates
        mol = pybel.readfile('xyz', resource_conf['path_to_input_xyz']).next()
        # get all elements and all metals
        all_elements_metal = list(set([self.ele_Table.GetSymbol(i.atomicnum) for i in mol if i.OBAtom.IsMetal()]))


        # optimzation or frequencies
        if obj.QMCalTypeP1 in ['Opt-Freq']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = True
        elif obj.QMCalTypeP1 in ['Opt']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = False
        elif obj.QMCalTypeP1 in ['Freq']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = True
        elif obj.QMCalTypeP1 in ['Energy']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = False
            step1_qm_conf['Energy'] = True
            step1_qm_conf['Theory'] = 'dft'

        # solvation model
        if obj.QMCavitySurfaceP1 in ['Default']:
            step1_qm_conf['SCRF_Read'] = False
            step1_qm_conf['SCRF_parameters_nw'] = ''
        else:
            step1_qm_conf['SCRF_Read'] = True
            #step1_qm_conf['SCRF_ReadConf'] = 'Surface=%s\nAlpha=%s\nModifySph\n\nHg 1.55 %s' % \
            #    (obj.QMCavitySurfaceP1, str(obj.QMScalingFactor), str(obj.QMScalingFactorP1))

            # if there is metal in the molecule, should list them explicitly.
            scrf_str = 'Surface=%s\nAlpha=%s\n' % (obj.QMCavitySurfaceP1, str(obj.QMScalingFactor))
            if len(all_elements_metal) > 0:
                scrf_str += 'ModifySph\n'
                for ele in all_elements_metal:
                    if ele == 'Hg':
                        scrf_str += '\nHg 1.55 %s' % str(obj.QMScalingFactorP1)
                    else:
                        scrf_str += '\n%s %s %s' % \
                                    (ele, self.ele_Table.GetCovalentRad(self.ele_Table.GetAtomicNum(ele)), str(obj.QMScalingFactorP1))
            step1_qm_conf['SCRF_ReadConf'] = scrf_str


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
        if obj.QMSoftwareP1 in ['Gaussian']:
            project_conf['USENWChem'] = False
        if obj.QMSoftwareP1 in ['NWChem']:
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
        # print elements_in_xyz

        # common element within conf
        element_common = [i for i in elements_in_xyz if i in conf['Pseudo_elements']]
        # print element_common

        if len(element_common) == 0:
            conf['Pseudo'] = False
        else:
            conf['Pseudo'] = True

        # for logk calculations, always use Gen keyword to generate basis set
        if obj.Name in ['logk']:
            conf['Pseudo'] = True

        return conf

    def obj_to_dict_M(self, obj):
        # prepare for conf_M
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
            'Charge': obj.QMChargeM,

            # if not specified, will calculate it according to odd or even number of electrons
            'Spin': obj.QMMultiplicityM,

            # if not specified, use B3LYP and 6-31G(d)
            'functional': obj.QMFunctionalM,
            'basis_set': obj.QMBasisSetM,

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
            'SCRF_model': obj.QMSolvationModelM,
            'SCRF_solvent': obj.QMSolventM,
            'SCRF_others': '',
            'SCRF_parameters_nw': 'radii.parm',
            'SCRF_parameters_content_nw': 'Hg 1.55',

            # others options could be put here
            'Others': ''
        }

        resource_conf = {
            # number of processors to be used
            'NProc': str(obj.QMProcessorsM),
            # memory
            'Mem': '%sGB' % str(obj.QMMemoryM),

            # chk file name will be the same as the input file

            # path to access the coordinates in .xyz file,
            # will be read by pybel
            # the filename will be used as the name of .com .chk .log
            'path_to_input_xyz': '%s/%s/%s/jobs/%s/M_%s-%s.xyz' %
                                 (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, obj.Name, obj.JobID)
        }

        # read the coordinates
        mol = pybel.readfile('xyz', resource_conf['path_to_input_xyz']).next()
        # get all elements and all metals
        all_elements_metal = list(set([self.ele_Table.GetSymbol(i.atomicnum) for i in mol if i.OBAtom.IsMetal()]))

        # optimzation or frequencies
        if obj.QMCalTypeM in ['Opt-Freq']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = True
        elif obj.QMCalTypeM in ['Opt']:
            step1_qm_conf['Opt'] = '(MaxCyc=100)'
            step1_qm_conf['Freq'] = False
        elif obj.QMCalTypeM in ['Freq']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = True
        elif obj.QMCalTypeM in ['Energy']:
            step1_qm_conf['Opt'] = False
            step1_qm_conf['Freq'] = False
            step1_qm_conf['Energy'] = True
            step1_qm_conf['Theory'] = 'dft'

        # solvation model
        if obj.QMCavitySurfaceM in ['Default']:
            step1_qm_conf['SCRF_Read'] = False
            step1_qm_conf['SCRF_parameters_nw'] = ''
        else:
            step1_qm_conf['SCRF_Read'] = True
            #step1_qm_conf['SCRF_ReadConf'] = 'Surface=%s\nAlpha=%s' % (
            #    obj.QMCavitySurfaceM, str(obj.QMScalingFactorM))
            #step1_qm_conf['SCRF_ReadConf'] = 'Surface=%s\nAlpha=%s\nModifySph\n\nHg 1.55 %s' % \
            #    (obj.QMCavitySurfaceM, str(obj.QMScalingFactor), str(obj.QMScalingFactorM))

            # if there is metal in the molecule, should list them explicitly.
            scrf_str = 'Surface=%s\nAlpha=%s\n' % (obj.QMCavitySurfaceM, str(obj.QMScalingFactor))
            if len(all_elements_metal) > 0:
                scrf_str += 'ModifySph\n'
                for ele in all_elements_metal:
                    if ele == 'Hg':
                        scrf_str += '\nHg 1.55 %s' % str(obj.QMScalingFactorM)
                    else:
                        scrf_str += '\n%s %s %s' % \
                                    (ele, self.ele_Table.GetCovalentRad(self.ele_Table.GetAtomicNum(ele)), str(obj.QMScalingFactorM))
            step1_qm_conf['SCRF_ReadConf'] = scrf_str

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
        if obj.QMSoftwareM in ['Gaussian']:
            project_conf['USENWChem'] = False
        if obj.QMSoftwareM in ['NWChem']:
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
        # print elements_in_xyz

        # common element within conf
        element_common = [i for i in elements_in_xyz if i in conf['Pseudo_elements']]
        # print element_common

        if len(element_common) == 0:
            conf['Pseudo'] = False
        else:
            conf['Pseudo'] = True

        # for logk calculations, always use Gen keyword to generate basis set
        if obj.Name in ['logk']:
            conf['Pseudo'] = True

        return conf

    def obj_to_dict_gas(self, obj):
        if obj.Name in ['pka']:
            complex_name = 'A'
        elif obj.Name in ['logk']:
            complex_name = 'L'
        elif obj.Name in ['gsolv']:
            complex_name = 'gas'

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
            'SCRF': False,
            'SCRF_model': '',
            'SCRF_solvent': '',
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
        step1_qm_conf['SCRF_Read'] = False
        step1_qm_conf['SCRF_parameters_nw'] = ''

        resource_conf = {
            # number of processors to be used
            'NProc': str(obj.QMProcessors),
            # memory
            'Mem': '%sGB' % str(obj.QMMemory),

            # chk file name will be the same as the input file

            # path to access the coordinates in .xyz file,
            # will be read by pybel
            # the filename will be used as the name of .com .chk .log
            'path_to_input_xyz': '%s/%s/%s/jobs/%s/%s-%s.xyz' % (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, obj.Name, obj.JobID)
        }

        if obj.Name in ['pka', 'logk']:
            resource_conf['path_to_input_xyz'] = '%s/%s/%s/jobs/%s/%s_%s-%s.xyz' % (self.DjangoHome, self.JobLocation, obj.Name, obj.JobID, complex_name, obj.Name, obj.JobID)

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
        # print elements_in_xyz

        # common element within conf
        element_common = [i for i in elements_in_xyz if i in conf['Pseudo_elements']]
        # print element_common

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

class QMResultsCalculation:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.DjangoHome = '/home/p6n/workplace/website/cyshg'
        self.JobLocation = 'media'
        self.obabel = '/home/p6n/anaconda2/bin/obabel'


    def QMSoftware(self, outputfile):
        try:
            fcon = open(outputfile).readlines()
        except:
            fcon = []

        if len([i for i in fcon if i.find('Gaussian, Inc.  All Rights Reserved') > 0]) > 0:
            software = 'Gaussian'
        elif len([i for i in fcon if i.find('Northwest Computational Chemistry Package (NWChem)') > 0]) > 0:
            software = 'NWChem'
        else:
            software = 'Unknown'
        return software

    def pKa_formula(self, Gaq_A, Gaq_AH, Gaq_H=-270.30):
        '''

        AH <-> A + H K

        pKa = (deltaG)/RT

        :param Gaq_A:  in a.u. Value from 'Sum of electronic and thermal Free Energies'
        :param Gaq_AH: in a.u. Value from 'Sum of electronic and thermal Free Energies'
        :param Gaq_H: in kcal/mol.
        '''
        return ((Gaq_A - Gaq_AH)*constants.h2kcal + Gaq_H)/(2.303 * constants.RT)


    def logK_formula(self, Gaq_M, Gaq_L, Gaq_ML):
        '''
        M + L <-> ML   K

        lnK = -(deltaG)/RT

        :param Gaq_M:  in a.u. Value from 'Sum of electronic and thermal Free Energies'
        :param Gaq_L: in a.u. Value from 'Sum of electronic and thermal Free Energies'
        :param Gaq_ML: in a.u.

        :return in kcal/mol.
        '''

        deltaG_standard_state_corretion = 1.89

        return -1*((Gaq_ML - Gaq_M - Gaq_L)*constants.h2kcal - deltaG_standard_state_corretion)/(2.303 * constants.RT)

    def Gsolv_formula(self, Gaq, Ggas):
        '''
        L(gas) <-> L(aq)

        lnK = -(deltaG)/RT
        '''

        deltaG_standard_state_corretion = 1.89

        return (Gaq - Ggas)*constants.h2kcal


    def Calc_pKa(self, obj):
        # path for the output files
        A_out = obj.UploadedOutputFile.file.name
        HA_out = obj.UploadedOutputFileP1.file.name
        workdir = os.path.dirname(A_out)


        # The output is from Gaussian or NWChem
        A_out_software = obj.QMSoftwareOutput
        HA_out_software = obj.QMSoftwareOutputP1

        # get the energies and convert to xyz
        if A_out_software in ['Gaussian']:
            Gaq_A = g09checkResults.finalE(open(A_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/A_out.xyz' % (self.obabel, A_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % A_out)
        elif A_out_software in ['NWChem']:
            Gaq_A = NWcheckResults.finalE(open(A_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/A_out.xyz' % (self.obabel, A_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % A_out)
        else:
            Gaq_A = 0.0

        if HA_out_software in ['Gaussian']:
            Gaq_HA = g09checkResults.finalE(open(HA_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/HA_out.xyz' % (self.obabel, HA_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % HA_out)
        elif HA_out_software in ['NWChem']:
            Gaq_HA = NWcheckResults.finalE(open(HA_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/HA_out.xyz' % (self.obabel, HA_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % HA_out)
        else:
            Gaq_HA = 0.0

        # calculate the pKa
        pKa = self.pKa_formula(Gaq_A=Gaq_A, Gaq_AH=Gaq_HA)

        return pKa, Gaq_A, Gaq_HA

    def Calc_logK(self, obj):
        # path for the output files
        L_out = obj.UploadedOutputFile.file.name
        ML_out = obj.UploadedOutputFileP1.file.name
        M_out = obj.UploadedOutputFileM.file.name
        workdir = os.path.dirname(L_out)


        # The output is from Gaussian or NWChem
        L_out_software = obj.QMSoftwareOutput
        ML_out_software = obj.QMSoftwareOutputP1
        M_out_software = obj.QMSoftwareOutputM

        # get the energies and convert to xyz
        if L_out_software in ['Gaussian']:
            Gaq_L = g09checkResults.finalE(open(L_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/L_out.xyz' % (self.obabel, L_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % L_out)
        elif L_out_software in ['NWChem']:
            Gaq_L = NWcheckResults.finalE(open(L_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/L_out.xyz' % (self.obabel, L_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % L_out)
        else:
            Gaq_L = 0.0

        if ML_out_software in ['Gaussian']:
            Gaq_ML = g09checkResults.finalE(open(ML_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/ML_out.xyz' % (self.obabel, ML_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % ML_out)
        elif ML_out_software in ['NWChem']:
            Gaq_ML = NWcheckResults.finalE(open(ML_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/ML_out.xyz' % (self.obabel, ML_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % ML_out)
        else:
            Gaq_ML = 0.0

        if M_out_software in ['Gaussian']:
            Gaq_M = g09checkResults.finalE(open(M_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/M_out.xyz' % (self.obabel, M_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % M_out)
        elif M_out_software in ['NWChem']:
            Gaq_M = NWcheckResults.finalE(open(M_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/M_out.xyz' % (self.obabel, M_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % M_out)
        else:
            Gaq_M = 0.0


        # calculate the pKa
        logK = self.logK_formula(Gaq_L=Gaq_L, Gaq_ML=Gaq_ML, Gaq_M=Gaq_M)

        return logK, Gaq_L, Gaq_ML, Gaq_M

    def Calc_Gsolv(self, obj):
        # path for the output files
        aq_out = obj.UploadedOutputFile.file.name
        gas_out = obj.UploadedOutputFileP1.file.name
        workdir = os.path.dirname(aq_out)


        # The output is from Gaussian or NWChem
        aq_out_software = obj.QMSoftwareOutput
        gas_out_software = obj.QMSoftwareOutputP1

        # get the energies and convert to xyz
        if aq_out_software in ['Gaussian']:
            Gaq = g09checkResults.finalE(open(aq_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/aq_out.xyz' % (self.obabel, aq_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % aq_out)
        elif aq_out_software in ['NWChem']:
            Gaq = NWcheckResults.finalE(open(aq_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/aq_out.xyz' % (self.obabel, aq_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % aq_out)
        else:
            Gaq = 0.0

        if gas_out_software in ['Gaussian']:
            Ggas = g09checkResults.finalE(open(gas_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -ig09 %s -O %s/gas_out.xyz' % (self.obabel, gas_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % gas_out)
        elif gas_out_software in ['NWChem']:
            Ggas = NWcheckResults.finalE(open(gas_out).readlines())[8]
            try:
                # convert to xyz
                cmd = '%s -inwo %s -O %s/gas_out.xyz' % (self.obabel, gas_out, workdir)
                cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = cmd.communicate()
            except:
                logging.warning('\nWARN: Failed to convert %s to xyz!' % gas_out)
        else:
            Ggas = 0.0


        # calculate the pKa
        Gsolv = self.Gsolv_formula(Gaq=Gaq, Ggas=Ggas)

        return Gsolv, Gaq, Ggas
