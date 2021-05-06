# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

time1=np.array([0.0333,0.0667,0.1000,0.1333,0.1667,0.2000,0.2333,0.2667,0.3000,0.3333,0.3667,0.4000,0.4333,
0.4667,0.5000,0.5333,0.5667,0.6000,0.6333,0.6667,0.7000])
time1_err=np.array([0.04])

velo1=np.array([0.3691,0.5211,0.6513,0.6513,0.7816,0.8901,0.9118,1.0421,1.1072,1.2158,1.3678,1.3678,1.3895,
1.5197,1.7586,1.8454,1.8237,1.8888,1.9974,2.1711,2.1928])
velo1_err=np.array([0.0092,0.0130,0.0163,0.0163,0.0195,0.0223,0.0228,0.0261,0.0277,0.0304,0.0342,0.0342,0.0347,
0.0380,0.0440,0.0461,0.0456,0.0472,0.0499,0.0543,0.0548])

time2=np.array([0.033333333,0.066666667,0.1,0.133333333,0.166666667,0.2,0.233333333,0.266666667,0.3,0.333333333,
0.366666667,0.4,0.433333333,0.466666667])
time2_err=np.array([0.04])

velo2=np.array([0.307544536,0.461316804,0.70295894,0.966568543,1.142308278,1.361982946,1.625592549,1.911169618,
2.086909353,2.284616555,2.723965893,2.965608029,2.987575495,3.361022432])
velo2_err=np.array([0.007688613,0.01153292,0.017573974,0.024164214,0.028557707,0.034049574,0.040639814,0.04777924,
0.052172734,0.057115414,0.068099147,0.074140201,0.074689387,0.084025561])

slope1, intercept1,r_value, p_value, std_err = stats.linregress(time1,velo1)
slope2, intercept2,r_value, p_value, std_err = stats.linregress(time2,velo2)

fig,ax1 = plt.subplots(1,1)

ax1.errorbar(time1,velo1,xerr=0.04,yerr=velo1_err,fmt='o',elinewidth=1,capsize=3,capthick=1,ms=3,c='b',ecolor='black')
ax1.plot(time1,slope1*time1+intercept1,c='b')

ax1.text(.55,.30, f'Set1:\n y={slope1:.4f}x+{intercept1:.4f}',fontsize=12,horizontalalignment='left',
         verticalalignment='top', transform=ax1.transAxes)

ax1.errorbar(time2,velo2,xerr=0.04,yerr=velo2_err,fmt='o',elinewidth=1,capsize=3,capthick=1,ms=3,c='orange',ecolor='black' )
ax1.plot(time2,slope2*time2+intercept2,c='orange')

ax1.text(.48,.7, f'Set2:\n y={slope2:.4f}x{intercept2:.4f}',fontsize=12,horizontalalignment='left',
         verticalalignment='top', transform=ax1.transAxes)

ax1.tick_params(direction='in', which='both',top=True,right=True,labelsize=12)

#ax1.legend(fontsize='small')
ax1.set_ylabel('Velocity (m/s)',fontsize=12)
ax1.set_xlabel('Time (s)',fontsize=12)
ax1.set_ylim(0.2,3.5)
ax1.set_xlim(0,0.75)

plt.tight_layout()
plt.show()


