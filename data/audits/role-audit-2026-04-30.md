# Role Audit for 2026-04-30

Reviewed every current row in the local `people` table against stored `article_people` context, article titles, and the retained `faculty_staff_directory` table.

## Summary

- People reviewed: 200
- Role corrections applied: 126
- Source of truth: local SQLite database at `data/hood_people.db`

## Role Counts Before And After

| Role | Before | After |
| --- | ---: | ---: |
| administrator | 3 | 13 |
| alumni | 17 | 39 |
| coach | 2 | 2 |
| faculty | 1 | 38 |
| guest | 0 | 18 |
| person | 107 | 0 |
| staff | 1 | 5 |
| student | 66 | 74 |
| student-athlete | 3 | 11 |

## Corrections Applied

| Name | Before | After | Local Evidence Basis |
| --- | --- | --- | --- |
| Aaron Angello | person | faculty | Official directory and article context identify an English professor/program director. |
| Amanda Ambrose | person | student | Local context says member of a Hood student research team and class year '26. |
| Amanda Dymek | person | staff | Local context says director of wellness at Hood. |
| Amber Samuels | person | faculty | Official directory lists graduate faculty; local story is a Graduate Faculty Focus. |
| Amrit Brown | person | student | Local context says current co-editor, class year '26. |
| Amy-Vaughan Roland | person | alumni | Local story gives Hood class year '06 and alumni framing. |
| Andrea Chapdelaine | person | administrator | Stored article says Hood president. |
| Andrew Campbell | person | faculty | Official directory/article context identify an assistant professor of counseling. |
| April Boulton | person | administrator | Official directory and article context identify associate provost/dean. |
| Autumn Smith | person | student | Graduate Assistant Focus says she is pursuing counseling education at Hood. |
| Bambi Volatile-Goebel | person | alumni | Local story gives Graduation Year 1988/Alumni. |
| Ben Foster | student | student-athlete | Athletics roster context lists swimmer event and class standing. |
| Betsy Moore | person | alumni | Alumni Teacher of the Year nominee list gives Hood degree year. |
| Brittney Cooper | person | guest | Hosted public talk / visiting author context. |
| Brooke Dawson | person | alumni | Alumni Teacher of the Year nominee list gives M.S.'23. |
| Brooke Witherow | person | faculty | Official directory lists assistant professor; promotion article names Hood faculty. |
| Cailyn Barthlow | person | alumni | Local context gives Hood class year '22. |
| Carol Jim | person | faculty | Official directory/promotion article identify a computer science professor. |
| Chris Stromberg | person | faculty | Directory fuzzy match Christopher J. Stromberg; stored article says Professor of Chemistry. |
| Christian Villarosa | student | staff | Local listing context identifies a graduate staff spotlight/staff entry. |
| Christine Mosere | person | guest | External artistic director for festival context. |
| Craig Laufer | person | faculty | Official directory and article context identify a Hood biology faculty member. |
| Craig Swagler | person | guest | External WYPR president/general manager in partner event context. |
| Daehwan Kim | person | faculty | Official directory/promotion article identify a Hood biology professor. |
| David Gurzick | person | faculty | Official directory lists professor of management; local article says taught by him. |
| Derek Miller | person | student | Hood story title/context gives class year '26. |
| Derrick Harrigan | person | alumni | Commencement speaker context gives Hood years '07 and MBA '14. |
| Diane Gallagher | person | alumni | Alumni nominee list gives Hood class year '95. |
| Dom Esposito | person | faculty | Graduate Faculty Spotlight and local context identify Hood faculty. |
| Dorian Young | person | alumni | Hood story gives class year '23 and post-Hood employment. |
| Drew Ferrier | person | faculty | Official directory and article context identify a Hood biology professor. |
| Elizabeth Atwood | person | faculty | Official directory lists associate professor of journalism. |
| Elizabeth Knapp | person | faculty | Directory fuzzy match Dorian Elizabeth Knapp; local context says professor of English. |
| Ella Hamilton | person | student | NSF research article identifies Hood student/class year '26. |
| Ethan Dmitrovsky | person | guest | External FNL/Leidos Biomedical president/director in symposium context. |
| Evelyn Nieves | person | faculty | Official directory and nursing article identify assistant professor of nursing. |
| Gayon Sampson | student | guest | External senior advisor to the mayor, not a student. |
| Hollis Caswell | person | faculty | Official directory and nursing article identify visiting assistant professor of nursing. |
| Isabel Malaga | person | student | Local context lists Hood college students including Isabel Malaga '26. |
| Janak Joshi | person | faculty | Official directory and article title identify economics professor. |
| Janet Fox | person | alumni | Alumni nominee list gives M.S.'04. |
| Jen Cinclair | person | alumni | Local story gives Hood class year '02. |
| Jennifer Cooper | person | faculty | Official directory and article context identify nursing faculty/chair. |
| Jennifer Cuddapah | person | faculty | Directory fuzzy match Jennifer Locraft Cuddapah; article says Hood faculty. |
| Jennifer Nelson | person | guest | External University of Delaware/Harvard Radcliffe scholar in event context. |
| Jenny Schlossberg | person | student | Local context lists Hood student Jenny Schlossberg '28. |
| Jevon Yarbrough | student | student-athlete | Athletics article identifies a Blazers basketball junior. |
| Jiang Li | person | faculty | Official directory/promotion article identify computer science faculty. |
| Jim Racheff | person | student | Doctoral Student Spotlight says he is a current doctoral student. |
| Joel White | student-athlete | staff | Athletics byline says Graduate Assistant, not student-athlete. |
| Jordan Banks | person | student | First-generation student quote uses class year '23 in student-day context. |
| Josephine Sasse | person | student | Local context says member of a Hood student research team/class year '25. |
| Jude Huseby | student | student-athlete | Athletics article identifies a Blazers basketball junior. |
| Julia Leclair | person | student | Local context lists student directors including Julia Leclair '26. |
| Kamryn Sohner | person | student-athlete | Ice hockey story identifies goaltender/class year '28. |
| Karen Cannon | person | guest | External Mobilize Frederick executive director in summit context. |
| Karen White | alumni | faculty | Local article says Hood alumna returned as an adjunct instructor. |
| Kathryn Hale | person | alumni | Alumni nominee list gives Hood years '04 and M.S.'13. |
| Katie Misuraca | person | alumni | Local media-career story gives Hood class year '16. |
| Kelly Schulz | person | alumni | Local context gives Hood class year '09. |
| Kimberly Morse-Jones | person | faculty | Directory fuzzy match Kimberly Morse Jones; promotion article identifies faculty. |
| Kristine Calo | person | faculty | Official directory and local context identify department chair/faculty. |
| Laura Catulle | person | faculty | Graduate Faculty Focus identifies Hood graduate faculty. |
| Leonard Freedman | person | guest | External FNL chief science officer in symposium context. |
| Lexie Page | person | student | First-generation student quote uses class year '25 in student-day context. |
| Linda Allan | person | alumni | Commencement context gives Hood years '70 and M.S.'78. |
| Lisa Littlefield | person | administrator | Local context says dean of career development and experiential learning. |
| Lori Warren-Ream | person | alumni | Alumni nominee list gives Hood years '17, M.S.'22, C'23. |
| Lucas Sasaki | person | alumni | Graduate spotlight context says recent graduate and Alumni tag. |
| Maggie Grijalva | person | student-athlete | Ice hockey story identifies goaltender/class year '28. |
| Maggie Ralston | person | student | Hood story title gives class year '26. |
| Mallory Huard | person | faculty | Official directory and local context identify assistant professor of history. |
| Marc Dupont | person | faculty | Official directory and local context identify assistant professor of marketing. |
| Marisel Torres-Crespo | person | faculty | Directory fuzzy match Marisel N. Torres-Crespo; promotion article identifies faculty. |
| Martha Church | person | administrator | Local context says Hood's seventh president. |
| Mary Carrington | person | guest | External FNL investigator in symposium context. |
| Mary Drexler | person | guest | External MCEPG director in grant-partner context. |
| Marylou Foley | person | administrator | Local context says appointed to Hood College Board of Trustees. |
| Matthew Gelhard | student-athlete | staff | Athletics byline says Assistant Director of Athletics for Communications. |
| Melissa Muntz | person | alumni | Local context gives Hood class year '12. |
| Michele Corr | person | guest | External Delaplaine Foundation executive director in grant context. |
| Mimi Bafor | person | student | Local context lists Hood college students including Mimi Bafor '26. |
| Mizuki Jones | person | student | NeighborHOOD Partners Scholarship story says pursuing M.S. at Hood. |
| Molly Moreland | person | faculty | Official directory/promotion article identify psychology faculty. |
| Nilah Magruder | person | alumni | Commencement speaker context gives Hood class year '05. |
| Nisha Manikoth | person | faculty | Official directory/promotion article identify organizational leadership faculty. |
| Paige Eager | person | administrator | Official directory and article context identify provost/vice president/dean. |
| Parker Neuenhaus | student | student-athlete | Athletics article identifies a basketball player/sophomore. |
| Patrick Morgan | person | alumni | Alumni nominee list gives Hood degree context. |
| Phil Bowers | student | alumni | Local story gives Hood class year '83. |
| Rachel Lamb | student | guest | External senior climate advisor, not student. |
| Rachel Miller | person | student | Scholarship Day quote gives class year '27. |
| Rana Khan | person | administrator | Local context says inaugural director of Hood biomedical research/training center. |
| Ravi Puli | person | guest | External IAMBIG co-founder in pitch competition context. |
| Rebecca Carroll | person | student | Chair of the Board Scholar story gives class year '25. |
| Reece Gall | person | student-athlete | Ice hockey story identifies scoring/goal context and class year '28. |
| Robert Putnam | person | guest | Visiting speaker/professor emeritus in lecture context. |
| Robin Fleming | person | guest | External Miss America's Scholarship Foundation representative. |
| Rona Mensah | person | alumni | Local story gives Hood class year '92 and media career. |
| Sabella Barron | person | student | Hood Students Support article gives class year '26. |
| Sam Pierre | alumni | student | Graduate Student Spotlight says current graduate student/GSA president. |
| Sangeeta Gupta | person | faculty | Official directory match and student research context identify psychology faculty mentor. |
| Shannon Kundey | student | faculty | Official directory and article context identify professor of psychology, not student. |
| Shannon Shoemaker | person | faculty | Official directory and program launch context identify counseling faculty. |
| Shea Fitzgerald | student | student-athlete | Athletics article identifies a basketball player/junior. |
| Sofia Montoya-Deck | person | student | Local context says current co-editor/class year '26 and study abroad story. |
| Sofie Ancona | person | student-athlete | Ice hockey story identifies top scorer/class year '28. |
| Sonia Bowie | person | staff | Local context says doctoral program assistant. |
| Sophia Routzahn | student | student-athlete | Athletics swim article identifies senior swimmer and medalist. |
| Stephanie Ware | person | alumni | Local story gives M.S.'07/Ed.D. alumni-style profile. |
| Sue Kolb | person | administrator | Stored article body says Director of Athletics. |
| Susan Ensel | student | faculty | Directory fuzzy match Susan M. Ensel; local context says professor of chemistry. |
| Susan Pickett | person | alumni | Alumni nominee list gives Hood degree context. |
| Suzanna Diaz | person | alumni | Alumni nominee list gives Hood years '06 and M.S.'15. |
| Tamelyn Tucker-Worgs | person | faculty | Local promotion/commencement context identifies associate professor of political science. |
| Tammi Simpson | person | administrator | Local context says vice president for community and inclusivity. |
| Tamsin Moore | person | student | Hood story title gives class year '28. |
| Thomas Finton | person | administrator | Local context says Board Chair. |
| Tianning Li | person | faculty | Official directory and Graduate Faculty Focus identify finance faculty. |
| Timothy Coffin | person | faculty | Directory fuzzy match Timothy P. Coffin; article title identifies professor. |
| Timothy Jacobsen | student | faculty | Local context says instructor of multimedia communications. |
| Torsten Heggman | student | guest | External Kent State researcher/mentor, not a Hood student. |
| Tyson Schritter | person | guest | External Colleges of Distinction chief operating officer. |
| William Stapp | staff | faculty | Official directory lists applied instructor/director of string ensemble. |
| Wilner Aguilar | person | student | Scholarship Day quote gives class year '26 and student financial-aid context. |
| Yemi Fagbohun | person | guest | External local artist/founder in community story context. |

