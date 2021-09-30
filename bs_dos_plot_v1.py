#!/usr/bin/env python3

from matplotlib.pyplot import *
from numpy import *

def get_bs_points(filename):
    'Takes a band structure .BAND output file and returns the points to be plotted.'
    with open(filename, 'r') as stream1:
        allbandslist = []
        for line in stream1:
            if line[0] not in ['@', '#']:
                verticalpoints = line.split()
                allbandslist = allbandslist + [verticalpoints]
        allbandslist = list(map(list, zip(*allbandslist)))
        
        for n in range(0, len(allbandslist)):
            allbandslist[n] = list(map(float, (allbandslist[n])))
        
    return allbandslist 

def get_bs_labels(filename):
    'Retrieves relevant labels from band structure file.'
    
    with open(filename, 'r') as stream1:
        labelslist = []
        xlabelslist = []
        xlabelsvals = []
        
        for line in stream1:
            
            if 'XAXIS TICKLABEL    ' in line:
                xlabel = line.split()[-1]
                xlabelslist = xlabelslist + [xlabel]
            
            elif 'XAXIS TICK     ' in line:
                xlabelval = line.split()[-1]
                xlabelsvals = xlabelsvals + [float(xlabelval)]
            
            elif 'YAXIS LABEL ' in line:
                ylabel = line.split('"')[-2]
            
            elif 'TITLE ' in line:
                title = line.split('"')[-2]

            xlabel = 'k-points'
                
        labelslist = [xlabelslist, xlabelsvals, xlabel, ylabel, title]
        
        for i in range(0, len(labelslist[0])):
            xlabelgood = labelslist[0][i].split('"')[1]
            labelslist[0][i] = xlabelgood
    return labelslist 


def get_dos_points(filename):
    'Gets points to be plotted from .DOSS file.'
    
    with open(filename, 'r') as stream:
        dospointslist = []
        
        for line in stream:
            if line[0] not in ['@', '#']:
                verticalpoints = line.split()
                dospointslist = dospointslist + [verticalpoints]
        
        dospointslist = list(map(list, zip(*dospointslist)))

        for n in range(0, len(dospointslist)):
            dospointslist[n] = list(map(float, (dospointslist[n])))
        
    return dospointslist


def get_dos_labels(filename):
    'Retrieves relevant labels from band structure file.'
    
    with open(filename, 'r') as stream:
        labelslist = []
        
        for line in stream:
            
            if 'XAXIS LABEL ' in line:
                xlabel = line.split('"')[-2]
            
            elif 'YAXIS LABEL ' in line:
                ylabel = line.split('"')[-2]
                ylabel = ylabel.replace('DENSITY OF STATES', 'DoS')
            
            title = 'Density of States'
                
        labelslist = [xlabel, ylabel, title]

    return labelslist 


def getfermienergy(filename, eV, prnt):
    'Extracts Fermi energy from a band structure or density of states file'
    
    with open(filename, 'r') as stream:
        
        for line in stream:
            if '# EFERMI' in line:
                efermi = float(line.split()[-1])
                
        if eV is True:
            unit = 'eV'
            efermi = efermi * 27.211386245988
            
        else:
            unit = 'Hartrees'
        
        if prnt is True:
            print('Fermi Energy:', efermi, unit)
        
    return efermi


