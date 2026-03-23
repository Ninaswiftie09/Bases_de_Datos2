-- acá van todas las consultas SQL que se harán a la base de datos.

-- PARTE 1 - CREACION DE NODOS
-- Creacion de artistas
CREATE
(taylor:Artist {name: 'Taylor Swift', country: 'USA', debutYear: 2006, mainGenre: 'Pop', era: '2010s'}),
(ed:Artist {name: 'Ed Sheeran', country: 'UK', debutYear: 2011, mainGenre: 'Pop', era: '2010s'}),
(harry:Artist {name: 'Harry Styles', country: 'UK', debutYear: 2017, mainGenre: 'Pop', era: '2020s'}),
(olivia:Artist {name: 'Olivia Rodrigo', country: 'USA', debutYear: 2021, mainGenre: 'Indie Pop', era: '2020s'}),
(sabrina:Artist {name: 'Sabrina Carpenter', country: 'USA', debutYear: 2015, mainGenre: 'Pop', era: '2020s'})

-- Creacion de albumes
CREATE
(a1989:Album {title: '1989', releaseYear: 2014, type: 'Studio', totalTracks: 13}),
(divide:Album {title: 'Divide', releaseYear: 2017, type: 'Studio', totalTracks: 16}),
(sour:Album {title: 'SOUR', releaseYear: 2021, type: 'Studio', totalTracks: 11}),
(house:Album {title: "Harry's House", releaseYear: 2022, type: 'Studio', totalTracks: 13}),
(shortsweet:Album {title: "Short n' Sweet", releaseYear: 2024, type: 'Studio', totalTracks: 12})

-- Creacion de canciones
CREATE
(blank:Song {title: 'Blank Space', releaseYear: 2014, durationSec: 231, language: 'English', popularity: 'High'}),
(shape:Song {title: 'Shape of You', releaseYear: 2017, durationSec: 233, language: 'English', popularity: 'High'}),
(drivers:Song {title: 'drivers license', releaseYear: 2021, durationSec: 242, language: 'English', popularity: 'High'}),
(asit:Song {title: 'As It Was', releaseYear: 2022, durationSec: 167, language: 'English', popularity: 'High'}),
(espresso:Song {title: 'Espresso', releaseYear: 2024, durationSec: 175, language: 'English', popularity: 'High'})

-- Creacion de generos
CREATE
(pop:Genre {name: 'Pop', originDecade: '1950s', mood: 'Energetic', instrument: 'Synth', scope: 'Global'}),
(country:Genre {name: 'Country Pop', originDecade: '1980s', mood: 'Warm', instrument: 'Guitar', scope: 'Global'}),
(indie:Genre {name: 'Indie Pop', originDecade: '2000s', mood: 'Emotional', instrument: 'Guitar', scope: 'Global'}),
(synth:Genre {name: 'Synth-pop', originDecade: '1970s', mood: 'Electronic', instrument: 'Synthesizer', scope: 'Global'}),
(folk:Genre {name: 'Folk pop', originDecade: '1960s', mood: 'Soft', instrument: 'Acoustic Guitar', scope: 'Global'})


-- PARTE 2 - CREACION DE RELACIONES
MATCH (a:Artist {name: 'Taylor Swift'}), (g:Genre {name: 'Pop'})
CREATE (a)-[:BELONGS_TO]->(g);

MATCH (a:Artist {name: 'Taylor Swift'}), (g:Genre {name: 'Country Pop'})
CREATE (a)-[:BELONGS_TO]->(g);

MATCH (a:Artist {name: 'Taylor Swift'}),
      (b1:Artist {name: 'Ed Sheeran'}),
      (b2:Artist {name: 'Sabrina Carpenter'}),
      (s:Song {title: 'Blank Space'}),
      (al:Album {title: '1989'})
CREATE
(a)-[:SIMILAR_TO]->(b1),
(a)-[:SIMILAR_TO]->(b2),
(a)-[:PERFORMS]->(s),
(a)-[:RELEASED]->(al);

MATCH (a:Artist {name: 'Ed Sheeran'}),
      (g:Genre {name: 'Folk Pop'}),
      (b1:Artist {name: 'Taylor Swift'}),
      (s:Song {title: 'Shape of You'}),
      (al:Album {title: 'Divide'})
CREATE
(a)-[:BELONGS_TO]->(g),
(a)-[:SIMILAR_TO]->(b1),
(a)-[:PERFORMS]->(s),
(a)-[:RELEASED]->(al);

MATCH (a:Artist {name: 'Harry Styles'}),
      (g:Genre {name: 'Synth-pop'}),
      (b1:Artist {name: 'Olivia Rodrigo'}),
      (s:Song {title: 'As It Was'}),
      (al:Album {title: "Harry's House"})
CREATE
(a)-[:BELONGS_TO]->(g),
(a)-[:SIMILAR_TO]->(b1),
(a)-[:PERFORMS]->(s),
(a)-[:RELEASED]->(al);

MATCH (a:Artist {name: 'Olivia Rodrigo'}),
      (g:Genre {name: 'Indie Pop'}),
      (b1:Artist {name: 'Harry Styles'}),
      (b2:Artist {name: 'Sabrina Carpenter'}),
      (s:Song {title: 'drivers license'}),
      (al:Album {title: 'SOUR'})
CREATE
(a)-[:BELONGS_TO]->(g),
(a)-[:SIMILAR_TO]->(b1),
(a)-[:SIMILAR_TO]->(b2),
(a)-[:PERFORMS]->(s),
(a)-[:RELEASED]->(al);

MATCH (a:Artist {name: 'Sabrina Carpenter'}),
      (g:Genre {name: 'Pop'}),
      (b1:Artist {name: 'Olivia Rodrigo'}),
      (b2:Artist {name: 'Taylor Swift'}),
      (s:Song {title: 'Espresso'}),
      (al:Album {title: "Short n' Sweet"})
CREATE
(a)-[:BELONGS_TO]->(g),
(a)-[:SIMILAR_TO]->(b1),
(a)-[:SIMILAR_TO]->(b2),
(a)-[:PERFORMS]->(s),
(a)-[:RELEASED]->(al);


-- PARTE 3 - ADICION DE LABELS
MATCH (a:Artist {country: 'UK'})
SET a:British;

MATCH (a:Artist {country: 'USA'})
SET a:American;

MATCH (s:Song {popularity: 'High'})
SET s:Hit;