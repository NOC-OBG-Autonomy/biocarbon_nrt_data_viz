import xarray as xr
import numpy as np
from scipy import signal 
from tqdm import tqdm

def boxcar_smooth_dataset(dataset, window_size):
    """Smooth data with a simple box car filter
    """
    window = signal.windows.boxcar(window_size)
    return signal.convolve(dataset, window, 'same') / window_size

def find_profiles_by_depth(db, tsint=2, winsize=10):
    """Discovery of profiles in a glider segment using depth and time.

    Profiles are discovered by smoothing the depth (pressure) timeseries and using the
    derivative of depth vs time (or N_MEASUREMENTS index) to find the inflection points to break
    the segment into profiles. The surfacing behaviour is detected and removed from the profile index.
    For smoothing a filtered depth is created at regular time intervals `tsint` (default
    2 secs) and boxcar filtered with window `winsize` (default 5 points).
    The smoothing is affected by both choice of `tsint` and `winsize`, but
    usually still returns similar profiles.  After profiles are discovered,
    they should be filtered with the `filter_profiles` method of this
    class, which removes profiles that are not true profiles.

    Args:
        db (string): The path of the OG1 format data
        tsint (integer): interval of smoothing
        winsize (integer): window of smoothing
    """
    indices = []

    dat = xr.open_dataset(db)

    depth = dat['PRES'].values
    # Identify indices of valid and NaN values
    nans = np.isnan(depth)
    valid = ~nans

    # Interpolate the NaN values
    depth[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(valid), depth[valid])

    ts = dat.N_MEASUREMENTS.values
    time_ = dat.N_MEASUREMENTS.values

    # Set negative depth values to NaN; using this method to avoid numpy
    # warnings from < when nans are in the array
    depth_ii = np.flatnonzero(np.isfinite(depth))  # non-nan indices
    neg_depths = np.flatnonzero(depth[depth_ii] <= 0)  # indices to depth_ii
    depth[depth_ii[neg_depths]] = np.nan

    # Remove NaN depths and truncate to when science data begins being
    # recorded and ends
    depth_ii = np.flatnonzero(np.isfinite(depth))

    sci_indices = dat.N_MEASUREMENTS.values
    if len(sci_indices) > 0:
        starting_index = sci_indices[0]
        ending_index = sci_indices[-1]
    else:
        print(f'No data in {db}')
        return  # no science_indices, then we don't care to finish

    depth_ii = depth_ii[
        np.logical_and(
            depth_ii >= starting_index,
            depth_ii <= ending_index)
    ]

    # ---Create a smoothed depth timeseries for finding inflections ------#

    # Find start and end times first adding winsize * tsint timesteps
    # onto the start and end to account for filter edge effects
    itime_start = np.ceil(ts[depth_ii].min()) - winsize * tsint
    itime_end = np.floor(ts[depth_ii].max()) + (winsize + 1) * tsint

    itime = np.arange(itime_start, itime_end, tsint)
    idepth = np.interp(itime, ts[depth_ii], depth[depth_ii],
                        left=depth[depth_ii[0]], right=depth[depth_ii[-1]])
    fz = boxcar_smooth_dataset(idepth, winsize)

    # remove the extra points with filter edge effects
    # ? isn't that why we trim itime_[start,end] by the window size?
    fz = fz[winsize:-winsize]
    itime = itime[winsize:-winsize]
    idepth = idepth[winsize:-winsize]

    # Zero crossings of the time derivative of filtered depth are the
    # inflection points.  Differential time is midway between the
    # filtered timestamps.
    # Originally, this used scipy's fsolver to locate the exact zero
    # crossing, but only the timestamp before the zero crossing is needed
    # to be the last in a profile and the timestamp after the zero
    # crossing to be the first in the next profile.

    dz_dt = np.diff(fz) / np.diff(itime)
    dtime = itime[:-1] + np.diff(itime) / 2  # differential time

    # Get the time point just after a zero crossing.  The flatnonzero
    # statement below gets the point before a zero crossing.
    zero_crossings_ii = np.flatnonzero(abs(np.diff(np.sign(dz_dt))))
    zc_times = dtime[zero_crossings_ii] + (
            dtime[zero_crossings_ii + 1] - dtime[zero_crossings_ii]) / 2.

    profile_switch_times = zc_times[np.logical_and(
        zc_times > time_[starting_index],
        zc_times < time_[ending_index]
    )]
    # insert the timestamp of the first science data point at the start
    # and the last data point at the end.
    profile_switch_times = np.insert(
        profile_switch_times, [0, len(profile_switch_times)],
        [time_[starting_index],
            time_[ending_index]])

    inflection_times = profile_switch_times

    # profile_switch_times = self.adjust_inflections(depth, time_)
    profile_switch_times = adjust_inflections(depth, time_, inflection_times)

    

    # use the time range to gather indices for each profile
    for ii in range(len(profile_switch_times)-1):
        pstart = profile_switch_times[ii]
        pend = profile_switch_times[ii+1]
        profile_ii = np.flatnonzero(
            np.logical_and(
                time_ >= pstart,
                time_ <= pend))  # inclusive since before the inflection
        if len(profile_ii) == 0:
            continue
        indices.append(profile_ii)
    
    surfaces = find_surfacing(indices, depth, time_)

    profiles = []

    for prof_number in range(len(indices)):
        prof = indices[prof_number]
        pos = surfaces[prof_number]

        prof = np.delete(prof, pos)
        profiles.append(prof)

    return(profiles)

