# [*AQUA-MER* : Databases and Aqueous Speciation Server](https://aquamer.ornl.gov/)

*AQUA-MER* is the first online resource that realizes multiscale modeling of Hg speciation analysis in the environmental water systems with high-performance computing (HPC) clusters. It has four modules, a speciation calculator for mesoscale modeling, a computational chemistry toolkit for atomic-scale and quantum-scale modeling, a calculated stability constants database and an experimental measured stability constants database. These modules can be used independently. For example, computational chemistry toolkit is also useful in computer-aided drug design studies. With proper configurations, it can run time-consuming jobs, such as conformational search, pKa, and log K calculations, on large-scale HPC clusters in a parallel manner.

## Getting Started

The best way to use this web resource is go to https://aquamer.ornl.gov and submit your jobs there. In case you want to run your own server, here is the instructions to install and run.

### Prerequisites

```
Python == 2.7.12
Django == 1.10.2
Numpy >= 1.11.3
Scipy >= 1.0.1
Pandas >= 0.21.1
Scikit-learn >= 0.16.1
Matplotlib >= 1.5.1

Phreeqc >= 3.3.10
OpenBabel >= 2.4.1
Rdkit >= 2016.09.4
AmberTools >= 14
VMD >= 1.9.2
NAMD2 >= 2.12
MOPAC >= 2016
Gaussian >= 09 (optional)
NWChem >= 6.8.1 (optional)
```

### Installing

For python related codes, I suggest to use Anaconda to install them, but you can use the system default python and pip to install them as well. For meso-/atomic-/quantum- scale modeling related codes, please install and add them to your environmental path.

```
cd your_installation_directory
git clone https://github.com/penglian518/Aqua-mer.git
./manage.py runserver 127.0.0.1:8000
```

### Running

While the server is running, open http://127.0.0.1:8000 in your web browser to start to use.

## Authors

* **[Peng Lian](https://github.com/penglian518)** - *Initial work*

See also the list of [contributors](https://github.com/penglian518/Aqua-mer/graphs/contributors) who participated in this project.

## FAQ

https://aquamer.ornl.gov/faq/

## Citations

For the web site please cite:
* Peng Lian, Luanjing Guo, Deepa Devarajan, Jerry M. Parks, Scott L. Painter, Scott C. Brooks, and Jeremy C. Smith. The AQUA-MER Databases and Aqueous Speciation Server: A Web Resource for Multiscale Modeling of Mercury Speciation. (2019) Journal of Computational Chemistry. DOI: 10.1002/jcc.26081

For calculation of ΔGsolv, pKa, and log K, please cite:
* Peng Lian, Ryne C. Johnston, Jerry M. Parks, Jeremy C. Smith. Quantum Chemical Calculation of pKas of Environmentally Relevant Functional Groups: Carboxylic Acids, Amines and Thiols in Aqueous Solution. (2018) The Journal of Physical Chemistry A. 122 (17), pp 4366–4374. DOI: 10.1021/acs.jpca.8b01751
* Deepa Devarajan, Peng Lian, Scoot C. Brooks, Jerry M. Parks, Jeremy C. Smith. Quantum Chemical Approach for Calculating Stability Constants of Mercury Complexes. (2018) ACS Earth and Space Chemistry. DOI: 10.1021/acsearthspacechem.8b00102


## NOTICE

* The configuration file for Django (cyshg/setting.py) and the database files are not allowed to share. You have to re-generate your own and run the website at your own risk. Again, we suggest you to run your job at https://aquamer.ornl.gov.
* In order to setup a fully functioned server, Apache with WSGI (as a sample, a configuration file is provided in Apache_conf directory) and Torque (PBS) Job management system are required.
