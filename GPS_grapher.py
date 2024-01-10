import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import requests

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = np.radians(lat_deg)
  n = 1 << zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
  return xtile, ytile

def num2deg(xtile, ytile, zoom):
  n = 1 << zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * ytile / n)))
  lat_deg = np.degrees(lat_rad)
  return lat_deg, lon_deg

def get_zoom_value(max_longitude, min_longitude):
    zoom_widths = []
    zoom_levels = []
    for i in range(21):
        zoom_widths.append(360*(0.5**(i+1)))
        zoom_levels.append(i)
    zoom_lookup = {zoom_widths[i]: zoom_levels[i] for i in range(len(zoom_widths))}
    zoom_level = zoom_lookup[min(zoom_widths, key=lambda x:abs(x-(max_longitude - min_longitude)))]
    return zoom_level

def find_all_coords(corner1, corner2):
    if abs(corner1[1]-corner2[1]) == 1:
        listofy = [corner1[0], corner2[0]]
        listofy.sort()
    else:
        listofcorner_y = [corner1[1], corner2[1]]
        listofy = listofcorner_y
        for i in range(1, abs(corner1[1]-corner2[1])):
            listofy.append((min(listofcorner_y)+(i)))
    if abs(corner1[0]-corner2[0]) == 1:
        listofx = [corner1[0], corner2[0]]
        listofx.sort()
    else:
        listofcorner_x = [corner1[0], corner2[0]]
        listofx = listofcorner_x
        for i in range(1, abs(corner1[0]-corner2[0])):
            listofx.append((min(listofcorner_x)+i))

    unique_combinations = []

    for i in range(len(listofx)):
        for j in range(len(listofy)):
            unique_combinations.append((listofx[i], listofy[j]))
    
    unique_combinations.sort()
    return unique_combinations

def generate_urls(corner1, corner2, zoom_value):    
    list_of_urls = []
    for i in range(len(find_all_coords(corner1, corner2))):
        list_of_urls.append("https://a.tile.openstreetmap.fr/osmfr/"+str(zoom_value)+"/"+str(find_all_coords(corner1, corner2)[i][0])+"/"+str(find_all_coords(corner1, corner2)[i][1])+".png")
    return list_of_urls

def download_tiles(urls_list):
    for i in range(len(urls_list)):
        image_url = urls_list[i]
        filename = str(str(urls_list[i].split("/")[5])+"x"+str(urls_list[i].split("/")[6]))
        folder_path = 'images'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, filename)

        r = requests.get(image_url)

        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(r.content)
        else:
            print(f'Error: {r.status_code} - {r.text}')

def boundingbox(unique_combinationss, zoom_value):
    unique_combinations = unique_combinationss
    unique_combinations.sort()  
    return ((num2deg(all_tiles[0][0], all_tiles[0][1], zoom_value)[1]), (num2deg((all_tiles[-1][0]+1), (all_tiles[-1][1]+1), zoom_value)[1]), (num2deg((max(all_tiles)[0]+1), (max(all_tiles)[1]+1), zoom_value)[0]), (num2deg(all_tiles[0][0], all_tiles[0][1], zoom_value)[0]))

def get_unique_tiles(unique_combinations):
    x_unique = []
    y_unique = []
    for i in range(len(unique_combinations)):
        x_unique.append(unique_combinations[i][0])
        y_unique.append(unique_combinations[i][1])
    y_unique = pd.Series(y_unique).drop_duplicates().tolist()
    x_unique = pd.Series(x_unique).drop_duplicates().tolist()
    return [x_unique, y_unique]

def stitch_tiles(x_and_y_tiles):
    for i in range(len(get_unique_tiles(x_and_y_tiles)[1])):
        image_paths = []
        for j in range(len(get_unique_tiles(x_and_y_tiles)[0])):
            image_paths.append("images/" + str((get_unique_tiles(x_and_y_tiles)[0])[j])+"x"+str((get_unique_tiles(x_and_y_tiles)[1])[i])+".png")
        first_image = plt.imread(image_paths[0])
        first_image = np.concatenate((first_image, plt.imread(image_paths[1])), axis=1)
        if i == 0:
            result_image = first_image
        else:
            result_image = np.concatenate((result_image, first_image), axis=0)
    return result_image

def data_corner_finder(data_df):
    return [(data_df["longitude"].min(), data_df["latitude"].max()), (data_df["longitude"].max(), data_df["latitude"].min())]

inputfile = input("Please enter the name of the coordinate file: ")
data = pd.read_csv(inputfile)

corner_1 = deg2num(data_corner_finder(data)[1][1], data_corner_finder(data)[1][0], get_zoom_value(data["longitude"].max(), data["longitude"].min()))
corner_2 = deg2num(data_corner_finder(data)[0][1], data_corner_finder(data)[0][0], get_zoom_value(data["longitude"].max(), data["longitude"].min()))

all_tiles = find_all_coords(corner_1, corner_2)
urls = generate_urls(corner_1, corner_2, get_zoom_value(data["longitude"].max(), data["longitude"].min()))
download_tiles(urls)
Bbox = boundingbox(all_tiles, get_zoom_value(data["longitude"].max(), data["longitude"].min()))

fig, ax=plt.subplots()

ax.scatter(data["longitude"], data["latitude"], zorder=1, alpha=0.2, c="b", s=10)

ax.set_title("")

ax.set_xlim(Bbox[0], Bbox[1])
ax.set_ylim(Bbox[2], Bbox[3])

ax.imshow(stitch_tiles(all_tiles), zorder=0, extent = Bbox, aspect="equal")
plt.show()
