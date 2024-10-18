import xarray as xr
import numpy as np
from scipy import signal 
def boxcar_smooth_dataset(dataset, window_size):
    """Smooth data with a simple box car filter
    """
    window = signal.windows.boxcar(window_size)
    return signal.convolve(dataset, window, 'same') / window_size

def find_profiles_by_depth(db, tsint=2, winsize=10):
    """Discovery of profiles in a glider segment using depth and time.

    Profiles are discovered by smoothing the depth timeseries and using the
    derivative of depth vs time to find the inflection points to break
    the segment into profiles.  Profiles are truncated to where science
    data exists; science sensors for the glider are configured in
    Configuration.py.
    Depth can be `DEPTH_SENSOR` as configured in configuration.py or
    CTD pressure (Default `DEPTH_SENSOR`).  For smoothing
    a filtered depth is created at regular time intervals `tsint` (default
    2 secs) and boxcar filtered with window `winsize` (default 5 points).
    The smoothing is affected by both choice of `tsint` and `winsize`, but
    usually still returns similar profiles.  After profiles are discovered,
    they should be filtered with the `filter_profiles` method of this
    class, which removes profiles that are not true profiles.

    :param depth_sensor: The Depth sensor to use for profile discovery.
    Should be either the configured `DEPTH_SENSOR`, or CTD pressure
    `PRESSURE_SENSOR` (configured in configuration.py), or a
    derivative of those 2.  Default is `DEPTH_SENSOR`
    :param tsint: Time interval in seconds for filtered depth.
    This affects filtering.  Default is 2.
    :param winsize: Window size for boxcar smoothing filter.
    :return: output is a list of profile indices in self.indices
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
    
    return(indices)

def adjust_inflections(depth, time_, inflection_times):
    """Filters out bad inflection points.

    Bad inflection points are small surface, bottom of dive, or mid-profile
    wiggles that are not associated with true dive or climb inflections.
    These false inflections are removed so that when profile indices are
    created, they don't separate into separate small profiles.

    :param depth:
    :param time_:
    :return:
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



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    path = 'C:/Users/flapet/OneDrive - NOC/Documents/NRT_viz/biocarbon_nrt_data_viz/Data/Gliders/Doombar_648_R.nc'
    dat = xr.open_dataset(path)
    prof  = find_profiles_by_depth(path)
    prof_165 = prof[34]
    pres = dat['PRES'][prof_165].values
    time = dat['TIME'][prof_165].values
    # Identify indices of valid and NaN values
    nans = np.isnan(pres)
    valid = ~nans

    # Interpolate the NaN values
    pres[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(valid), pres[valid])
    plt.plot(time, pres)
    plt.show() 