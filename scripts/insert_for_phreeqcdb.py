#!/usr/bin/env python

import os

class PhreeqcDB:
    def __init__(self):
        self.Sections = ['SOLUTION_MASTER_SPECIES', 'SOLUTION_SPECIES', 'PHASES',
                         'SURFACE_MASTER_SPECIES', 'SURFACE_SPECIES',
                         'EXCHANGE_MASTER_SPECIES', 'EXCHANGE_SPECIES', 'RATES', 'END']

    # public functions
    def find_flag_idx(self, fcon, startstring, findall=True):
        '''return the index of the give string'''
        if findall:
            idx = []
        else:
            idx = 0

        conter = 0
        while conter < len(fcon):
            line = fcon[conter]
            if line.startswith(startstring):
                if findall:
                    idx.append(conter)
                    conter += 1
                else:
                    idx = conter
                    conter += len(fcon)
            else:
                conter += 1
        return idx

    def genSectionIdx(self, fcon):
        idx_dict = {}
        for i in self.Sections:
            idxs = self.find_flag_idx(fcon, i, findall=True)
            if len(idxs) > 0:
                for idx in idxs:
                    idx_dict[idx] = i
        return idx_dict

    def separateDatFile(self, filename, tmpDir='./phreeqcdb'):
        '''
        clean & separate the dat file to different piciese according to section

        :param filename:
        :return:
        '''

        # get file name & read the file
        fcon = open(filename).readlines()
        Fname = '%s/%s' % (tmpDir, os.path.basename(filename))

        # clean fcon, remove blank line or comment lines
        fcon = [i.replace('\t', ' ') for i in fcon if len(i.strip())>0 and not i.startswith('#')]

        # make a tmp dir according to file name
        try:
            os.makedirs(Fname)
        except:
            pass

        # locate idx for each sections
        section_idxs = self.genSectionIdx(fcon)

        if 'END' not in section_idxs.values():
            section_idxs[len(fcon)] = 'END'

        # sort updated_sections according to its index value!
        #updated_sections = [i for i in self.Sections if i in section_idxs.keys()]
        updated_sections = [(i, section_idxs[i]) for i in sorted(section_idxs.keys())]

        # write out sections
        for i in range(len(updated_sections)-1):
            idx_start = updated_sections[i][0]
            idx_end = updated_sections[i+1][0]
            fcon_i = fcon[idx_start:idx_end]
            # remove the section title
            fcon_j = [j for j in fcon_i if j.strip() not in section_idxs.values()]
            try:
                open('%s/%s.txt' % (Fname, updated_sections[i][1]), 'w').writelines(fcon_j)
            except:
                print('Failed to write %s' % updated_sections[i][1])
        return

    def getInLineComments(self, line):
        comm = ''
        line = line.replace('\t', ' ')
        idx = line.find('#')
        if idx >= 0:
            comm = line[idx:]
            line = line[:idx]
        return comm, line

    # section by section
    def getSolutionMaster(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx]
            if not line.startswith(' '):
                comm, line = self.getInLineComments(line)
                ele = line.split()[0]
                species = line.split()[1]
                alk = line.split()[2]
                gfw_formula = line.split()[3]
                try:
                    ele_gfw = line.split()[4]
                except:
                    ele_gfw = None

                d = {'ele': ele, 'species': species, 'alk': alk,
                     'gfw_formula': gfw_formula, 'ele_gfw': ele_gfw, 'note':comm}
                results.append(d)
        return results

    def getSpecies(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx]
            comm, line = self.getInLineComments(line)

            if not line.startswith(' '):
                reaction = line.strip()
                d = {'reaction': reaction}

                logk = 0.0
                deltah = 0.0
                deltaunit = 'kJ/mol'
                a1 = a2 = a3 = a4 = a5 = 0.0
                dw1 = dw2 = dw3 = dw4 = 0.0
                vm1 = vm2 = vm3 = vm4 = vm5 = vm6 = vm7 = vm8 = vm9 = vm10 = 0.0
                gammaA = 0.0
                gammaB = 0.0

                l = 1
                subline = fcon[idx + l]
                comm_sub = ''
                while subline.startswith(' '):
                    comm_sub_i, subline = self.getInLineComments(subline)
                    if comm_sub_i != '':
                        comm_sub += ' %s' % comm_sub_i
                    if subline.strip().startswith('-log'):
                        logk = subline.strip().split()[1]
                    if subline.strip().startswith('-delta'):
                        deltah = subline.strip().split()[1]
                        try:
                            deltaunit = subline.strip().split()[2]
                        except Exception as e:
                            print e
                            pass
                    if subline.strip().startswith('-ana'):
                        a1 = subline.strip().split()[1]
                        a2 = subline.strip().split()[2]
                        try:
                            a3 = subline.strip().split()[3]
                        except:
                            a3 = 0.0
                        try:
                            a4 = subline.strip().split()[4]
                        except:
                            a4 = 0.0
                        try:
                            a5 = subline.strip().split()[5]
                        except:
                            a5 = 0.0
                    if subline.strip().startswith('-dw'):
                        dw1 = subline.strip().split()[1]
                        try:
                            dw2 = subline.strip().split()[2]
                        except:
                            dw2 = 0.0
                        try:
                            dw3 = subline.strip().split()[3]
                        except:
                            dw3 = 0.0
                        try:
                            dw4 = subline.strip().split()[4]
                        except:
                            dw4 = 0.0
                    if subline.strip().startswith('-Vm'):
                        vm1 = subline.strip().split()[1]
                        try:
                            vm2 = subline.strip().split()[2]
                        except:
                            vm2 = 0.0
                        try:
                            vm3 = subline.strip().split()[3]
                        except:
                            vm3 = 0.0
                        try:
                            vm4 = subline.strip().split()[4]
                        except:
                            vm4 = 0.0
                        try:
                            vm5 = subline.strip().split()[5]
                        except:
                            vm5 = 0.0
                        try:
                            vm6 = subline.strip().split()[6]
                        except:
                            vm6 = 0.0
                        try:
                            vm7 = subline.strip().split()[7]
                        except:
                            vm7 = 0.0
                        try:
                            vm8 = subline.strip().split()[8]
                        except:
                            vm8 = 0.0
                        try:
                            vm9 = subline.strip().split()[9]
                        except:
                            vm9 = 0.0
                        try:
                            vm10 = subline.strip().split()[10]
                        except:
                            vm10 = 0.0

                    if subline.strip().startswith('-gamma'):
                        gammaA = subline.strip().split()[1]
                        gammaB = subline.strip().split()[2]

                    l += 1
                    try:
                        subline = fcon[idx + l]
                    except:
                        break

                d['logk'] = logk
                d['deltah'] = deltah
                d['deltaunit'] = deltaunit
                d['a1'] = a1
                d['a2'] = a2
                d['a3'] = a3
                d['a4'] = a4
                d['a5'] = a5
                d['dw1'] = dw1
                d['dw2'] = dw2
                d['dw3'] = dw3
                d['dw4'] = dw4
                d['vm1'] = vm1
                d['vm2'] = vm2
                d['vm3'] = vm3
                d['vm4'] = vm4
                d['vm5'] = vm5
                d['vm6'] = vm6
                d['vm7'] = vm7
                d['vm8'] = vm8
                d['vm9'] = vm9
                d['vm10'] = vm10
                d['gammaA'] = gammaA
                d['gammaB'] = gammaB

                if comm_sub != '':
                    comm += ' %s' % comm_sub
                d['note'] = comm.strip()

                results.append(d)

        return results

    def getPhases(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx]
            comm, line = self.getInLineComments(line)

            if not line.startswith(' '):
                name = line.split()[0]
                reaction = fcon[idx + 1].strip()
                comm_reaction, reaction = self.getInLineComments(reaction)

                d = {'name': name, 'reaction': reaction.strip()}
                logk = 0.0
                deltah = 0.0
                deltaunit = 'kJ/mol'
                a1 = a2 = a3 = a4 = a5 = 0.0
                vm1 = vm2 = vm3 = vm4 = vm5 = vm6 = vm7 = vm8 = vm9 = vm10 = 0.0
                Tc = 0.0
                Pc = 0.0
                Omega = 0.0

                l = 1
                subline = fcon[idx + l]
                comm_sub = ''
                while subline.startswith(' '):
                    comm_sub_i, subline = self.getInLineComments(subline)
                    if comm_sub_i != '':
                        comm_sub += ' %s' % comm_sub_i
                    if subline.strip().startswith('-log'):
                        logk = subline.strip().split()[1]
                    if subline.strip().startswith('-T_c'):
                        Tc = subline.strip().split()[1].strip(';')
                        if subline.find(';') > 0:
                            try:
                                Pc = subline.split(';')[1].split()[1].strip()
                            except:
                                pass
                            try:
                                Omega = subline.split(';')[2].split()[1].strip()
                            except:
                                pass
                    if subline.strip().startswith('-P_c'):
                        Pc = subline.strip().split()[1]
                    if subline.strip().startswith('-Omega'):
                        Omega = subline.strip().split()[1]
                    if subline.strip().startswith('-delta'):
                        deltah = subline.strip().split()[1]
                        try:
                            deltaunit = subline.strip().split()[2]
                        except:
                            pass
                    if subline.strip().startswith('-ana'):
                        a1 = subline.strip().split()[1]
                        a2 = subline.strip().split()[2]
                        a3 = subline.strip().split()[3]
                        try:
                            a4 = subline.strip().split()[4]
                        except:
                            a4 = 0.0

                        try:
                            a5 = subline.strip().split()[5]
                        except:
                            a5 = 0.0
                    if subline.strip().startswith('-Vm'):
                        vm1 = float(subline.strip().split()[1])
                        try:
                            vm2 = float(subline.strip().split()[2])
                        except:
                            vm2 = 0.0
                        try:
                            vm3 = float(subline.strip().split()[3])
                        except:
                            vm3 = 0.0
                        try:
                            vm4 = float(subline.strip().split()[4])
                        except:
                            vm4 = 0.0
                        try:
                            vm5 = float(subline.strip().split()[5])
                        except:
                            vm5 = 0.0
                        try:
                            vm6 = float(subline.strip().split()[6])
                        except:
                            vm6 = 0.0
                        try:
                            vm7 = float(subline.strip().split()[7])
                        except:
                            vm7 = 0.0
                        try:
                            vm8 = float(subline.strip().split()[8])
                        except:
                            vm8 = 0.0
                        try:
                            vm9 = float(subline.strip().split()[9])
                        except:
                            vm9 = 0.0
                        try:
                            vm10 = float(subline.strip().split()[10])
                        except:
                            vm10 = 0.0

                    l += 1
                    try:
                        subline = fcon[idx + l]
                    except:
                        break

                d['logk'] = logk
                d['deltah'] = deltah
                d['deltaunit'] = deltaunit
                d['a1'] = a1
                d['a2'] = a2
                d['a3'] = a3
                d['a4'] = a4
                d['a5'] = a5

                d['Tc'] = Tc
                d['Pc'] = Pc
                d['Omega'] = Omega
                d['vm1'] = vm1
                d['vm2'] = vm2
                d['vm3'] = vm3
                d['vm4'] = vm4
                d['vm5'] = vm5
                d['vm6'] = vm6
                d['vm7'] = vm7
                d['vm8'] = vm8
                d['vm9'] = vm9
                d['vm10'] = vm10

                if comm_sub != '':
                    comm += ' %s' % comm_sub
                d['note'] = comm.strip().decode('unicode_escape').encode('ascii','ignore')

                results.append(d)

        return results

    def getSurfaceMaster(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx].strip()
            if not line.startswith(' '):
                comm, line = self.getInLineComments(line)
                site = line.split()[0]
                master = line.split()[1]

                d = {'site': site, 'master': master, 'note': comm}
                results.append(d)
        return results

    def getSurfaceSpecies(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx].strip()
            comm, line = self.getInLineComments(line)

            if not line.startswith('-'):
                reaction = fcon[idx]

                d = {'reaction': reaction}
                logk = 0.0

                l = 1
                subline = fcon[idx + l].strip()
                comm_sub = ''
                while subline.startswith('-'):
                    comm_sub_i, subline = self.getInLineComments(subline)
                    if comm_sub_i != '':
                        comm_sub += ' %s' % comm_sub_i
                    if subline.strip().startswith('-log'):
                        logk = subline.strip().split()[1]

                    l += 1
                    try:
                        subline = fcon[idx + l]
                    except:
                        break

                d['logk'] = logk

                if comm_sub != '':
                    comm += ' %s' % comm_sub
                d['note'] = comm.strip()

                results.append(d)

        return results

    def getExchangeSpecies(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx]
            comm, line = self.getInLineComments(line)

            line = line.strip()
            #if not line.startswith(' '):
            if line.find('=')>0:
                reaction = line.strip()
                d = {'reaction': reaction}

                logk = 0.0
                deltah = 0.0
                deltaunit = 'kJ/mol'
                gammaA = 0.0
                gammaB = 0.0

                l = 1
                subline = fcon[idx + l].strip()
                comm_sub = ''
                while subline.startswith('-'):
                    comm_sub_i, subline = self.getInLineComments(subline)
                    if comm_sub_i != '':
                        comm_sub += ' %s' % comm_sub_i
                    if subline.strip().startswith('-log'):
                        logk = subline.strip().split()[1]
                    if subline.strip().startswith('-delta'):
                        deltah = subline.strip().split()[1]
                        try:
                            deltaunit = subline.strip().split()[2]
                        except Exception as e:
                            print e
                            pass
                    if subline.strip().startswith('-gamma'):
                        gammaA = subline.strip().split()[1]
                        gammaB = subline.strip().split()[2]

                    l += 1
                    try:
                        subline = fcon[idx + l]
                    except:
                        break

                d['logk'] = logk
                d['deltah'] = deltah
                d['deltaunit'] = deltaunit
                d['gammaA'] = gammaA
                d['gammaB'] = gammaB

                if comm_sub != '':
                    comm += ' %s' % comm_sub
                d['note'] = comm.strip()

                results.append(d)

        return results

    def getRates(self, filename):
        fcon = open(filename).readlines()
        fcon = [f.strip('\n') for f in fcon]
        results = []
        for idx in range(len(fcon)):
            line = fcon[idx]
            comm, line = self.getInLineComments(line)

            line = line.strip()
            if not line.startswith('-') and not line[0].isdigit():
            #if line.find('=')>0:
                name = line.strip()
                d = {'name': name}

                l = 1
                subline = fcon[idx + l].strip()

                basicStatement = ''
                while subline.startswith('-') or subline[0].isdigit():

                    basicStatement += '%s\n' % subline

                    l += 1
                    try:
                        subline = fcon[idx + l].strip()
                    except:
                        break

                d['note'] = comm.strip()
                d['BasicStatement'] = basicStatement

                results.append(d)

        return results


    # insert
    def inputSolutionMaster(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(Element=d['ele']))[0]
            except Exception as e:
                #print e
                inst = model.objects.create()
                print d
            inst.Element = d['ele']
            inst.Species = d['species']
            inst.Alkalinity = d['alk']
            inst.GFWorFormula = d['gfw_formula']
            inst.GFWforElement = d['ele_gfw']
            inst.Note = d['note']

            if RefID == 'Auto':
                # input data from SCB
                RefID = 'SCB'

            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputSpecies(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(Reaction=d['reaction']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d

            inst.Reaction = d['reaction']
            inst.LogK = d['logk']
            inst.DeltaH = d['deltah']
            inst.DeltaHUnits = d['deltaunit']
            inst.AEA1 = d['a1']
            inst.AEA2 = d['a2']
            inst.AEA3 = d['a3']
            inst.AEA4 = d['a4']
            inst.AEA5 = d['a5']
            inst.DW1 = d['dw1']
            inst.DW2 = d['dw2']
            inst.DW3 = d['dw3']
            inst.DW4 = d['dw4']
            inst.VM1 = d['vm1']
            inst.VM2 = d['vm2']
            inst.VM3 = d['vm3']
            inst.VM4 = d['vm4']
            inst.VM5 = d['vm5']
            inst.VM6 = d['vm6']
            inst.VM7 = d['vm7']
            inst.VM8 = d['vm8']
            inst.VM9 = d['vm9']
            inst.VM10 = d['vm10']
            inst.GammaA = d['gammaA']
            inst.GammaB = d['gammaB']
            inst.Note = d['note']

            # find RefID from comments
            if RefID == 'Auto':
                currentRefIDs = [i.RefID for i in Refs.objects.all()]

                try:
                    s = d['note'].split('[')[1].split(']')[0]
                except Exception as e:
                    s = ''
                    # input data from SCB
                    pass

                if s in currentRefIDs:
                    RefID_new = s
                else:
                    RefID_new = 'SCB'
            else:
                RefID_new = RefID

            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID_new).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID_new))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputPhases(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(PhaseName=d['name']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.PhaseName = d['name']
            inst.Reaction = d['reaction']
            inst.LogK = d['logk']
            inst.DeltaH = d['deltah']
            inst.DeltaHUnits = d['deltaunit']
            inst.AEA1 = d['a1']
            inst.AEA2 = d['a2']
            inst.AEA3 = d['a3']
            inst.AEA4 = d['a4']
            inst.AEA5 = d['a5']
            inst.TC = d['Tc']
            inst.PC = d['Pc']
            inst.OMEGA = d['Omega']
            inst.VM1 = d['vm1']
            inst.VM2 = d['vm2']
            inst.VM3 = d['vm3']
            inst.VM4 = d['vm4']
            inst.VM5 = d['vm5']
            inst.VM6 = d['vm6']
            inst.VM7 = d['vm7']
            inst.VM8 = d['vm8']
            inst.VM9 = d['vm9']
            inst.VM10 = d['vm10']
            inst.Note = d['note']

            # find RefID from comments
            if RefID == 'Auto':
                currentRefIDs = [i.RefID for i in Refs.objects.all()]

                try:
                    s = d['note'].split('[')[1].split(']')[0]
                except Exception as e:
                    s = ''
                    # input data from SCB
                    pass

                if s in currentRefIDs:
                    RefID_new = s
                else:
                    RefID_new = 'SCB'
            else:
                RefID_new = RefID

            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID_new).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID_new))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputSurfaceMaster(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(BindingSite=d['site']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.BindingSite = d['site']
            inst.SurfaceMaster = d['master']
            inst.Note = d['note']
            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputSurfaceSpecies(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(Reaction=d['reaction']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.Reaction = d['reaction']
            inst.LogK = d['logk']
            inst.Note = d['note']
            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputExchangeMaster(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(ExchangeName=d['site']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.ExchangeName = d['site']
            inst.ExchangeMaster = d['master']
            inst.Note = d['note']
            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputExchangeSpecies(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(Reaction=d['reaction']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.Reaction = d['reaction']
            inst.LogK = d['logk']
            inst.DeltaH = d['deltah']
            inst.DeltaHUnits = d['deltaunit']
            inst.GammaA = d['gammaA']
            inst.GammaB = d['gammaB']
            inst.Note = d['note']
            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()

    def inputRates(self, model, reseults, DBID, RefID):
        for d in reseults:
            try:
                inst = model.objects.filter(Q(DBSource__DBID=DBID) & Q(Name=d['name']))[0]
            except Exception as e:
                inst = model.objects.create()
                print d
            inst.Name = d['name']
            inst.BasicStatement = d['BasicStatement']
            inst.Note = d['note']
            try:
                inst.Ref_id = Refs.objects.get(RefID=RefID).pk
            except:
                print ('Cannot find RefID=%s in Refs' % str(RefID))
            try:
                inst.DBSource_id = DBSources.objects.get(DBID=DBID).pk
            except:
                print('Cannot find DBID=%s in DBSources' % str(DBID))
            inst.save()


if __name__ == '__main__':
    # where to save the intermediate files
    if os.uname()[1] == 'aquamer':
        tmpDir = '%s/workplace/website/cyshg/scripts/phreeqcdb' % os.environ.get('HOME')

        import os, django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cyshg.settings")
        django.setup()

        from phreeqcdb.models import *
        from django.db.models import Q

    elif os.uname()[1] == 'cameo':
        tmpDir = '%s/aquamer/workplace/website/cyshg/scripts/phreeqcdb' % os.environ.get('HOME')

    # which db to use
    #db = 'minteq.v4.dat.dat'
    db = 'Additions_SCB.dat'
    #db = 'phreeqc.dat'

    if db in ['phreeqc.dat']:
        DBID = 'Phreeqc_default'
        RefID = 'Phreeqc'
    elif db in ['Additions_SCB.dat']:
        DBID = 'Aquamer_default'
        RefID = 'Auto'

    # full path to the input db
    dat = '%s/database/%s' % (tmpDir, db)

    # create an instance
    phDB = PhreeqcDB()
    # separate .dat file into sections
    phDB.separateDatFile(dat, tmpDir=tmpDir)

    #### for default phreeqc.dat ####
    #l = phDB.getSolutionMaster('%s/%s/SOLUTION_MASTER_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSolutionMaster(SolutionMasterSpecies, l, DBID=DBID, RefID=RefID)

    #l = phDB.getSpecies('%s/%s/SOLUTION_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSpecies(SolutionSpecies, l, DBID=DBID, RefID=RefID)

    #l = phDB.getPhases('%s/%s/PHASES.txt' % (tmpDir, db))
    #phDB.inputPhases(Phases, l, DBID=DBID, RefID=RefID)

    #l = phDB.getSurfaceMaster('%s/%s/SURFACE_MASTER_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSurfaceMaster(SurfaceMasterSpecies, l, DBID, RefID)

    #l = phDB.getSurfaceSpecies('%s/%s/SURFACE_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSurfaceSpecies(SurfaceSpecies, l, DBID, RefID)

    #l = phDB.getSurfaceMaster('%s/%s/EXCHANGE_MASTER_SPECIES.txt' % (tmpDir, db))
    #phDB.inputExchangeMaster(ExchangeMasterSpecies, l, DBID, RefID)

    #l = phDB.getExchangeSpecies('%s/%s/EXCHANGE_SPECIES.txt' % (tmpDir, db))
    #phDB.inputExchangeSpecies(ExchangeSpecies, l, DBID, RefID)

    #l = phDB.getRates('%s/%s/RATES.txt' % (tmpDir, db))
    #phDB.inputRates(Rates, l, DBID, RefID)

    ### for Additions_SCB.dat ####
    #l = phDB.getSolutionMaster('%s/%s/SOLUTION_MASTER_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSolutionMaster(SolutionMasterSpecies, l, DBID=DBID, RefID=RefID)

    #l = phDB.getSpecies('%s/%s/SOLUTION_SPECIES.txt' % (tmpDir, db))
    #phDB.inputSpecies(SolutionSpecies, l, DBID=DBID, RefID=RefID)

    l = phDB.getPhases('%s/%s/PHASES.txt' % (tmpDir, db))
    phDB.inputPhases(Phases, l, DBID=DBID, RefID=RefID)


    #for i in range(len(l)):
    #    print(l[i])


