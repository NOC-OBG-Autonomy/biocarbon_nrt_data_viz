library(ggplot2)
library(dplyr)
library(patchwork)   # for side-by-side plots
library(ggpubr)      # for arranging multiple plots
library(gridExtra)   # optional, for flexible layouts

make_profile_plots <- function(df, pdf_file = "profiles.pdf") {
  
  # identify profiles
  profiles <- unique(df$profile_num)
  
  # open pdf device
  pdf(pdf_file, width = 10, height = 12)  # landscape-like pages
  
  # iterate over profiles in groups of 3
  for (i in seq(1, length(profiles), by = 3)) {
    # select up to 3 profiles
    subset_profiles <- profiles[i:min(i+2, length(profiles))]
    
    plots <- list()
    
    for (p in subset_profiles) {
      data_to_plot <- df %>% filter(profile_num == p)
      
      p1 <- ggplot(data_to_plot) +
        geom_point(aes(x = sci_flbbcd_chlor_units,
                       y = -sci_water_pressure,
                       color = "Seabird")) +
        geom_point(aes(x = sci_rbrtridente_ch2_sig,
                       y = -sci_water_pressure,
                       color = "RBR")) +
        theme_minimal() +
        xlab("Chlorophyll (mg.m-3)") +
        ylab("Depth (m)") +
        ylim(-15, 0) +
        scale_color_brewer(palette = "Set1", name = "Sensor") +
        ggtitle(paste("Profile", p, "- Chlorophyll"))
      
      p2 <- ggplot(data_to_plot) +
        geom_point(aes(x = sci_flbbcd_bb_units,
                       y = -sci_water_pressure,
                       color = "Seabird")) +
        geom_point(aes(x = sci_rbrtridente_ch1_sig,
                       y = -sci_water_pressure,
                       color = "RBR")) +
        theme_minimal() +
        xlab("bb (m-1)") +
        ylab("Depth (m)") +
        ylim(-50, 0) +
        scale_color_brewer(palette = "Set1", name = "Sensor") +
        ggtitle(paste("Profile", p, "- Backscatter"))
      
      # store as one row (chlorophyll | bb)
      plots[[length(plots) + 1]] <- p1 + p2
    }
    
    # arrange 3 rows per page
    final_page <- ggpubr::ggarrange(plotlist = plots, ncol = 1, nrow = 3)
    print(final_page)
  }
  
  dev.off()
}