## Reviewed People After Audit

| Name | Role | First Seen | Last Seen |
| --- | --- | --- | --- |
| Aahana Nigam | student | 2026-04-04 | 2026-04-04 |
| Aaron Angello | faculty | 2026-04-04 | 2026-04-08 |
| Adam Barnhart | student | 2026-04-28 | 2026-04-28 |
| Alan Goldenbach | faculty | 2026-04-04 | 2026-04-04 |
| Alicia Bishop | student | 2026-04-04 | 2026-04-04 |
| Alisa Gorham | student | 2026-04-04 | 2026-04-04 |
| Alyssa Moore | alumni | 2026-04-04 | 2026-04-04 |
| Amanda Ambrose | student | 2026-04-04 | 2026-04-04 |
| Amanda Dymek | staff | 2026-04-04 | 2026-04-04 |
| Amber Samuels | faculty | 2026-04-04 | 2026-04-04 |
| Amrit Brown | student | 2026-04-04 | 2026-04-04 |
| Amy-Vaughan Roland | alumni | 2026-04-04 | 2026-04-04 |
| Andrea Chapdelaine | administrator | 2026-04-09 | 2026-04-09 |
| Andrew Campbell | faculty | 2026-04-04 | 2026-04-04 |
| Angie Auldridge | student | 2026-04-04 | 2026-04-30 |
| April Boulton | administrator | 2026-04-04 | 2026-04-30 |
| Ashish Shrestha | student | 2026-04-25 | 2026-04-25 |
| Ashley Lancaster | alumni | 2026-04-04 | 2026-04-23 |
| Ashley Norris-Barthlow | alumni | 2026-04-04 | 2026-04-04 |
| Autumn Smith | student | 2026-04-04 | 2026-04-04 |
| Bambi Volatile-Goebel | alumni | 2026-04-04 | 2026-04-04 |
| Ben Foster | student-athlete | 2026-03-20 | 2026-03-20 |
| Betsy Moore | alumni | 2026-04-04 | 2026-04-04 |
| Brandon Green | alumni | 2026-04-04 | 2026-04-04 |
| Brittney Cooper | guest | 2026-04-04 | 2026-04-04 |
| Brooke Dawson | alumni | 2026-04-04 | 2026-04-04 |
| Brooke Witherow | faculty | 2026-04-08 | 2026-04-08 |
| Cailyn Barthlow | alumni | 2026-04-04 | 2026-04-04 |
| Calleigh Hoffman | student | 2026-04-04 | 2026-04-04 |
| Carol Jim | faculty | 2026-04-04 | 2026-04-04 |
| Casey Chamberlin | student | 2026-04-04 | 2026-04-04 |
| Cass Byers | student | 2026-04-04 | 2026-04-04 |
| Charlotte Fahlbush | student | 2026-04-04 | 2026-04-04 |
| Chris Stromberg | faculty | 2026-04-04 | 2026-04-04 |
| Christian Villarosa | staff | 2026-04-04 | 2026-04-28 |
| Christine Mosere | guest | 2026-04-04 | 2026-04-04 |
| Cory Watson | alumni | 2026-04-04 | 2026-04-04 |
| Craig Laufer | faculty | 2026-04-04 | 2026-04-04 |
| Craig Swagler | guest | 2026-04-04 | 2026-04-04 |
| Daehwan Kim | faculty | 2026-04-04 | 2026-04-04 |
| David Gurzick | faculty | 2026-04-04 | 2026-04-04 |
| Debbie Ricker | administrator | 2026-03-20 | 2026-04-30 |
| Derek Miller | student | 2026-04-04 | 2026-04-04 |
| Derrick Harrigan | alumni | 2026-03-20 | 2026-04-30 |
| Diane Gallagher | alumni | 2026-03-20 | 2026-03-20 |
| Dom Esposito | faculty | 2026-04-04 | 2026-04-04 |
| Dominic Bechtel | student | 2026-04-04 | 2026-04-04 |
| Dorian Young | alumni | 2026-04-04 | 2026-04-04 |
| Drew Ferrier | faculty | 2026-04-04 | 2026-04-04 |
| Elijah Matlock | student | 2026-04-04 | 2026-04-04 |
| Elizabeth Atwood | faculty | 2026-04-04 | 2026-04-04 |
| Elizabeth Knapp | faculty | 2026-04-04 | 2026-04-04 |
| Ella Hamilton | student | 2026-04-04 | 2026-04-04 |
| Ellie Cooper | student | 2026-04-04 | 2026-04-04 |
| Ethan Dmitrovsky | guest | 2026-04-04 | 2026-04-04 |
| Evelyn Nieves | faculty | 2026-04-04 | 2026-04-08 |
| Eyob Jigsa | student | 2026-04-04 | 2026-04-04 |
| Gabrielle Averill | student | 2026-04-04 | 2026-04-04 |
| Garrett Hitchens | student | 2026-04-04 | 2026-04-04 |
| Gayon Sampson | guest | 2026-04-04 | 2026-04-04 |
| Georgia Esipila | student | 2026-04-13 | 2026-04-13 |
| Hannah Furlow | student | 2026-04-04 | 2026-04-04 |
| Hannah Poole | student | 2026-04-04 | 2026-04-04 |
| Harriet Caesley | student | 2026-04-28 | 2026-04-28 |
| Hollis Caswell | faculty | 2026-04-04 | 2026-04-04 |
| Isabel Malaga | student | 2026-04-04 | 2026-04-04 |
| Izzy Peroni | student | 2026-04-04 | 2026-04-04 |
| Jack Marti | alumni | 2026-04-04 | 2026-04-04 |
| Janak Joshi | faculty | 2026-04-04 | 2026-04-04 |
| Janet Fox | alumni | 2026-03-20 | 2026-03-20 |
| Jared Wagner | coach | 2026-03-20 | 2026-03-20 |
| Jazzmyn Proctor | alumni | 2026-04-04 | 2026-04-04 |
| Jen Cinclair | alumni | 2026-04-04 | 2026-04-04 |
| Jennifer Cooper | faculty | 2026-04-04 | 2026-04-04 |
| Jennifer Cuddapah | faculty | 2026-04-04 | 2026-04-04 |
| Jennifer Nelson | guest | 2026-04-04 | 2026-04-04 |
| Jennifer Wenner | alumni | 2026-03-20 | 2026-03-20 |
| Jenny Schlossberg | student | 2026-04-04 | 2026-04-04 |
| Jevon Yarbrough | student-athlete | 2026-03-20 | 2026-03-20 |
| Jiang Li | faculty | 2026-04-04 | 2026-04-04 |
| Jim Racheff | student | 2026-04-04 | 2026-04-04 |
| Joel White | staff | 2026-03-20 | 2026-03-20 |
| Johnathan Alexander | student | 2026-04-04 | 2026-04-04 |
| Jordan Banks | student | 2026-04-09 | 2026-04-09 |
| Jordan Taylor | student | 2026-04-04 | 2026-04-04 |
| Josephine Sasse | student | 2026-04-04 | 2026-04-04 |
| Jude Huseby | student-athlete | 2026-03-20 | 2026-03-20 |
| Julia Leclair | student | 2026-04-04 | 2026-04-04 |
| Justin Hilty | student | 2026-04-04 | 2026-04-04 |
| Kadem Hodge | student | 2026-04-04 | 2026-04-04 |
| Kamryn Sohner | student-athlete | 2026-04-04 | 2026-04-04 |
| Karen Cannon | guest | 2026-04-04 | 2026-04-04 |
| Karen White | faculty | 2026-04-04 | 2026-04-04 |
| Kate Weir | student | 2026-04-30 | 2026-04-30 |
| Kathryn Hale | alumni | 2026-04-04 | 2026-04-04 |
| Katie Cheng | alumni | 2026-03-20 | 2026-03-20 |
| Katie Misuraca | alumni | 2026-04-04 | 2026-04-04 |
| Katy Svitak | student | 2026-04-04 | 2026-04-04 |
| Kayla Russell | student | 2026-04-04 | 2026-04-04 |
| Kelly Esposito | student | 2026-04-04 | 2026-04-04 |
| Kelly Schulz | alumni | 2026-03-20 | 2026-03-20 |
| Kendra Speicher | student | 2026-04-04 | 2026-04-04 |
| Kendra Speicher-Eisenstark | alumni | 2026-04-04 | 2026-04-04 |
| Khatija Nishat | student | 2026-04-04 | 2026-04-04 |
| Kimberly Morse-Jones | faculty | 2026-04-08 | 2026-04-08 |
| Kristine Calo | faculty | 2026-04-04 | 2026-04-04 |
| Krisztina Fabo | student | 2026-04-04 | 2026-04-04 |
| Kullen Robinson | student-athlete | 2026-03-20 | 2026-03-20 |
| Laura Brown | alumni | 2026-04-27 | 2026-04-28 |
| Laura Catulle | faculty | 2026-04-28 | 2026-04-28 |
| Laurie Ward | student | 2026-04-04 | 2026-04-04 |
| Leonard Freedman | guest | 2026-04-04 | 2026-04-04 |
| Levi White | student | 2026-04-04 | 2026-04-04 |
| Lexie Page | student | 2026-04-09 | 2026-04-09 |
| Linda Allan | alumni | 2026-04-04 | 2026-04-04 |
| Lisa Littlefield | administrator | 2026-04-04 | 2026-04-04 |
| Lori Duke | student | 2026-04-04 | 2026-04-04 |
| Lori Warren-Ream | alumni | 2026-04-04 | 2026-04-04 |
| Lucas Sasaki | alumni | 2026-04-04 | 2026-04-04 |
| Maddie Sheffield | student | 2026-04-04 | 2026-04-04 |
| Maggie Grijalva | student-athlete | 2026-04-04 | 2026-04-04 |
| Maggie Ralston | student | 2026-04-04 | 2026-04-04 |
| Mallory Huard | faculty | 2026-04-04 | 2026-04-04 |
| Marc Dupont | faculty | 2026-04-04 | 2026-04-04 |
| Marcy Taylor | alumni | 2026-04-04 | 2026-04-04 |
| Marguerite Heebner | alumni | 2026-04-04 | 2026-04-04 |
| Maria Guiza | student | 2026-04-04 | 2026-04-04 |
| Marisel Torres-Crespo | faculty | 2026-04-04 | 2026-04-04 |
| Mark Reinhardt | administrator | 2026-04-04 | 2026-04-04 |
| Martha Church | administrator | 2026-04-04 | 2026-04-04 |
| Mary Carrington | guest | 2026-04-04 | 2026-04-04 |
| Mary Drexler | guest | 2026-04-04 | 2026-04-04 |
| Marylou Foley | administrator | 2026-04-04 | 2026-04-04 |
| Matthew Gelhard | staff | 2026-03-20 | 2026-04-22 |
| Maya Aylor | student | 2026-04-04 | 2026-04-04 |
| Meagan Cooley | alumni | 2026-04-04 | 2026-04-04 |
| Meg Wilcox | student | 2026-04-28 | 2026-04-28 |
| Melissa Muntz | alumni | 2026-03-20 | 2026-03-20 |
| Michele Corr | guest | 2026-04-04 | 2026-04-04 |
| Mimi Bafor | student | 2026-04-04 | 2026-04-04 |
| Mizuki Jones | student | 2026-04-04 | 2026-04-04 |
| Molly Moreland | faculty | 2026-04-04 | 2026-04-04 |
| Nilah Magruder | alumni | 2026-03-20 | 2026-04-30 |
| Nisha Manikoth | faculty | 2026-04-08 | 2026-04-08 |
| Noah Turner | student | 2026-04-04 | 2026-04-04 |
| Nwamaka Ejiogu | student | 2026-04-04 | 2026-04-04 |
| Paige Eager | administrator | 2026-03-20 | 2026-04-30 |
| Parker Neuenhaus | student-athlete | 2026-03-20 | 2026-03-20 |
| Patrick Morgan | alumni | 2026-03-20 | 2026-03-20 |
| Peter Azorsa | alumni | 2026-04-04 | 2026-04-04 |
| Phebe Frost | student | 2026-04-09 | 2026-04-09 |
| Phil Bowers | alumni | 2026-04-04 | 2026-04-10 |
| Rachel Kucharski | student | 2026-04-04 | 2026-04-04 |
| Rachel Lamb | guest | 2026-04-04 | 2026-04-04 |
| Rachel Miller | student | 2026-04-04 | 2026-04-04 |
| Rana Khan | administrator | 2026-04-04 | 2026-04-04 |
| Ravi Puli | guest | 2026-04-04 | 2026-04-04 |
| Rebecca Carroll | student | 2026-04-04 | 2026-04-04 |
| Reece Gall | student-athlete | 2026-04-04 | 2026-04-04 |
| Riana Caldwell | student | 2026-04-04 | 2026-04-13 |
| Ridley Little | student | 2026-04-04 | 2026-04-04 |
| Robert Putnam | guest | 2026-04-04 | 2026-04-04 |
| Robin Draetta | student | 2026-04-04 | 2026-04-04 |
| Robin Fleming | guest | 2026-03-20 | 2026-03-20 |
| Ron Volpe | administrator | 2026-04-04 | 2026-04-30 |
| Rona Mensah | alumni | 2026-04-04 | 2026-04-04 |
| Rook Bartlett | student | 2026-04-04 | 2026-04-04 |
| Ryan Mee | coach | 2026-03-20 | 2026-03-20 |
| Sabella Barron | student | 2026-04-04 | 2026-04-04 |
| Sam Pierre | student | 2026-04-04 | 2026-04-04 |
| Sangeeta Gupta | faculty | 2026-04-04 | 2026-04-04 |
| Shannon Kundey | faculty | 2026-04-04 | 2026-04-04 |
| Shannon Shoemaker | faculty | 2026-04-04 | 2026-04-04 |
| Shea Fitzgerald | student-athlete | 2026-03-20 | 2026-03-20 |
| Shirley Gonzalez | student | 2026-04-04 | 2026-04-04 |
| Sidney Brinkman | student | 2026-04-13 | 2026-04-13 |
| Sofia Montoya-Deck | student | 2026-04-04 | 2026-04-04 |
| Sofie Ancona | student-athlete | 2026-04-04 | 2026-04-04 |
| Sonia Bowie | staff | 2026-03-20 | 2026-03-20 |
| Sophia Routzahn | student-athlete | 2026-04-22 | 2026-04-22 |
| Stephanie Ware | alumni | 2026-04-04 | 2026-04-04 |
| Sue Kolb | administrator | 2026-04-04 | 2026-04-04 |
| Susan Ensel | faculty | 2026-04-04 | 2026-04-04 |
| Susan Pickett | alumni | 2026-03-20 | 2026-03-20 |
| Suzanna Diaz | alumni | 2026-04-04 | 2026-04-04 |
| Tamelyn Tucker-Worgs | faculty | 2026-04-04 | 2026-04-04 |
| Tammi Simpson | administrator | 2026-04-04 | 2026-04-04 |
| Tamsin Moore | student | 2026-04-04 | 2026-04-04 |
| Terel Reid | student | 2026-04-04 | 2026-04-04 |
| Thomas Finton | administrator | 2026-04-04 | 2026-04-04 |
| Tianning Li | faculty | 2026-04-04 | 2026-04-04 |
| Timothy Coffin | faculty | 2026-04-04 | 2026-04-04 |
| Timothy Jacobsen | faculty | 2026-04-04 | 2026-04-04 |
| Torsten Heggman | guest | 2026-04-04 | 2026-04-04 |
| Tyson Schritter | guest | 2026-04-04 | 2026-04-04 |
| Venkata Krishna | student | 2026-04-04 | 2026-04-04 |
| William Stapp | faculty | 2026-04-04 | 2026-04-04 |
| Wilner Aguilar | student | 2026-04-04 | 2026-04-04 |
| Wylie Beland | student | 2026-04-04 | 2026-04-04 |
| Yemi Fagbohun | guest | 2026-04-04 | 2026-04-04 |
