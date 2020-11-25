#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 09:50:46 2017
author: Jiajia Liu @ University of Sheffield

Please change parameters in this file
"""
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pickle
# Also dependent on sklearn (0.19.1)


def get_mean(array, low, high, null=999):
    '''
    obtain average value for a given array from index low to index high
    '''
    flag = 0
    if low > high:
        flag = 1
        tem = high
        high = low
        low = tem
    avg = np.mean([])
    while np.isnan(avg):
        dust = array[low:high+1]
        dust2 = []
        for value in dust:
            if int(value) != null and not np.isnan(float(value)):
                dust2.append(value)
        dust2 = np.array(dust2, dtype=float)

        if len(dust2) != 0:
            avg = dust2.mean()
        else:
            avg = np.nan
        if np.isnan(avg):
            if flag == 0:
                low = low - 1
            else:
                high = high + 1
    if high - low > 24: # if there is no data that day
        avg = 1e-5

    return "{0:.5f}".format(avg)


def read_omni(time='2015-04-04T16:32:00', duration=6):
    '''
    Get solar wind plasma data for a giving time and time duration
    '''
    url = 'https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_' + \
          time[0:4] + '.dat'
    data = pd.read_csv(url, delimiter="\s+", header=None)
    time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    doy = time - datetime.strptime(str(time.year) + '-01-01', '%Y-%m-%d')
    doy = np.int(doy.total_seconds() / (3600. * 24.))
    idx = np.long(doy * 24. - 24) + time.hour
    wind = {}
    wind.setdefault('Bz', get_mean(data[14], idx, idx+duration))
    wind.setdefault('Ratio', get_mean(data[27], idx, idx+duration, 9))
    wind.setdefault('V', get_mean(data[24], idx, idx+duration, 9999))
    wind.setdefault('Lat', get_mean(data[26], idx, idx+duration))
    wind.setdefault('P', get_mean(data[28], idx, idx+duration, 99))
    wind.setdefault('Lon', get_mean(data[25], idx, idx+duration))
    wind.setdefault('Bx', get_mean(data[12], idx, idx+duration))
    wind.setdefault('T', get_mean(data[22], idx, idx+duration, 9999999))

    return wind


def get_svm_input(info, features):
    '''
    return value:
        array x for the input of the engine
    '''
    features = sorted(features)
    x = []
    if 'CME Acceleration' in features:
        x.append(np.array(info['Acceleration'], dtype=float))
    if 'CME Angular Width' in features:
        x.append(np.array(info['Width'], dtype=float))
    if 'CME Average Speed' in features:
        x.append(np.array(info['Speed'], dtype=float))
    if 'CME Final Speed' in features:
        x.append(np.array(info['Speed_final'], dtype=float))
    if 'CME Mass' in features:
        x.append(np.array(info['Mass'], dtype=float))
    if 'CME Position Angle' in features:
        x.append(np.array(info['PA'], dtype=float))
    if 'CME Source Region Latitude' in features:
        x.append(np.array(info['Lat'], dtype=float))
    if 'CME Source Region Longitude' in features:
        x.append(np.array(info['Lon'], dtype=float))
    if 'CME Speed at 20 Rs' in features:
        x.append(np.array(info['Speed_20'], dtype=float))

    wind = info['Wind']

    if 'Solar Wind Bx' in features:
        x.append(np.array(wind['Bx'], dtype=float))
    if 'Solar Wind By' in features:
        x.append(np.array(wind['By'], dtype=float))
    if 'Solar Wind Bz' in features:
        x.append(np.array(wind['Bz'], dtype=float))
    if 'Solar Wind Density' in features:
        x.append(np.array(wind['Rho'], dtype=float))
    if 'Solar Wind He Proton Ratio' in features:
        x.append(np.array(wind['Ratio'], dtype=float))
    if 'Solar Wind Latitude' in features:
        x.append(np.array(wind['Lat'], dtype=float))
    if 'Solar Wind Longitude' in features:
        x.append(np.array(wind['Lon'], dtype=float))
    if 'Solar Wind Plasma Beta' in features:
        x.append(np.array(wind['Beta'], dtype=float))
    if 'Solar Wind Pressure' in features:
        x.append(np.array(wind['P'], dtype=float))
    if 'Solar Wind Speed' in features:
        x.append(np.array(wind['V'], dtype=float))
    if 'Solar Wind Temperature' in features:
        x.append(np.array(wind['T'], dtype=float))

    x = np.array(x)
    x = x.reshape(1, -1)

    return x


class svm_engine:
    None


if __name__ == '__main__':
    # Do not edit the following parameters unless you know exactly what you want
    # -----------------------------------------------------------------------------
    features = ['CME Average Speed',
                'CME Final Speed',
                'CME Angular Width',
                'CME Mass',
                'Solar Wind Bz',
                'Solar Wind Speed',
                'Solar Wind Temperature',
                'Solar Wind Pressure',
                'Solar Wind Longitude',
                'Solar Wind He Proton Ratio',
                'Solar Wind Bx',
                'CME Position Angle'
                ]
    duration = 6  # will average 6-hour solar wind parameters after the CME onset
    engine_file = './engine.obj'
    # -----------------------------------------------------------------------------
    
    # CME Parameters
    time = '2015-12-28T12:12:00'  # CME Onset time in LASCO C2
    width = 360.  # angular width, degree, set as 360 if it is halo
    speed = 1212.  # linear speed in LASCO FOV, km/s
    final_speed = 1243.  # second order final speed leaving LASCO FOV, km/s
    mass = 1.9e16  # estimated mass using 'cme_mass.pro' in SSWIDL or from the 
                   # SOHO LASCO CME Catalog
    mpa = 163.  # degree, position angle corresponding to the fasted front
    actual = '2015-12-31T00:02:00'  # Actual arrival time, set to None if unknown
    
    # Solar Wind Parameters
    auto = True  # Obtain solar wind parameter automatically or manually?
    
    time = time.replace('/', '-')
    time = time.replace(' ', 'T')
    if auto:  # automatically obtain solar wind data from omniweb plus
        wind = read_omni(time, duration)
    else:
        wind = {'Bz': 0.0,
                'Ratio': 0.0,
                'V': 0.0,
                'Lat': 0.0,
                'P': 0.0,
                'Lon': 0.0,
                'Bx': 0.0,
                'T': 0.0}
    
    info = {'CME': time,
            'Speed': speed,
            'Speed_final': final_speed,
            'Width': width,
            'Mass': mass,
            'PA': mpa}
    
    info.setdefault('Wind', wind)
    
    # Get input for the engine
    xinput = get_svm_input(info, features)
    # Load the engine
    f = open(engine_file, 'r')
    engine = pickle.load(f)
    f.close()
    # Normalize x
    xinput = engine.scaler.transform(xinput)
    # Do Prediction
    travel = engine.clf.predict(xinput)[0]
    arrive = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=travel)
    arrive = datetime.strftime(arrive, '%Y-%m-%dT%H:%M:%S')
    # Show Result
    print ('%s%s%s' % ('CME with onset time ', time, ' UT'))
    print ('%s%s%s' % ('Will hit the Earth at ', arrive, ' UT'))
    print ('%s%6.1f%s' % ('with a transit time of', travel, ' hours'))
    
    if actual is not None:
        diff = datetime.strptime(arrive, '%Y-%m-%dT%H:%M:%S') - \
               datetime.strptime(actual, '%Y-%m-%dT%H:%M:%S')
        diff = diff.total_seconds() / 3600.
        print ('%s%s%s' % ('The actual arrival time is ', actual, ' UT'))
        print ('%s%6.1f%s' % ('The prediction error is', diff, ' hours '))
