INSERT INTO city (name, province_id, country_id)
SELECT 'Stuttgart', id FROM province WHERE name = 'Baden-Wuerttemberg', id FROM country WHERE name = 'Germany';

INSERT INTO city (name, province_id, country_id)
SELECT 'Muenchen', id FROM province WHERE name = 'Bayern', id FROM country WHERE name = 'Germany';
