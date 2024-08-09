////////////////// RECUPERATION DES DONNEES //////////////////////////////////////////////

https://github.com/inaturalist/inaturalist-open-data/tree/documentation

- Installer le client aws
pip3 install --upgrade awscli

- Télécharger les photos
aws s3 cp --no-sign-request s3://inaturalist-open-data/photos.csv.gz photos.csv.gz

- Télécharger les observations 
aws s3 cp --no-sign-request s3://inaturalist-open-data/observations.csv.gz observations.csv.gz

Garder les quality_grade = research (avec script python par exemple, pour avoir plutôt un fichier observation_research_only.csv)

- Télécharger les taxons 
aws s3 cp --no-sign-request s3://inaturalist-open-data/taxa.csv.gz taxa.csv.gz




////////////////// PASSAGE DANS UNE BASE DE DONNEES SQLITE //////////////////////////////////////////////

(Extrait et adapté de : https://forum.inaturalist.org/t/getting-the-inaturalist-aws-open-data-metadata-files-and-working-with-them-in-a-database/22135)

- Installation de SQLite :
sudo apt-get install sqlite3

- Création d'une nouvelle base de données : 
sqlite3 inat.db

- Création des tables : 
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

- Pour vérifier que tout va bien, regarder les tables :
.tables
- et le contenu :
.schema nom_table

- Mettre en place une importation de csv avec colonnes séparées par des tabulations
.mode tabs
.import taxa.csv taxa

- Vérifier le bon import des données
select * from taxa limit 10;

Importer les autres tables : (ou la version observations_research_only.csv le cas échéant)
.import observations.csv observations
.import photos.csv photos

Création d'indexes pour accélérer les requêtes 
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


Pour vérifier que tout a bien été créé : 
.indices

Le fichier de BD fait 44Go à la fin de tout ça ! (19/04/2022) (86Go au 12/01/2024 (74Go en research_only))


/////////////////////////////////////////////// LES REQUETES //////////////////////

- Pour télécharger une photo à l'adresse suivante, il faut une "photo_id" et une "extension": 
https://inaturalist-open-data.s3.amazonaws.com/photos/[photo_id]/medium.[extension]
 
 
- Récupérer le taxon_id d'un taxon à partir de son nom latin :  (ici Apis mellifera)
select taxon_id from Taxa where name='Apis mellifera';

# Recuperer toutes les infos associees a l'ordre 47792, en amerique du sud
.headers on
.mode csv
.output selected_pictures_megaloptera_latam.csv
SELECT o.taxon_id, p.photo_id, p.extension, p.observation_uuid, o.latitude, o.longitude
FROM observations o
INNER JOIN photos p ON p.observation_uuid = o.observation_uuid
WHERE o.taxon_id IN (
    SELECT DISTINCT t.taxon_id
    FROM taxa t
    INNER JOIN observations o ON t.taxon_id = o.taxon_id
    WHERE t.ancestry LIKE '%/48112/%'
)
AND o.latitude BETWEEN -52 AND 12
AND o.longitude BETWEEN -90 AND -37;
.output stdout

47822 : Diptera
47157 : Lepidoptera
47208 : Coleoptera
47201 : Hymenoptera
47651 : Orthoptera
47744 : Hemiptera
48112 : Mantodea
48763 : Neuroptera
62164 : Trichoptera
47198 : Phasmida (also cited as Phasmatodea)
47792 : Odonata
47864 : Megaloptera
