from api_modules import *
from kml_plot_toolbox import *
import datetime
import config
import cartopy.crs as ccrs
import numpy as np
import matplotlib.pyplot as plt

# currents = get_observations(config.token, 'slocum', "unit_398", variables = ["m_water_vy", "m_water_vx", "m_lat", "m_lon", "m_time"])

# print(currents)

# quit()
lon_list = []
lat_list = []
u_list = []
v_list = []
gliders = ['unit_345', 'unit_397', 'unit_398', 'unit_405']
#Unit 345
print(f"Unit 345 traj updating...")
data = get_positions(config.token, 'slocum', 'unit_345')
create_kml_line(data, 'unit_345_traj.kml', simplekml.Color.purple)

#Unit 397
print(f"Unit 397 traj updating...")
data = get_positions(config.token, 'slocum', 'unit_397')
create_kml_line(data, 'unit_397_traj.kml', simplekml.Color.orange)

#Unit 398
print(f"Unit 398 traj updating...")
data = get_positions(config.token, 'slocum', 'unit_398')
create_kml_line(data, 'unit_398_traj.kml', simplekml.Color.green)


#unit 405
print(f"Unit 405 traj updating...")
data = get_positions(config.token, 'slocum', 'unit_405')
create_kml_line(data, 'unit_405_traj.kml', simplekml.Color.blue)


currents = get_observations(config.token, 'slocum', gliders, variables = ["m_water_vy", "m_water_vx", "m_lat", "m_lon", "m_time"])

for i in gliders:
    df_temp = currents[currents['platform_serial'] == i]

    v = df_temp[df_temp['variable'] == 'm_water_vy']
    last_time = v["timestamp"].max()
    v = v['value'].iloc[-1]
    v_list.append(v)


    u = df_temp[df_temp['variable'] == 'm_water_vx']
    last_time = u["timestamp"].max()
    u = u['value'].iloc[-1]
    u_list.append(u)

    lon_v = df_temp[df_temp['variable'] == 'm_lon']
    last_time = lon_v["timestamp"].max()
    lon_v = lon_v['value'].iloc[-1]
    lon_list.append(lon_v)

    lat_v = df_temp[df_temp['variable'] == 'm_lat']
    last_time = lat_v["timestamp"].max()
    lat_v = lat_v['value'].iloc[-1]
    lat_list.append(lat_v)


create_kml_point(gliders, lon_list, lat_list, u_list, v_list, 'last_pos.kml')

print(f"Making a csv...")

#write a csv

currents['datetime'] = currents['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000, datetime.UTC))
currents_position = currents[currents['variable'].isin(['m_lon', 'm_lat'])].drop_duplicates(subset=['value'])

currents_x = currents[currents['variable'] == 'm_water_vx'].drop_duplicates(subset=['value'])
currents_y = currents[currents['variable'] == 'm_water_vy'].drop_duplicates(subset=['value'])
currents_position = currents_position.pivot_table(index='datetime', columns='variable', values='value').reset_index()
currents_x =  currents_x.pivot_table(index='datetime', columns='variable', values='value').reset_index()
currents_y =  currents_y.pivot_table(index='datetime', columns='variable', values='value').reset_index()


# Ensure both DataFrames are sorted by the datetime column
currents_position = currents_position.sort_values('datetime')
currents_x = currents_x.sort_values('datetime')
currents_y = currents_y.sort_values('datetime')

# Perform the asof merge
merged_current = pd.merge_asof(currents_x, currents_y, on='datetime', direction='nearest')
merged_df = pd.merge_asof(currents_position, merged_current, on='datetime', direction='nearest')

# Get the current time in UTC
now = pd.Timestamp.now(tz='UTC')

# Calculate the time 24 hours ago
last_day = now - datetime.timedelta(hours=24)

filtered_dac =  merged_df[merged_df['datetime'] >= last_day]
filtered_dac = filtered_dac.drop_duplicates(subset=['m_lon', 'm_lat']).drop_duplicates(subset=['m_water_vx'])

current_data = filtered_dac.copy()
#filtered_dac.to_csv('gliders_dac.csv')

print(f"Making a quiver plot...")
#extract the lon and lat from the dataset only once
x = current_data['m_lon']
y = current_data['m_lat']


#From the U and V vector compute the speed, we use it as our colour map
u = current_data['m_water_vx']
v = current_data['m_water_vy']
speed = np.sqrt(pd.Series(u_list)**2 + pd.Series(v_list)**2)

#Set up the plot layout, extent and title


fig, ax = gearth_fig(llcrnrlon=x.min()-0.2,
                     llcrnrlat=y.min()-0.1,
                     urcrnrlon=x.max()+0.2,
                     urcrnrlat=y.max()+0.1)
#ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

#Plot the current vectors field and the coastline
im = ax.quiver(lon_list, lat_list, u_list, v_list, speed, angles='xy', scale_units='xy', cmap='jet', scale = 30)

ax.set_axis_off()
#format the color bar
#cbar = plt.colorbar(im, ax = ax, label=r'Depth averaged current (m s$^{-1}$)')
#cbar.set_label(r'Depth averaged current (m s$^{-1}$)', rotation=270, labelpad=15)

#save the plot and then close it to avoid high memory usage
plt.savefig('gliders_dac.png', transparent = True)
plt.clf()
plt.close()

fig = plt.figure(figsize=(1.0, 4.0), facecolor=None, frameon=False)
ax = fig.add_axes([0.0, 0.05, 0.2, 0.9])
cb = fig.colorbar(im, cax=ax)
cb.set_label(label=r'Depth averaged current (m s$^{-1}$)', rotation=-90, color='k', labelpad=20)
fig.savefig('legend.png', transparent=True, format='png') 

make_kml(llcrnrlon=x.min()-0.2, llcrnrlat=y.min()-0.1,
         urcrnrlon=x.max()+0.2, urcrnrlat=y.max()+0.1,
         figs=['gliders_dac.png'], colorbar='legend.png',
         kmzfile='dac_uv.kmz', name='Depth averaged current')