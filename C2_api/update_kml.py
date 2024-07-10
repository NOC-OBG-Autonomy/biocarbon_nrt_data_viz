from api_modules import *
import datetime
import config

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
    v = v['value'].iloc[-1]
    v_list.append(v)

    u = df_temp[df_temp['variable'] == 'm_water_vx']
    u = u['value'].iloc[-1]
    u_list.append(u)

    lon_v = df_temp[df_temp['variable'] == 'm_lon']
    lon_list.append(lon_v['value'].iloc[-1])

    lat_v = df_temp[df_temp['variable'] == 'm_lat']
    lat_list.append(lat_v['value'].iloc[-1])


create_kml_point(gliders, lon_list, lat_list, u_list, v_list, 'last_pos.kml')

print(f"All done !")

#write a csv

# currents['datetime'] = currents['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000, datetime.UTC))
# currents_position = currents[currents['variable'].isin(['m_lon', 'm_lat'])]
# currents_x = currents[currents['variable'] == 'm_water_vx']
# currents_y = currents[currents['variable'] == 'm_water_vy']
# currents_position = currents_position.pivot_table(index='datetime', columns='variable', values='value').reset_index()
# currents_x =  currents_x.pivot_table(index='datetime', columns='variable', values='value').reset_index()
# currents_y =  currents_y.pivot_table(index='datetime', columns='variable', values='value').reset_index()


# # Ensure both DataFrames are sorted by the datetime column
# currents_position = currents_position.sort_values('datetime')
# currents_x = currents_x.sort_values('datetime')
# currents_y = currents_y.sort_values('datetime')

# # Perform the asof merge
# merged_df = pd.merge_asof(currents_x, currents_y, on='datetime', direction='nearest')
# merged_df = pd.merge_asof(merged_df, currents_position, on='datetime', direction='nearest')

# # Get the current time in UTC
# now = pd.Timestamp.now(tz='UTC')

# # Calculate the time 24 hours ago
# last_day = now - datetime.timedelta(hours=24)

# filtered_dac =  merged_df[merged_df['datetime'] >= last_day]
# filtered_dac = filtered_dac.drop_duplicates(subset=['m_lon', 'm_lat'])

# filtered_dac.to_csv('gliders_dac.csv')