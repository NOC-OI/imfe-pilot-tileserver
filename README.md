
# TILE SERVER FOR HAIG FRAS DIGITAL TWIN PROJECT
This repository is a combination of two system:
1) Titiler: FastAPI application for dynamic tiling.
2) MBTiles: a python server for organizing mbtiles files from object stores

## Titiler
This repository is an edit of the original TiTiler repository. If you want to see information about the original repository, click on the links below.
-  *Documentation*: https://devseed.com/titiler/
-  *Source Code*: https://github.com/developmentseed/titiler

### Changes from the original package

#### dockerfiles >> Dockerfile.uvicorn
- Add requirements.txt installation
- Add copy of localhost ssl pem files
- Add ssl -certifile in uvicorn CMD for development

#### docker compose
- Change ports for titiler-uvicorn container
- Add env file

#### .ENV
- Create env file with HASH password for signed url encryption

#### src >> titiler >> core >> titiler >> core >> dependencies.pypi
- Change the DatasetPathParams method
- In this method, it was added a parameter called encoded. If this parameter is true, it will convert the url to the new signed url. It will use the HASH password in the ENV file and decrypt the url using Fernet.

#### src >> titiler >> core >> titiler >> core >> factory.py
- Change the line from `environment_dependency: Callable[..., Dict] = field(default=lambda: {})` to `environment_dependency: Callable[..., Dict] = field(default=lambda: {"CPL_VSIL_CURL_USE_HEAD":"NO"})`

### Installation
To install from PyPI and run:

```bash
git  clone  https://git.noc.ac.uk/ocean-informatics/imfepilot/tileserver.git
cd  titiler
pip  install  -U  pip
pip  install  -e  src/titiler/core  -e  src/titiler/extensions  -e  src/titiler/mosaic  -e  src/titiler/application
pip  install  -r  requirements.txt
```

### Generate SSL keys for localhost (optional)
Depending on your type of development environment, you may need to have SSL on your localhost.
First you need to install mkcert.

```bash
brew  install  mkcert
mkcert  -install
```

Then you have to generate the ssl certificates

```bash
mkcert  localhost
```

It will generate two files: `./localhost.pem` and `./localhost-key.pem`. You need to copy then to the root folder of your tileserver repository.

### Launch application locally
```bash
# Run locally without ssl
uvicorn  titiler.application.main:app  --reload
# Run locally with ssl
uvicorn  titiler.application.main:app  --reload  --ssl-certfile  ./localhost.pem  --ssl-keyfile  ./localhost-key.pem  --reload
```

### Docker
- Built and deploy the docker

```
docker-compose up -d --build titiler-uvicorn
```
---

## MBTiles

The MBTiles part of this repository is based on the `mbtiles-s3-server` repository, including part of this README file. If you want to see information about the `mbtiles-s3-server` package, click on the link below.
-  *Source Code*: https://github.com/uktrade/mbtiles-s3-server

### Instalation

Run the following commands in the terminal:

``` shell
pip  install  -r  requirements.txt
```

### Generate mbtiles data

If you want to generate MBTiles files, you need to install tippecanoe

``` shell
git  clone  https://github.com/mapbox/tippecanoe.git
cd  tippecanoe
make  -j
make  install
```

To generate a MBTiles files, you can run a simple command:

``` shell
tippecanoe  -zg  -o  data/out.mbtiles  --drop-densest-as-needed  data/in.geojson
```

