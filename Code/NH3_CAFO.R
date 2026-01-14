library(readxl)
library(dplyr)
library(ggplot2)
library(maps)
library(scales)

# -----------------------------
# Read NH3 data
# -----------------------------
nh3_df <- read.csv("../Data/conus_nh3.csv") %>%
  transmute(
    lon = as.numeric(Longitude),
    lat = as.numeric(Latitude),
    nh3 = as.numeric(`NH3.column`)
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
# Hex map
# -----------------------------

p_nh3_hex <- ggplot(nh3_df, aes(lon, lat)) +
  stat_summary_hex(
    aes(z = nh3, fill = after_stat(value)),
    fun = median,
    bins = 50,   # adjust for coarser/finer hexes
    alpha = 1
  ) +
  geom_path(
    data = states,
    aes(long, lat, group = group),
    inherit.aes = FALSE,
    color = "black",
    linewidth = 0.3
  ) +
  coord_map("albers", lat0 = 45.5, lat1 = 29.5) +
  scale_fill_gradientn(
    colours = c(
      "#fffffb",
      "#fffff0",
      "#ffffe5",
      "#fff7bc",
      "#fec44f",
      "#fe9929",
      "#f16913",
      "#d7301f"
    ),
    # trans = scales::trans_new(
    #   "log1p10",
    #   transform = function(x) log10(x + 1),
    #   inverse   = function(x) (10^x) - 1
    # ),
    oob = scales::squish,
    breaks = scales::pretty_breaks(n = 5),
    # labels = function(x) {
    #   s <- formatC(x, format = "e", digits = 2)          # e.g. "1.00e+15"
    #   s <- gsub("e([+-]?)(\\d+)", " %*% 10^\\1\\2", s)   # -> "1.00 %*% 10^15"
    #   s <- gsub("\\^\\+", "^", s)                        # clean + sign
    #   parse(text = s)
    # },
    name = expression(paste("NH"[3], " Column")),
    guide = guide_colorbar(
      title.position = "top",
      title.hjust = 0.5,
      barheight = grid::unit(190, "pt"),
      ticks = TRUE
    )
  ) +
  labs(title = expression(paste("CONUS NH"[3], " Column"))) +
  theme_void() +
  theme(
    legend.key.height = grid::unit(18, "pt"),
    legend.text = element_text(size = 10),
    legend.title = element_text(size = 11),
    legend.box.margin = margin(0, 0, 0, 8)
  )

print(p_nh3_hex)

