# Cargar las bibliotecas necesarias
library(sf)
library(spdep)
library(ggplot2)
library(dplyr)

url <- "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/spain-provinces.geojson" 
provinces <- st_read(url)

data <- read.csv("D:/Desktop/TFG/data.csv")

data_sf <- st_as_sf(data, coords = c("longitude", "latitude"), crs = 4326)

data_sf <- st_transform(data_sf, crs =3035)

nb <- dnearneigh(st_coordinates(data_sf), 0, 100000)
listw <- nb2listw(nb, style = "B", zero.policy = TRUE)

gi_star <- localG(data_sf$test_value, listw)

data_sf <- st_transform(data_sf, st_crs(provinces))

data_sf$gi_star <- as.numeric(gi_star)

ggplot() +
  geom_sf(data = provinces, fill = "white", color = "black") +
  geom_sf(data = data_sf, aes(color = gi_star), size = 2) +
  scale_color_gradient2(midpoint = 0, low = "blue", mid = "white", high = "red", space = "Lab",
                        na.value = "grey50", guide = "colourbar") +
  theme_minimal() +
  ggtitle("Mapa de Calor - Índice Getis-Ord Gi* por Provincias en España") +
  theme(plot.title = element_text(hjust = 0.5))
