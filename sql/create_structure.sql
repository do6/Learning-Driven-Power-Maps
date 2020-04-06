---- "learning driven power maps"
--- create structure for database

-- new types
CREATE TYPE "spatial_resolution" AS ENUM (
  'city',
  'province',
  'country'
);

CREATE TYPE "temporal_resolution" AS ENUM (
  'day',
  'month',
  'year'
);

CREATE TYPE "category" AS ENUM (
  'energy',
  'geography',
  'society',
  'economy'
);

-- spatial information tables
CREATE TABLE "country" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50)
);

CREATE TABLE "province" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "country_id" BIGINT REFERENCES country (id)
);

CREATE TABLE "city" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "province_id" BIGINT REFERENCES province (id),
  "country_id" BIGINT REFERENCES country (id)
);

-- feature and data
CREATE TABLE "feature" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "name" VARCHAR(50),
  "unit" VARCHAR(20),
  "category" category
);

CREATE TABLE "data" (
  "id" BIGSERIAL NOT NULL PRIMARY KEY,
  "feature_id" BIGINT REFERENCES feature (id),
  "value" DOUBLE PRECISION,
  "city_id" BIGINT REFERENCES city (id),
  "province_id" BIGINT REFERENCES province (id),
  "country_id" BIGINT REFERENCES country (id),
  "spatial_resolution" spatial_resolution,
  "temporal_resolution" temporal_resolution,
  "date" DATE
);