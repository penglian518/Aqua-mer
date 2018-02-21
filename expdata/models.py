from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible  # only if you need to support Python 2
class Compound(models.Model):
    PubChemID = models.PositiveIntegerField(blank=True, default=0)
    Name = models.CharField(max_length=200, blank=True, default='')
    Formula = models.CharField(max_length=30, blank=True, default='')
    InChIKey = models.CharField(max_length=50, blank=True, default='')
    SMILES = models.CharField(max_length=100, blank=True, default='')
    IUPACName = models.CharField(max_length=200, blank=True, default='')
    Charge = models.SmallIntegerField(default=0)
    MolecularWeight = models.CharField(max_length=10, blank=True, default='')
    CASRegNumber = models.CharField(max_length=30, blank=True, default='')
    Source = models.CharField(max_length=100, blank=True, default='')
    Note = models.CharField(max_length=200, blank=True, default='')

    #PKa = models.ForeignKey('PKA', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


@python_2_unicode_compatible  # only if you need to support Python 2
class dGsolv(models.Model):
    MolID = models.ForeignKey('Compound', on_delete=models.CASCADE, default=0)
    dGsolv = models.CharField(max_length=20, blank=True, default='')
    dGsolvReference = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        s = str(self.MolID) + '_' + str(self.dGsolv)
        return s


@python_2_unicode_compatible  # only if you need to support Python 2
class PKA(models.Model):
    MCHOICE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )
    ELECTROLYTECHOICE = (
        ('-', '-'),
        ('NaCl', 'NaCl'),
        ('NaClO4', 'NaClO4'),
        ('NaNO3', 'NaNO3'),
        ('NH4Cl', 'NH4Cl'),
        ('KCl', 'KCl'),
        ('KNO3', 'KNO3'),
        ('HNa, Cl', 'HNa, Cl'),
    )


    MolID = models.ForeignKey('Compound', on_delete=models.CASCADE, default=0)
    H = models.PositiveSmallIntegerField(choices=MCHOICE, default=1)
    L = models.PositiveSmallIntegerField(choices=MCHOICE, default=1)
    IonicStrength = models.CharField(max_length=10, blank=True, default='')
    #Electrolyte = models.CharField(max_length=30, choices=ELECTROLYTECHOICE, default='-')
    Electrolyte = models.ForeignKey('Electrolyte', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    TemperatureC = models.CharField(max_length=10, blank=True, default='')
    pKa = models.CharField(max_length=10, blank=True, default='')
    pKaReference = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    dHr = models.CharField(max_length=20, blank=True, default='')
    dSr = models.CharField(max_length=20, blank=True, default='')
    dGr = models.CharField(max_length=20, blank=True, default='')
    ThermalReference = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')

    @property
    def Species(self):
        rawlist = [('H', self.H), ('L', self.L)]
        combined = []
        for i in rawlist:
            if i[1] == 1:
                combined.append(i[0])
            elif i[1] > 1:
                combined.append(i[0]+str(i[1]))

        return ''.join(combined)


    def __str__(self):
        s = str(self.MolID) + '_' + str(self.Species) + '_' + str(self.pKa)
        return s


@python_2_unicode_compatible  # only if you need to support Python 2
class StabilityConstants(models.Model):
    METALCHOICE = (
        ('Hg1+', 'Hg1+'),
        ('Hg2+', 'Hg2+'),
        ('Co1+', 'Co1+'),
        ('Co2+', 'Co2+'),
    )
    CONSTANTCHOICE = (
        ('B', 'B'),
        ('K', 'K'),
    )
    MCHOICE = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )
    LPRIMECHOISE = (
        ('', ''),
        ('Cl-', 'Cl-'),
        ('Br-', 'Br-'),
    )
    ELECTROLYTECHOICE = (
        ('-', '-'),
        ('NaCl', 'NaCl'),
        ('NaClO4', 'NaClO4'),
        ('NaNO3', 'NaNO3'),
        ('NH4Cl', 'NH4Cl'),
        ('KCl', 'KCl'),
        ('KNO3', 'KNO3'),
        ('HNa, Cl', 'HNa, Cl'),
    )


    MolID = models.ForeignKey('Compound', on_delete=models.CASCADE, default=0)
    Metal = models.CharField(max_length=30, choices=METALCHOICE, default='Hg2+')
    Constant = models.CharField(max_length=10, choices=CONSTANTCHOICE, default='B')
    M = models.PositiveSmallIntegerField(choices=MCHOICE, default=1)
    L = models.PositiveSmallIntegerField(choices=MCHOICE, default=1)
    H = models.PositiveSmallIntegerField(choices=MCHOICE, default=0)
    OH = models.PositiveSmallIntegerField(choices=MCHOICE, default=0)
    Lprime = models.CharField(max_length=10, choices=LPRIMECHOISE, blank=True, default='')
    LprimeNumber = models.PositiveSmallIntegerField(choices=MCHOICE, default=0)
    #Reactants = models.CharField(max_length=50, blank=True, default='')
    Reactants = models.ForeignKey('Reactants', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    IonicStrength = models.CharField(max_length=10, blank=True, default='')
    #Electrolyte = models.CharField(max_length=30, choices=ELECTROLYTECHOICE, default='-')
    Electrolyte = models.ForeignKey('Electrolyte', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    TemperatureC = models.CharField(max_length=10, blank=True, default='')
    LogBorK = models.CharField(max_length=10, blank=True, default='')
    dHr = models.CharField(max_length=20, blank=True, default='')
    dSr = models.CharField(max_length=20, blank=True, default='')
    dGr = models.CharField(max_length=20, blank=True, default='')
    ThermalReference = models.ForeignKey('Refs', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')


    @property
    def Species(self):
        rawlist = [('M', self.M), ('L', self.L), ('H', self.H), ('(OH)', self.OH), (self.Lprime, self.LprimeNumber)]
        combined = []
        for i in rawlist:
            if i[1] == 1:
                combined.append(i[0])
            elif i[1] > 1:
                combined.append(i[0]+str(i[1]))

        return ''.join(combined)

    def __str__(self):
        s = str(self.MolID) + '_' + str(self.Constant) + '_' + str(self.LogBorK)
        return s


@python_2_unicode_compatible  # only if you need to support Python 2
class Refs(models.Model):
    RefID = models.CharField(max_length=20, blank=True, null=True, unique=True)
    Reference = models.CharField(max_length=500, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.RefID)


@python_2_unicode_compatible  # only if you need to support Python 2
class Electrolyte(models.Model):
    Electrolyte = models.CharField(max_length=20, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.Electrolyte)


@python_2_unicode_compatible  # only if you need to support Python 2
class Reactants(models.Model):
    Reactants = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return str(self.Reactants)