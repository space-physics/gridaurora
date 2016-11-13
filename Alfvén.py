#!/usr/bin/env python
from numpy import exp,linspace,sqrt
from matplotlib.pyplot import figure,show
import seaborn as sns
sns.set_style('whitegrid')
#%% Staciewicz Eqn 3, Figure 3
"""
units for r,r0,h: Re
units for n,na,nb: cm^-3
"""
r0 = 1.05
h  = 0.06
na = 6e4
nb = 17
r = linspace(1.01,4,100)

Ne = na*exp(-(r-r0)/h) + nb*(r-1)**-1.5
Li = 5.3/sqrt(Ne)
#%% plot
alt_km = r*6371-6371
figure(3).clf()
ax = figure(3).gca()
ax.semilogy(alt_km,Ne,label='$N_e$ [cm$^{-3}$]')
ax.plot(alt_km,Li,label='$\lambda_e$ [km]')
ax.set_xlabel('altitude [km]')
ax.set_title('inertial length $\lambda_e$  electron number density $N_e$')
ax.legend()

show()