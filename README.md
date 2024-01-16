# GPS-Plotter
This script takes a .csv file of Longitude and Latitude coordinates and plots them on a map using the OpenStreetMaps API and Matplotlib, outputting an image with the route plotted.
## Usage
Place the .csv file of coordinates into the root folder, and run the script. The .csv file must have the headers "latitude" and "longitude". When prompted, enter the filename into the box and hit enter, an image should soon appear.

The script will create an "images" folder to store the downloaded OSM tiles in the root directory. It will create this folder if it does not exist, and then fill it with tiles.

## To Do
- Modify code to check if a tile is downloaded already before querying the API

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

[© OpenStreetMap contributors](https://www.openstreetmap.org/copyright)
