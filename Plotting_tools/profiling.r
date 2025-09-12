library(dplyr)

assign_profiles_surface_or_deep <- function(df,
                                            depth_col = "sci_water_pressure",
                                            surface_range = c(0, 0.5),
                                            deep_range = c(95, 100)) {
  
  df <- df %>% arrange(timestamp)
  
  profile_id <- 0
  profiles <- integer(nrow(df))
  state <- rep(NA_character_, nrow(df))  # "surfacing" / "deep" / NA
  
  for (i in seq_len(nrow(df))) {
    depth <- df[[depth_col]][i]
    
    if (!is.na(depth)) {
      # Start a new profile at surface or deep
      if ((depth >= surface_range[1] && depth <= surface_range[2]) ||
          (depth >= deep_range[1] && depth <= deep_range[2])) {
        profile_id <- profile_id + 1
      }
      
      # Assign profile state
      if (depth >= surface_range[1] && depth <= surface_range[2]) {
        state[i] <- "surfacing"
      } else if (depth >= deep_range[1] && depth <= deep_range[2]) {
        state[i] <- "deep"
      } else {
        state[i] <- NA
      }
      
      # Assign current profile number
      profiles[i] <- profile_id
    }
  }
  
  df <- df %>%
    mutate(profile_num = profiles,
           profile_state = state)
  
  return(df)
}

