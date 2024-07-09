from api_modules import *
import config

lon_list = []
lat_list = []
u_list = []
v_list = []
gliders = ['unit_345', 'unit_397', 'unit_398', 'unit_405']
#Unit 345
data = get_positions(config.token, 'slocum', 'unit_345')
create_kml_line(data, 'unit_345_traj.kml', simplekml.Color.purple)
print(f'')


#Unit 397

data = get_positions(config.token, 'slocum', 'unit_397')
create_kml_line(data, 'unit_397_traj.kml', simplekml.Color.orange)

#Unit 398
data = get_positions(config.token, 'slocum', 'unit_398')
create_kml_line(data, 'unit_398_traj.kml', simplekml.Color.green)


#unit 405

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