You can see more information on [tippecanoe docs](https://github.com/mapbox/tippecanoe).

#### (Optional) Create another file with a page size of 65536 bytes (64KiB) using `VACUUM` or `VACUUM INTO`

```bash
sqlite3  my-map.mbtiles  "PRAGMA page_size=65536; VACUUM INTO 'mytiles-65536.mbtiles';"
```

While this step is optional, performance with default mbtiles files that have smaller page sizes can be horrible to the point of being unusable - loading of a single tile can take many seconds. Performance of this server is limited by the latency of calls to S3, and this step effectively reduces the number of calls to S3 per map tile.

Note both `VACUUM` and `VACUUM INTO` need disk space since they create another database which is approximately the size of the original file.


### Object Store Credentials

You will need to set the following environment variables related to the object store:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_ENDPOINT

You can also add these variables to the .ENV file.


### Upload mbtiles data to object store
 
To use your mbtiles data, you need to upload it to object store. One thing that is important to mention is that your object store need to have versioning enabled.

To update your mbtiles file to jasmin, please run the following codes:

``` shell
python src/upload_bucket  -i  input  -o  output  -b  bucket
```

You can try to test and update your files in a local object store. To do that, you can use MINIO. Please follow the steps below to use minio locally:

#### MINIO Object Store locally

To install minio, follow the steps below:
``` shell
wget  https://dl.min.io/server/minio/release/linux-amd64/minio_20230420175655.0.0_amd64.deb
sudo  dpkg  -i  minio_20230420175655.0.0_amd64.deb
```

To create a minio server to object store, please type the following command
``` shell
MINIO_ROOT_USER=admin  MINIO_ROOT_PASSWORD=password  minio  server  /mnt/data  --console-address  ":9001"
```

This command will create an object store. You can open it using the ip showed on your terminal. You need to use the password and user name that you entered in the command. It is important to mention that the port 9001 will be used to bucket admin and por 9000 will be use to upload and download files.

After running the command, you can upload the files to minio. To do that, you need to update the ENVIROMENT VARIABLES.

**IMPORTANT: Please make sure to enable versioning on your object store**

### Create a Server on your object store

First, Ensure to have a IAM user that has `s3:GetObject` and `s3:GetObjectVersion`. Also ensure the your object store has versioning enabled

Start this server, configured with the location of this object and credentials for this user - it's configured using environment variables. You can assign the tiles file any version you like, in this case, `1.0.0`.
```bash
PORT=8080  \
MBTILES__1__URL=https://my-bucket.s3.eu-west-2.amazonaws.com/mytiles-65536.mbtiles  \
MBTILES__1__MIN_ZOOM=0  \
MBTILES__1__MAX_ZOOM=14  \
MBTILES__1__IDENTIFIER=mytiles  \
MBTILES__1__VERSION=1.0.0  \
AWS_REGION=eu-west-2  \
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  \
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  \
HTTP_ACCESS_CONTROL_ALLOW_ORIGIN="*"  \
	python  -m  mbtiles_s3_server
```

You need to update the following variables with your object store information
- MBTILES__1__URL
- AWS_ACCESS_KEY_ID
- AWS_ACCESS_ACCESS_KEY

Done, your server will be running locally on port 8080.

### Test your server and mbtiles file

On your user-facing site, include HTML that loads these tiles from this server. We have an example below:

```html
<!DOCTYPE  html>
<html>
	<head>
		<meta  charset="utf-8">
		<title>Example map</title>
		<meta  name="viewport"  content="initial-scale=1,maximum-scale=1,user-		scalable=no">
		<link  rel="stylesheet"  href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
		integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
		crossorigin=""/>
		<script  src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
		integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
		crossorigin=""></script>
		<script  src="https://unpkg.com/leaflet.vectorgrid@latest/dist/Leaflet.VectorGrid.bundled.js"></script>
		<script  src="https://unpkg.com/leaflet.vectorgrid@latest/dist/Leaflet.VectorGrid.js"></script>
		<style>
		body, html, #map {margin: 0; padding: 0; height: 100%; width: 100%}
		</style>
	</head>
	<body>
		<div  id="map"></div>
		<script>
			const  mymap = L.map('map', { zoomControl:  false }).setView([50, -8], 4);
			L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
				attribution:  '© OpenStreetMap',
				maxZoom:  30,
			}).addTo(mymap);
			var  vectorTileOptions = {
				vectorTileLayerStyles: {
					// A plain set of L.Path options.
					landuse: {
						weight:  0,
						fillColor:  '#9bc2c4',
						fillOpacity:  1,
						fill:  true
					},
					// A function for styling features dynamically, depending on their
					// properties and the map's zoom level
					admin:  function(properties, zoom) {
						var  level = properties.admin_level;
						var  weight = 1;
						if (level == 2) {weight = 4;}
							return {
								weight:  weight,
								color:  '#cf52d3',
								dashArray:  '2, 6',
								fillOpacity:  1
							}
						},
					// A function for styling features dynamically, depending on their
					// properties, the map's zoom level, and the layer's geometry
					// dimension (point, line, polygon)
					water:  function(properties, zoom, geometryDimension) {
						if (geometryDimension === 1) { // point
							return ({
								radius:  5,
								color:  '#cf52d3',
							});
						}

						if (geometryDimension === 2) { // line
							return ({
								weight:  1,
								color:  '#cf52d3',
								dashArray:  '2, 6',
								fillOpacity:  1
							});
						}
						if (geometryDimension === 3) { // polygon
							return ({
								weight:  1,
									fillColor:  '#9bc2c4',
									fillOpacity:  1,
									fill:  true
								});
						}
					},

					// An 'icon' option means that a L.Icon will be used
					place: {
						icon:  new  L.Icon.Default()
					},
					road: []

				}
			};				  
			L.vectorGrid.protobuf('http://127.0.0.1:8080/v1/tiles/mytiles@1.0.0/{z}/{x}/{y}.mvt', {
				vectorTileOptions,
			}).addTo(mymap);
		</script>
	</body>
</html>
```

This HTML is included in this repository in [example.html](./example.html). A simple server can be started to view it by

```bash
python  -m  http.server  8081  --bind  127.0.0.1
````
and  going  to [http://localhost:8081/example.html](http://localhost:8081/example.html)


### RUN as a Docker Container

You  can  also  run  the  mbtiles  server  as  a  docker  image. First  you  need to add to .env  file some environmental  variables.  You  can  see  below  an  example  of  the  .env  file:
```
PORT=8000
MBTILES__1__URL=https://your-tenancy/bucket-name/bucket-folder/filename1.mbtiles
MBTILES__1__MIN_ZOOM=0
MBTILES__1__MAX_ZOOM=30
MBTILES__1__IDENTIFIER=mytiles1
MBTILES__1__VERSION=1.0.0
MBTILES__2__URL=https://your-tenancy/bucket-name/bucket-folder/filename2.mbtiles
MBTILES__2__MIN_ZOOM=0
MBTILES__2__MAX_ZOOM=30
MBTILES__2__IDENTIFIER=mytiles2
MBTILES__2__VERSION=1.0.0
AWS_REGION=eu-west-2
AWS_ACCESS_KEY_ID=aaaaaaaaaaaaaaaaaaaaaaaaaaa
AWS_SECRET_ACCESS_KEY=bbbbbbbbbbbbbbbbbbbbbbbbbb
HTTP_ACCESS_CONTROL_ALLOW_ORIGIN=*
```
If you want to add more layers to your mbtiles server, you need to add more "MBTILES__[NUMBER]__*" environmental variables to your .env file.

To  build and run the image,  run:
  
```
docker-compose up -d --build mbtiles
```

The  docker  image  is  configurated  the  show  the  files  on  the  port  8082  of  the  container (EXPOSE 8082  line  on  the  Dockerfile).
