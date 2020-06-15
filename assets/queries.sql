SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi_idx.info_type_id=50 AND t.production_year<=2060
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi_idx.info_type_id=32 AND t.production_year<=1951
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id<=81 AND t.production_year>=2025
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>1 AND mi_idx.info_type_id=58 AND t.production_year<=2070
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id<=113 AND t.production_year<1999
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id=23 AND t.production_year<=2027
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi_idx.info_type_id<=96 AND t.production_year>=2098
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=2 AND mi_idx.info_type_id<71 AND t.production_year<=1933
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id<2 AND mi_idx.info_type_id<=92 AND t.production_year>=2062
SELECT COUNT(*) FROM movie_companies mc,movie_info_idx mi_idx,title t WHERE t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi_idx.info_type_id!=69 AND t.production_year<=1980
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mk.keyword_id!=160621 AND t.production_year>=2112
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mk.keyword_id>=61190 AND t.production_year!=2039
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mk.keyword_id!=50641 AND t.production_year!=2026
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mk.keyword_id=9750 AND t.production_year=2037
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mk.keyword_id=209880 AND t.production_year<=1888
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id>1 AND mk.keyword_id<=205232 AND t.production_year>=1961
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=2 AND mk.keyword_id=177718 AND t.production_year>=1953
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mk.keyword_id=198000 AND t.production_year>=1902
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mk.keyword_id>=2756 AND t.production_year!=1949
SELECT COUNT(*) FROM movie_companies mc,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mc.movie_id AND mc.company_type_id<2 AND mk.keyword_id>79663 AND t.production_year<=2080
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year>2100
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year>2006
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year!=2036
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year!=1891
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year>1921
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year!=2060
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year<1938
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year=1932
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year<1973
SELECT COUNT(*) FROM movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.production_year!=2042
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id<30 AND t.production_year<=1896
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id>74 AND t.production_year<2047
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id!=73 AND t.production_year<=2084
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id=91 AND t.production_year<=1948
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id>26 AND t.production_year!=2112
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id=65 AND t.production_year>=1994
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id>=8 AND t.production_year!=1890
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id<=109 AND t.production_year!=1904
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id<=44 AND t.production_year=2020
SELECT COUNT(*) FROM movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi_idx.movie_id AND mi_idx.info_type_id<=31 AND t.production_year=2048
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND t.production_year!=1957
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND t.production_year>1961
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=2 AND t.production_year<=2018
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND t.production_year<=1914
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=2 AND t.production_year>2020
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id>1 AND t.production_year>2053
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id>=2 AND t.production_year<2101
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=1 AND t.production_year<=1903
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND t.production_year=1961
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND t.production_year<=1981
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id>163283 AND t.kind_id>=4 AND t.production_year>1972
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id!=2715 AND t.kind_id>3 AND t.production_year<2017
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id!=114046 AND t.kind_id>7 AND t.production_year>1971
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id!=65244 AND t.kind_id<=6 AND t.production_year!=1942
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id<=223055 AND t.kind_id>=1 AND t.production_year>=2077
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id!=234569 AND t.kind_id<3 AND t.production_year!=1918
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id<218535 AND t.kind_id=5 AND t.production_year<2056
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id<=136080 AND t.kind_id<4 AND t.production_year=1921
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id>197910 AND t.kind_id=7 AND t.production_year<1908
SELECT COUNT(*) FROM cast_info ci,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND mk.keyword_id=157495 AND t.kind_id<=7 AND t.production_year<1975
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year>=2050
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year<=1962
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year>2004
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year=1980
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year=1964
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year>1911
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year!=1951
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year<=2019
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year!=2080
SELECT COUNT(*) FROM cast_info ci,title t WHERE t.id=ci.movie_id AND t.production_year>2020
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year<=2103 AND ci.role_id<8
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year>=1888 AND ci.role_id=8
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year=2026 AND ci.role_id<=8
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year=2059 AND ci.role_id<7
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year!=2107 AND ci.role_id>3
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year>2109 AND ci.role_id<=1
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year<1993 AND ci.role_id>8
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year<1958 AND ci.role_id>4
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year<2030 AND ci.role_id<2
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,title t WHERE t.id=ci.movie_id AND t.id=mc.movie_id AND t.production_year>2102 AND ci.role_id>3
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id<=2 AND mi.info_type_id=94 AND mi_idx.info_type_id>26 AND t.kind_id!=1 AND t.production_year!=2026
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>1 AND mi.info_type_id>75 AND mi_idx.info_type_id<42 AND t.kind_id>=8 AND t.production_year>1999
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=2 AND mi.info_type_id=52 AND mi_idx.info_type_id=42 AND t.kind_id!=7 AND t.production_year!=2065
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id=2 AND mi.info_type_id>3 AND mi_idx.info_type_id>88 AND t.kind_id<3 AND t.production_year!=2015
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id<2 AND mi.info_type_id>=84 AND mi_idx.info_type_id!=15 AND t.kind_id>=4 AND t.production_year=1941
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id!=2 AND mi.info_type_id!=51 AND mi_idx.info_type_id!=64 AND t.kind_id=4 AND t.production_year=2035
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=2 AND mi.info_type_id<=30 AND mi_idx.info_type_id<=40 AND t.kind_id!=4 AND t.production_year>=1923
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi.info_type_id=88 AND mi_idx.info_type_id>92 AND t.kind_id=4 AND t.production_year=2017
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>=1 AND mi.info_type_id!=84 AND mi_idx.info_type_id<81 AND t.kind_id>=7 AND t.production_year<=2108
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=mi.movie_id AND t.id=mc.movie_id AND t.id=mi_idx.movie_id AND mc.company_type_id>1 AND mi.info_type_id>63 AND mi_idx.info_type_id<=3 AND t.kind_id<=2 AND t.production_year<1949
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<7 AND mi_idx.info_type_id=49 AND t.kind_id=6 AND t.production_year>1992
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<=62 AND mi_idx.info_type_id>58 AND t.kind_id<3 AND t.production_year=1875
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<105 AND mi_idx.info_type_id>=85 AND t.kind_id>=1 AND t.production_year!=1917
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id!=58 AND mi_idx.info_type_id>=52 AND t.kind_id<=1 AND t.production_year<=1891
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id!=81 AND mi_idx.info_type_id<73 AND t.kind_id>1 AND t.production_year=1963
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id!=60 AND mi_idx.info_type_id!=36 AND t.kind_id=5 AND t.production_year!=1898
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id>=108 AND mi_idx.info_type_id!=33 AND t.kind_id>=3 AND t.production_year<1999
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id=77 AND mi_idx.info_type_id>=94 AND t.kind_id>7 AND t.production_year!=2036
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id>=41 AND mi_idx.info_type_id=4 AND t.kind_id!=3 AND t.production_year!=1959
SELECT COUNT(*) FROM movie_info mi,movie_info_idx mi_idx,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<=40 AND mi_idx.info_type_id!=70 AND t.kind_id!=5 AND t.production_year<1914
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mi.info_type_id!=89 AND mk.keyword_id<58307 AND t.production_year<2027
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mi.info_type_id<108 AND mk.keyword_id=160095 AND t.production_year<=2072
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id<=2 AND mi.info_type_id<109 AND mk.keyword_id>=213337 AND t.production_year>=1984
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id>1 AND mi.info_type_id>=42 AND mk.keyword_id!=42236 AND t.production_year>=2008
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=1 AND mi.info_type_id>=72 AND mk.keyword_id>130728 AND t.production_year<=1905
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=1 AND mi.info_type_id<74 AND mk.keyword_id!=213966 AND t.production_year=2088
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id>1 AND mi.info_type_id<41 AND mk.keyword_id>162779 AND t.production_year>=2057
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=2 AND mi.info_type_id!=35 AND mk.keyword_id>107304 AND t.production_year<=1913
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id!=2 AND mi.info_type_id>39 AND mk.keyword_id<2375 AND t.production_year>=1931
SELECT COUNT(*) FROM movie_companies mc,movie_info mi,movie_keyword mk,title t WHERE t.id=mk.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mc.company_type_id=2 AND mi.info_type_id<=55 AND mk.keyword_id<128547 AND t.production_year>=2008
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>178184
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>212410
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id<=227903
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id<109123
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>13226
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>=89588
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>196269
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id<=205782
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id<59426
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_keyword mk,title t WHERE t.id=ci.movie_id AND t.id=mk.movie_id AND t.id=mc.movie_id AND mk.keyword_id>=220337
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id=69 AND mi_idx.info_type_id!=19 AND t.production_year!=2068
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<=90 AND mi_idx.info_type_id!=46 AND t.production_year>1944
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<=62 AND mi_idx.info_type_id<=45 AND t.production_year<1948
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id>58 AND mi_idx.info_type_id=113 AND t.production_year>=1964
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id>=49 AND mi_idx.info_type_id>25 AND t.production_year<1906
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<101 AND mi_idx.info_type_id=43 AND t.production_year!=1920
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id!=1 AND mi_idx.info_type_id<100 AND t.production_year>2069
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id=74 AND mi_idx.info_type_id<8 AND t.production_year<1959
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id<=74 AND mi_idx.info_type_id!=17 AND t.production_year<1888
SELECT COUNT(*) FROM cast_info ci,movie_info mi,movie_info_idx mi_idx,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND mi.info_type_id>106 AND mi_idx.info_type_id>36 AND t.production_year<1890
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id<105 AND t.production_year=2004 AND ci.role_id=2
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id>87 AND t.production_year<2103 AND ci.role_id>6
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id!=62 AND t.production_year!=2055 AND ci.role_id<2
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id!=90 AND t.production_year>2028 AND ci.role_id=3
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id<46 AND t.production_year=2092 AND ci.role_id>=4
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id>62 AND t.production_year>1989 AND ci.role_id<=3
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id=35 AND t.production_year<1923 AND ci.role_id=1
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id>39 AND t.production_year<=2027 AND ci.role_id!=4
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id<=27 AND t.production_year<2001 AND ci.role_id>=4
SELECT COUNT(*) FROM cast_info ci,movie_companies mc,movie_info mi,title t WHERE t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mc.movie_id AND mi.info_type_id!=96 AND t.production_year>1897 AND ci.role_id>3