def plot_bs_dos(filenamebs, filenamedos, filename, bstitlestring, dostitlestring, *argv, eV, fermienergy):#, labels):
    'Plots DoS and given bands from BS side by side. Can plot one, all or a specified range of bands.'
    
    if len(argv) > 2:
        print('Error: too many arguments.')
    
    else:
        
        # Getting the band structure and DoS data
        
        bspoints = get_bs_points(filenamebs)
        dospoints = get_dos_points(filenamedos)
        bslabels = get_bs_labels(filenamebs)
        doslabels = get_dos_labels(filenamedos)
        
        # Dealing with FermiEnergy input
        
        if fermienergy is True:
            FermiEnergy = getfermienergy(filenamebs, eV = False, prnt = False)
            
            bslabels[3] = bslabels[3].replace('E-EFERMI', 'ENERGY')
            doslabels[0] = doslabels[0].replace('E-EFERMI', 'ENERGY')
            
            for band in range(1, len(bspoints)):
                for bsvalue in range(0, len(bspoints[band])):
                    bspoints[band][bsvalue] = bspoints[band][bsvalue] + FermiEnergy
                    
            for dos in range(0, 1):
                for dosvalue in range(0, len(dospoints[dos])):
                    dospoints[dos][dosvalue] = dospoints[dos][dosvalue] + FermiEnergy
            
        else:
            FermiEnergy = 0
        
        # Dealing with eV input - changing units and labels
        
        if eV is True:
            
            FermiEnergy = FermiEnergy * 27.211386245988
            
            for band in range(1, len(bspoints)):
                for bsvalue in range(0, len(bspoints[band])):
                    bspoints[band][bsvalue] = bspoints[band][bsvalue] * 27.211386245988
            for dos in range(0, 1):
                for dosvalue in range(0, len(dospoints[dos])):
                    dospoints[dos][dosvalue] = dospoints[dos][dosvalue] * 27.211386245988
            
            bslabels[3] = bslabels[3].replace('HARTREE', 'eV')
            doslabels[0] = doslabels[0].replace('HARTREE', 'eV')
            doslabels[1] = doslabels[1].replace('HARTREE', 'eV')
    
        # Dealing with Band selection inputs (0, 1 or 2)
        
        if len(argv) is 2:
            first_band = argv[0]
            last_band = argv[1]
    
        elif len(argv) is 0:
            first_band = 1
            last_band = len(bspoints) - 1
            
        elif len(argv) is 1:
            first_band = argv[0]
            last_band = argv[0]
    
        # Dealing with bad inputs
    
        if (last_band + 1) > len(bspoints):
            print('Error: the file does not contain that many bands.')
        
        elif first_band < 1:
            print('Error: start band plotting from 1.')
        
        else:
            
            # Setting up the subplot
    
            fig, axes = subplots(nrows = 1, ncols = 2, figsize=(8, 5), sharey=True)
        
            subplots_adjust(wspace=0)
    
    
            # Plotting the Band Structure
        
            bsxaxis = bspoints[0]
            
            bszeropoints = linspace(FermiEnergy, FermiEnergy, len(bsxaxis))
            axes[0].plot(bsxaxis, bszeropoints, color ='red')
        
            for a in range(first_band, last_band+1):
                axes[0].plot(bsxaxis, bspoints[a], color='black')
    
            for b in range(0, len(bslabels[1])):
                axes[0].axvline(x = bslabels[1][b], label=bslabels[0][b])
    
            bsxlimit = amax(bspoints[0])
            axes[0].set_xlim(-0.01, bsxlimit+0.01)
    
            axes[0].set_xlabel(bslabels[2])
            axes[0].set_ylabel(bslabels[3])
            axes[0].set_title(bslabels[4])
            
            axes[0].set_xticks(bslabels[1])
            
            axes[0].spines['right'].set_visible(False)
            axes[0].spines['left'].set_visible(False)
            
            #Generating correct labels
            if ['(0,0,0)/6', '(3,0,0)/6', '(3,3,0)/6', '(2,2,0)/6', '(0,0,0)/6'] == bslabels[0]:
                bslabels[0] = ['$\Gamma$', 'X', 'M', 'K', '$\Gamma$']
                axes[0].set_xticklabels(bslabels[0])
            
            else:
                axes[0].set_xticklabels(bslabels[0])
                setp(axes[0].get_xticklabels(), rotation=30, horizontalalignment='right')
    
            if len(bstitlestring) > 0:
                axes[0].set_title(bstitlestring)
            else:
                axes[0].set_title('Band Structure')

    
            # Plotting the Density of States
    
    
            dosxaxis = dospoints[0]
            doszeropoints = linspace(0, 0, len(dosxaxis))
    
            maxdosval = amax(dospoints[len(dospoints)-1])
    
            axes[1].plot([0, maxdosval], [FermiEnergy, FermiEnergy], color ='red')
    
            for c in range(1, len(dospoints)):
                axes[1].plot(dospoints[c], dosxaxis)#, color='black')
    
            dosxlimit = amax(dospoints[-1])
            axes[1].set_xlim(0, ceil(dosxlimit))
    
            axes[1].set_xlabel(doslabels[1])
            
            if len(dostitlestring) > 0:
                axes[1].set_title(dostitlestring)
            else:
                axes[1].set_title(doslabels[2])
            
            axes[1].tick_params(left = False)
    
            ###
    
            fig.tight_layout()
    
            savefig(filename+'.png')
            show()
            
