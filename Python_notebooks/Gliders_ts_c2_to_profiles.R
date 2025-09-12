library(tidyverse)
source("Plotting_tools/profiling.r")
source("Plotting_tools/pdf_prof_plotting.r")

dat <- read_csv("Data/Gliders/glider_927_c2merged.csv")

dat_with_prof <- assign_profiles_surface_or_deep(dat)
dat_with_prof <- dat_with_prof |> mutate(
  profile_num = case_when(is.na(profile_state) ~ profile_num, TRUE ~ 0),
  profile_num = match(profile_num, unique(profile_num)),
  cast = case_when(profile_num %% 2 == 0 ~ "Down",
                   TRUE ~ "Up")) |> 
  filter(profile_num > 1)

sample <- dat[1:5000,]

ggplot(dat_with_prof)+
  geom_point(aes(x = timestamp, y = -sci_water_pressure, color = cast))

data_to_plot <- filter(dat_with_prof, profile_num == 15)

ggplot(data_to_plot)+
  geom_point(aes(x = sci_rbrtridente_ch3_sig, y = - sci_water_pressure, color = timestamp))
ggplot(data_to_plot)+
  geom_point(aes(x = timestamp, y = -sci_water_pressure, color = profile_num))

ggplot(data_to_plot)+
  geom_point(aes(x = sci_flbbcd_cdom_units, y = - sci_water_pressure, color = "Seabird"))+
  geom_point(aes(x = sci_rbrtridente_ch3_sig, y = - sci_water_pressure, color = "RBR"))+
  theme_minimal()+
  xlab("CDOM")+
  ylim(-100, 0)+
  scale_color_brewer(palette = "Set1", name = "Sensor")

ggplot(data_to_plot)+
  geom_point(aes(x = sci_flbbcd_bb_units, y = - sci_water_pressure, color = "Seabird"))+
  geom_point(aes(x = sci_rbrtridente_ch1_sig, y = - sci_water_pressure, color = "RBR"))+
  theme_minimal()+
  xlab("bb (m-1)")+
  ylim(-50, 0)+
  scale_color_brewer(palette = "Set1", name = "Sensor")


make_profile_plots(dat_with_prof, pdf_file = "Output/profiles.pdf")

write_csv(dat_with_prof, "Output/Glider927_C2_timeseries.csv")

# median and R2 ----------------------------------------------------------

df_binned <- dat_with_prof %>%
  group_by(profile_num) |> 
  select(-cast) |> 
  mutate(bin_time = floor_date(timestamp, unit = "60 seconds")) %>%
  group_by(bin_time) %>%
  summarise_all(median, na.rm = TRUE, .groups = "drop")

data_to_plot <- filter(df_binned, profile_num == 22)

ggplot(data_to_plot)+
  geom_point(aes(x = sci_rbrtridente_ch2_sig, y = - sci_water_pressure))
ggplot(data_to_plot)+
  geom_point(aes(x = timestamp, y = -sci_water_pressure, color = profile_num))

ggplot(filter(df_binned, sci_water_pressure < 20))+
  geom_point(aes(x = log(sci_flbbcd_chlor_units), y = log(sci_rbrtridente_ch2_sig)))+
  geom_path(aes(x = log(sci_flbbcd_chlor_units), y = log(sci_flbbcd_chlor_units)), color = "Red")

model = lm(log(sci_flbbcd_chlor_units)~log(sci_rbrtridente_ch2_sig), df_binned)
summary(model)

ggplot(filter(df_binned, sci_flbbcd_bb_units < 0.001))+
  geom_point(aes(x = log(sci_flbbcd_bb_units), y = log(sci_rbrtridente_ch1_sig)))+
  geom_path(aes(x = log(sci_flbbcd_bb_units), y = log(sci_flbbcd_bb_units)), color = "Red")+
  theme_minimal(base_size = 14)

ggplot(filter(df_binned, sci_flbbcd_bb_units < 0.001))+
  geom_point(aes(x = sci_flbbcd_bb_units, y = sci_rbrtridente_ch1_sig))+
  geom_path(aes(x = sci_flbbcd_bb_units, y = sci_flbbcd_bb_units), color = "Red")+
  theme_minimal(base_size = 14)


model = lm(sci_rbrtridente_ch1_sig~sci_flbbcd_bb_units, df_binned)
summary(model)

ggplot(df_binned)+
  geom_point(aes(x = sci_flbbcd_cdom_units, y = sci_rbrtridente_ch3_sig))+
  geom_path(aes(x = sci_flbbcd_cdom_units, y = sci_flbbcd_cdom_units), color = "Red")+
  theme_minimal(base_size = 14)


ggplot(df_binned)+
  geom_point(aes(x = bin_time, y = - sci_water_pressure, color = sci_flbbcd_bb_units))+
  scale_color_viridis_c()+
  theme_minimal()
