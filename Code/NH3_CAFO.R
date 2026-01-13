library(readxl)
library(dplyr)
library(ggplot2)
library(maps)
library(scales)

# -----------------------------
# Read NH3 data
# -----------------------------
nh3_df <- read_excel("/Users/benjohnson/Downloads/conus_nh3_countavg_june_aug_2021_2023 (1).xls") %>%
  transmute(
    lon = as.numeric(Longitude),
    lat = as.numeric(Latitude),
    nh3 = as.numeric(`NH3 column`)
  ) %>%
  filter(
    !is.na(nh3),
    nh3 > 0,                       # required for log scale
    lon >= -125, lon <= -66.5,
    lat >=  24,  lat <=  49.5
  )

q <- quantile(nh3_df$nh3, probs = c(0, .1, .25, .5, .75, .9, 1), na.rm = TRUE)
q


# -----------------------------
# Basemap
# -----------------------------
states <- map_data("state")


# -----------------------------
# Yellow → orange → red palette
# (matched to your density maps)
# -----------------------------
ylow_orange_red_NH3 <- c(
  "#fffffb",  # almost white (very low NH3)
  "#fffff0",
  "#ffffe5",
  "#fffbd1",
  "#fff7bc",
  "#ffeda0",  # mid yellow
  "#fed976",  # yellow-orange
  "#feb24c",  # light orange
  "#fd8d3c",  # orange
  "#f16913",  # deep orange
  "#d7301f"   # red (true hotspots)
)
scale_color_gradientn(
  colours = ylow_orange_red_NH3,
  trans   = "log10",
  values  = scales::rescale(log10(q)),
  breaks  = c(3e14, 1e15, 3e15, 1e16, 3e16),
  labels  = scales::label_scientific(),
  name    = expression(NH[3]~"column")
)


# -----------------------------
# Plot
# -----------------------------
plot_title <- "CONUS NH\u2083 Column"

p.nh3 <- ggplot() +
  geom_polygon(
    data = states,
    aes(long, lat, group = group),
    fill = NA,
    color = "black",
    linewidth = 0.3
  ) +
  geom_point(
    data = nh3_df,
    aes(lon, lat, color = nh3),
    size = 1.6,
    alpha = 0.8
  ) +
  coord_map("albers", lat0 = 45.5, lat1 = 29.5) +
  scale_color_gradientn(
    colours = ylow_orange_red_NH3,
    trans   = "log10",
    breaks  = c(3e14, 1e15, 3e15, 1e16),
    labels  = label_scientific(),
    name    = expression(NH[3]~"column")
  ) +
  guides(color = guide_colorbar(
    barheight = unit(55, "mm"),
    barwidth  = unit(10, "mm")
  )) +
  labs(title = plot_title) +
  theme_void() +
  theme(
    plot.title   = element_text(face = "bold"),
    legend.title = element_text(face = "bold"),
    legend.text  = element_text(size = 10)
  )

print(p.nh3)

