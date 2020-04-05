CREATE TYPE "spatial_resolution" AS ENUM (
  'city',
  'province',
  'country'
);

CREATE TYPE "temporal_resolution" AS ENUM (
  'year',
  'month',
  'day'
);

CREATE TYPE "category" AS ENUM (
  'energy',
  'society',
  'geography',
  'economy',
  'infrastructure'
);


CREATE TABLE "city" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "province_id" INT,
  "country_id" INT
);

CREATE TABLE "province" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "country_id" INT
);

CREATE TABLE "country" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50)
);

CREATE TABLE "feature" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "unit" VARCHAR(20),
  "category" category
);

CREATE TABLE "data" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "feature_id" INT,
  "value" FLOAT,
  "city_id" INT,
  "province_id" INT,
  "country_id" INT,
  "spatial_resolution" spatial_resolution,
  "temporal_resolution" temporal_resolution,
  "date" DATE
);
