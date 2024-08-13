# Download images

We downloaded our images from [iNaturalist](https://www.inaturalist.org/) which is an opensourced biodiversity images database.

We needed a lot of specific images to train our model. Here is the flow to follow to efficiently download thousands of images with filters.

## Get the data

Install the AWS client
```
pip3 install --upgrade awscli
```

Download the photos
```
aws s3 cp --no-sign-request s3://inaturalist-open-data/photos.csv.gz photos.csv.gz
```

Download the observations
```
aws s3 cp --no-sign-request s3://inaturalist-open-data/observations.csv.gz observations.csv.gz
```

Download the taxa
```
aws s3 cp --no-sign-request s3://inaturalist-open-data/taxa.csv.gz taxa.csv.gz
```

If you want to only keep observations that have been research graded, use ```keep_only_research.py```. This will ensure that the label of the image is correct.

More information on this procedure can be found [here](https://github.com/inaturalist/inaturalist-open-data/tree/documentation).



## Create database

Since there are million of observation on iNaturalist, we need to create a database to query the previously downloaded csv. In our case, we used SQLite.

Install SQLite and create new database
```
sudo apt-get install sqlite3
sqlite3 inat.db
```

Create tables
```SQL
CREATE TABLE observations (
    observation_uuid uuid NOT NULL,
    observer_id integer,
    latitude numeric(15,10),
    longitude numeric(15,10),
    positional_accuracy integer,
    taxon_id integer,
    quality_grade character varying(255),
    observed_on date
);

CREATE TABLE photos (
    photo_uuid uuid NOT NULL,
    photo_id integer NOT NULL,
    observation_uuid uuid NOT NULL,
    observer_id integer,
    extension character varying(5),
    license character varying(255),
    width smallint,
    height smallint,
    position smallint
);

CREATE TABLE taxa (
    taxon_id integer NOT NULL,
    ancestry character varying(255),
    rank_level double precision,
    rank character varying(255),
    name character varying(255),
    active boolean
);

CREATE TABLE observers (
    observer_id integer NOT NULL,
    login character varying(255),
    name character varying(255)
);
```

Verify that everything works
```SQL
.tables
.schema table_name
```

Set up a CSV import with columns separated by tabs.
```SQL
.mode tabs
.import taxa.csv taxa
```

Verify that everything works
```SQL
select * from taxa limit 10;
```
Import other tables
```SQL
.import observations_research_only.csv observations
.import photos.csv photos
```
Create indexes to speed up queries
```SQL
CREATE UNIQUE INDEX "idx_observations_observation_uuid" ON "observations" ("observation_uuid");
CREATE INDEX "idx_observations_observer_id" ON "observations" ("observer_id");
CREATE INDEX "idx_observations_taxon_id" ON "observations" ("taxon_id");
CREATE INDEX "idx_observations_quality_grade" ON "observations" ("quality_grade");
CREATE INDEX "idx_observations_observed_on" ON "observations" ("observed_on");
CREATE INDEX "idx_observations_longitude" ON "observations" ("longitude");
CREATE INDEX "idx_observations_latitude" ON "observations" ("latitude");

CREATE INDEX "idx_photos_photo_uuid" ON "photos" ("photo_uuid");
CREATE INDEX "idx_photos_observation_uuid" ON "photos" ("observation_uuid");
CREATE INDEX "idx_photos_photo_id" ON "photos" ("photo_id");
CREATE INDEX "idx_photos_observer_id" ON "photos" ("observer_id");
CREATE INDEX "idx_photos_license" ON "photos" ("license");

CREATE UNIQUE INDEX "idx_taxa_taxon_id" ON "taxa" ("taxon_id");
CREATE INDEX "idx_taxa_name" ON "taxa" ("name");
CREATE INDEX "idx_taxa_rank" ON "taxa" ("rank");
CREATE INDEX "idx_taxa_rank_level" ON "taxa" ("rank_level");
CREATE INDEX "idx_taxa_ancestry" ON "taxa" ("ancestry");
```

Verify that everything has been correctly setup
```SQL
.indices
```




## Queries

To download a photo, you need ```photo_id``` and ```extension```. Then, go to this url : https://inaturalist-open-data.s3.amazonaws.com/photos/[photo_id]/medium.[extension]

First, let's get the ```taxon_id``` from the orders that we want.
```SQL
select taxon_id from Taxa where name='order_name';
```

Once we have those, we can query all the information we need. In our case, we added a filter to only get observations that occured in Latin America.
```SQL
.headers on
.mode csv
.output selected_pictures_ordername_latam.csv
SELECT o.taxon_id, p.photo_id, p.extension, p.observation_uuid, o.latitude, o.longitude
FROM observations o
INNER JOIN photos p ON p.observation_uuid = o.observation_uuid
WHERE o.taxon_id IN (
    SELECT DISTINCT t.taxon_id
    FROM taxa t
    INNER JOIN observations o ON t.taxon_id = o.taxon_id
    WHERE t.ancestry LIKE '%/[enter here the taxon_id]/%'
)
AND o.latitude BETWEEN -52 AND 12
AND o.longitude BETWEEN -90 AND -37;
.output stdout
```

This query creates a csv file containing all the information. In our case, these were the ```taxon_id``` we were interested in :
- 47822 : Diptera
- 47157 : Lepidoptera
- 47208 : Coleoptera
- 47201 : Hymenoptera
- 47651 : Orthoptera
- 47744 : Hemiptera
- 48112 : Mantodea
- 48763 : Neuroptera
- 62164 : Trichoptera
- 47198 : Phasmida
- 47792 : Odonata
- 47864 : Megaloptera



## Create a raw dataset

First, we need to filter the csv files. Since we only need a small fraction of the available images, we won't lose time downloading everything. ```filter_csv.py``` creates a folder containing csv files with ~ 1500 images per order.


Then, we can download the images. ```download_photos.py``` will download all the images referenced in the filtered csv files and organize those in folders named after the order's name.


Last thing to do, split the downloaded images between train, val and test folders : ```split_dataset.py```



## Visualize the data

```visualize_dataset.py``` shows you the number of images per class, per folder.

```visualize_data.py``` creates a map pointing to the location where all the observations occured.