def adjust_inflections(depth, time_, inflection_times):
    """Filters out bad inflection points.

    Bad inflection points are small surface, bottom of dive, or mid-profile
    wiggles that are not associated with true dive or climb inflections.
    These false inflections are removed so that when profile indices are
    created, they don't separate into separate small profiles.

    Args:
        depth (array): pressure array from the OG1 format
        time_ (array): N_MEASUREMENTS array from the OG1 format
        inflection_times: inflection points detected by find_profile_by_depth function
    
    Return:
        An array of true inflection points

    """
    inflections = inflection_times
    inflection_depths = np.interp(
        inflections, time_[np.isfinite(depth)],
        depth[np.isfinite(depth)]
    )

    # First remove the false diving inflections (i.e. the small wiggles) by
    # taking the good inflection and looking ahead until an inflection depth
    # difference greater than 2m is found
    inflx_ii = 0
    fwd_counter = 1
    inflx_to_keep = np.full(len(inflections), True)
    while inflx_ii < len(inflections):
        ii_depth = inflection_depths[inflx_ii]  # depth of current inflection
        # look ahead for the next true inflection change
        if inflx_ii + fwd_counter >= len(inflections):
            break
        while abs(inflection_depths[inflx_ii + fwd_counter] - ii_depth) < 2:
            inflx_to_keep[inflx_ii + fwd_counter] = False
            fwd_counter += 1
            if inflx_ii + fwd_counter >= len(inflections):
                break
        inflx_ii = inflx_ii + fwd_counter
        fwd_counter = 1

    # afterwards we may be left with mid profile direction changes that were
    # greater than 2 m.  But now they can identified by not changing trend,
    # since any of our good  inflection points left will change trend sign.
    good_inflx_ii = np.flatnonzero(inflx_to_keep)
    trends = np.diff(inflection_depths[good_inflx_ii])
    # find where the trends are the same by getting the diff of the sign of
    # the trend (which is also a diff).  Must add one because diff always
    # results in N-1
    same_trends = np.flatnonzero(np.diff(np.sign(trends)) == 0) + 1
    good_inflx_ii = np.delete(good_inflx_ii, same_trends)
    inflection_times = inflections[good_inflx_ii]

    return inflection_times

def find_surfacing(prof_indexes, depth, itime, fwd_counter = 10, threshold = 2):
    """Identify indexes of surfacing behaviour (i.e. a slow vertical speed from the glider). It is not based on the absolute depth, so it can identify deep 'surfacing behavior'.
    Returns a 2D array of surfacing behavior in each profile. 

    Args:
        prof_indexes (2D array): array of n,m shapes where n is the number of profiles, it is the output from find_profiles_by_depth
        depth (array): The depth values (actually pressure)
        itime (array): A numeric index of the observations, for OG1 format it is N_MEASUREMENTS
        fwd_counter (integer): An integer corresponding to the delta number of observation on which we base our surface behavior detection
        threshold (integer): An integer corresponding to the maximal change in pressure to detect a surfacing behavior
    """
    surfaces = []

    # Find indices with finite (non-NaN) depths
    depth_ii = np.flatnonzero(np.isfinite(depth))
    neg_depths = np.flatnonzero(depth[depth_ii] <= 0)
    depth[depth_ii[neg_depths]] = np.nan

    # Recompute finite indices after replacing depths <= 0 with NaN
    depth_ii = np.flatnonzero(np.isfinite(depth))

    # Interpolate the depths for the measurements
    idepth = np.interp(itime, itime[depth_ii], depth[depth_ii],
                    left=depth[depth_ii[0]], right=depth[depth_ii[-1]])
    fz = boxcar_smooth_dataset(idepth, 10)

    for i in tqdm(range(len(prof_indexes))):
        profile_depth = fz[prof_indexes[i]]
        depth_ii = 0
        surface = []

        while depth_ii < (len(profile_depth) - fwd_counter):
            # Check if the pressure changes minimally over the next `fwd_counter` points
            if abs(profile_depth[depth_ii] - profile_depth[depth_ii + fwd_counter]) < threshold:
                surface.append(depth_ii)
                last_valid_depth = depth_ii  # Update to track the last valid `depth_ii`
                depth_ii += 1  # Skip forward to avoid overlapping ranges
            else:
                depth_ii += 1

        # After exiting the loop, append the last valid range if it exists
        if last_valid_depth == depth_ii - 1:
            surface.extend(list(range(last_valid_depth, last_valid_depth + fwd_counter + 1)))

        surfaces.append(surface)
    return(surfaces)

def interp_nan(var):
    """Linear interpolation of any variable. Used to plot variables that are not observed on the same time. 

    Args:
        var (array): A 1D array of any numerical variable.
    """    
    # Identify indices of valid and NaN values
    nans = np.isnan(var)
    valid = ~nans

    #Interpolate the NaN values
    var[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(valid), var[valid])

    return(var)

if __name__ == '__main__':

    #An example on how to split a OG1 in profiles and to look at specific profiles
    import matplotlib.pyplot as plt

    #Use Doombar data as example
    path = 'C:/Users/flapet/OneDrive - NOC/Documents/NRT_viz/biocarbon_nrt_data_viz/Data/Gliders/Doombar_648_R.nc'

    #Open the netcdf
    dat = xr.open_dataset(path)

    #Find profiles, will return a 2D array of indexes corresponding to profiles
    prof  = find_profiles_by_depth(path)

    #We can extract a 1D array of any profile based on the number of that profile (e.g. number 165)
    prof_165 = prof[165]

    #Then, we use the prof_165 to extract any variables we want to look
    pres = dat['PRES'][prof_165].values
    time = dat['TIME'][prof_165].values
    chla = dat['CHLA'][prof_165].values
    
    #There is a simple interpolation function above to match the same grid between pressure and variables
    chla = interp_nan(chla)
    pres = interp_nan(pres)

    #Simple plot
    plt.plot(chla, -pres)
    plt.show() 