def plot_bs(filenamebs, filename, titlestring, *argv, eV, fermienergy):
    'Takes a band structure file .BAND and plots the BS with matplotlib.'
    
    if len(argv) > 2:
        print('Error: too many arguments.')
    
    else:
        
        # Getting the band structure data
        
        bspoints = get_bs_points(filenamebs)
        bslabels = get_bs_labels(filenamebs)
        
        # Dealing with FermiEnergy input
        
        if fermienergy is True:
            FermiEnergy = getfermienergy(filenamebs, eV = False, prnt = False)
            
            bslabels[3] = bslabels[3].replace('E-EFERMI', 'ENERGY')
            
            for band in range(1, len(bspoints)):
                for bsvalue in range(0, len(bspoints[band])):
                    bspoints[band][bsvalue] = bspoints[band][bsvalue] + FermiEnergy
            
        else:
            FermiEnergy = 0
        
        # Dealing with eV input - changing units and labels
        
        if eV is True:
            
            FermiEnergy = FermiEnergy * 27.211386245988
            
            for band in range(1, len(bspoints)):
                for bsvalue in range(0, len(bspoints[band])):
                    bspoints[band][bsvalue] = bspoints[band][bsvalue] * 27.211386245988
            
            bslabels[3] = bslabels[3].replace('HARTREE', 'eV')
    
        # Dealing with Band selection inputs (0, 1 or 2)
        
        if len(argv) is 2:
            first_band = argv[0]
            last_band = argv[1]
    
        elif len(argv) is 0:
            first_band = 1
            last_band = len(bspoints) - 1
            
        elif len(argv) is 1:
            first_band = argv[0]
            last_band = argv[0]
    
        # Dealing with bad inputs
    
        if (last_band + 1) > len(bspoints):
            print('Error: the file does not contain that many bands.')
        
        elif first_band < 1:
            print('Error: start band plotting from 1.')
        
        else:
    
            # Plotting the Band Structure
        
            figure(figsize=(4, 5))
        
            bsxaxis = bspoints[0]
            
            bszeropoints = linspace(FermiEnergy, FermiEnergy, len(bsxaxis))
            plot(bsxaxis, bszeropoints, color ='red')
        
            for a in range(first_band, last_band+1):
                plot(bsxaxis, bspoints[a], color='black')
    
            for b in range(0, len(bslabels[1])):
                axvline(x = bslabels[1][b], label=bslabels[0][b])
    
            bsxlimit = amax(bspoints[0])
            xlim(-0.01, bsxlimit+0.01)
    
            xlabel(bslabels[2])
            ylabel(bslabels[3])
            title(bslabels[4])
            
            #spines['right'].set_visible(False)
            #spines['left'].set_visible(False)
            
            #Generating correct labels
            if ['(0,0,0)/6', '(3,0,0)/6', '(3,3,0)/6', '(2,2,0)/6', '(0,0,0)/6'] == bslabels[0]:
                bslabels[0] = ['$\Gamma$', 'X', 'M', 'K', '$\Gamma$']
                xticks(bslabels[1], bslabels[0])
            
            else:
                xticks(bslabels[1], bslabels[0], rotation=30, horizontalalignment='right')
    
            if len(titlestring) > 0:
                title(titlestring)
            else:
                title('Band Structure')

            ###
            
            tight_layout()
            
            savefig(filename+'.png')
            show()


def plot_dos(filenamedos, filename, titlestring, eV, fermienergy):
    'Plots DoS from a given .DOSS file'
        
    # Getting the band structure and DoS data
        
    dospoints = get_dos_points(filenamedos)
    doslabels = get_dos_labels(filenamedos)
        
    # Dealing with FermiEnergy input
        
    if fermienergy is True:
        FermiEnergy = getfermienergy(filenamedos, eV = False, prnt = False)
        
        doslabels[0] = doslabels[0].replace('E-EFERMI', 'ENERGY')
                    
        for dos in range(0, 1):
            for dosvalue in range(0, len(dospoints[dos])):
                dospoints[dos][dosvalue] = dospoints[dos][dosvalue] + FermiEnergy
            
    else:
        FermiEnergy = 0
        
    # Dealing with eV input - changing units and labels
        
    if eV is True:
            
        FermiEnergy = FermiEnergy * 27.211386245988
        
        for dos in range(0, 1):
            for dosvalue in range(0, len(dospoints[dos])):
                dospoints[dos][dosvalue] = dospoints[dos][dosvalue] * 27.211386245988
            
        doslabels[0] = doslabels[0].replace('HARTREE', 'eV')
        doslabels[1] = doslabels[1].replace('HARTREE', 'eV')
    
    # Plotting the Density of States
    
    figure(figsize=(4, 5))
    
    dosxaxis = dospoints[0]
    doszeropoints = linspace(0, 0, len(dosxaxis))
    
    maxdosval = amax(dospoints[len(dospoints)-1])
    
    plot([0, maxdosval], [FermiEnergy, FermiEnergy], color ='red')
    
    for c in range(1, len(dospoints)):
        plot(dospoints[c], dosxaxis)#, color='black')
    
    dosxlimit = amax(dospoints[-1])
    xlim(0, ceil(dosxlimit))
    
    xlabel(doslabels[1])
    ylabel(doslabels[0])
    
    if len(titlestring) > 0:
        title(titlestring)
    else:
        title(doslabels[2])
    
    tick_params(left = False)
    
    ###
    
    savefig(filename+'.png')
    show()
    
    
input0 = input('Plot band structure, density of states or both? BS/DoS/Both ')

if input0 in ['BS','bs']:
    input1 = input('Band structure filename? ')
    input3 = input('Desired destination filename? ')
    input4 = input('Which bands do you want to print? (Leave blank for all) ')
    input5 = input('Print in eV? Y/N ')
    input6 = input('Absolute energy? Y/N ')
    input7 = input('Band structure title? (Leave blank for default title) ')
    
    if len(input4) is 2:
        input4 = input4.split(',')
        for num in range(0, len(input4)):
            input4[num] = int(input4[num])

    if input5 is ['Y', 'y']:
        elecvolts = True 
    elif input5 is ['N', 'n']:
        elecvolts = False
        
    if input6 is ['Y', 'y']:
        fermien = True 
    elif input6 is ['N', 'n']:
        fermien = False

    if len(input4) is 0:
        plot_bs(input1, input3, input7, eV = elecvolts, fermienergy = fermien)
    
    elif len(input4) is 1:
        input4 = int(input4)
        plot_bs(input1, input3, input7, int(input4), eV = elecvolts, fermienergy = fermien)

    elif len(input4) is 2:
        plot_bs(input1, input3, input7, input4[0], input4[1], eV = elecvolts, fermienergy = fermien)
    
elif input0 in ['DoS', 'dos', 'DOS']:
    input2 = input('Density of states filename? ')
    input3 = input('Desired destination filename? ')
    input5 = input('Print in eV? Y/N ')
    input6 = input('Absolute energy? Y/N ')
    input8 = input('Density of states title? (Leave blank for default title) ')
    
    if input5 is ['Y', 'y']:
        elecvolts = True 
    elif input5 is ['N', 'n']:
        elecvolts = False
    
    if input6 is ['Y', 'y']:
        fermien = True 
    elif input6 is ['N', 'n']:
        fermien = False
    
    plot_dos(input2,  input3, input8, eV = elecvolts, fermienergy = fermien)

elif input0 in ['Both','both']:
    input1 = input('Band structure filename? ')
    input2 = input('Density of states filename? ')
    input3 = input('Desired destination filename? ')
    input4 = input('Which bands do you want to print? (Leave blank for all) ')
    input5 = input('Print in eV? Y/N ')
    input6 = input('Absolute energy? Y/N ')
    input7 = input('Band structure title? (Leave blank for default title) ')
    input8 = input('Density of states title? (Leave blank for default title) ')

    if len(input4) is 2:
        input4 = input4.split(',')
        for num in range(0, len(input4)):
            input4[num] = int(input4[num])

    if input5 is ['Y', 'y']:
        elecvolts = True 
    elif input5 is ['N', 'n']:
        elecvolts = False
    
    if input6 is ['Y', 'y']:
        fermien = True 
    elif input6 is ['N', 'n']:
        fermien = False

    if len(input4) is 0:
        plot_bs_dos(input1, input2, input3, input7, input8, eV = elecvolts, fermienergy = fermien)
    
    elif len(input4) is 1:
        input4 = int(input4)
        plot_bs_dos(input1, input2, input3, input7, input8, int(input4), eV = elecvolts, fermienergy = fermien)

    elif len(input4) is 2:
        plot_bs_dos(input1, input2, input3, input7, input8, input4[0], input4[1], eV = elecvolts, fermienergy = fermien)
