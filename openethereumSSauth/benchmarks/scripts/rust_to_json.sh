#!/bin/bash


stats=`cat stats*`

stats="${stats/Summary/[}]"
stats="${stats//Summary/,}"
stats="${stats//\(/[}"
stats="${stats//\)/]}"
stats="${stats//, /,\\n}"
stats="${stats//sum/\"sum\"}"
stats="${stats//min/\"min\"}"
stats="${stats//max/\"max\"}"
stats="${stats//mean/\"mean\"}"
stats="${stats//median:/\"median\":}"
stats="${stats//var/\"var\"}"
stats="${stats//std_dev_pct:/\"std_dev_pct\":}"
stats="${stats//std_dev:/\"std_dev\":}"
stats="${stats//median_abs_dev_pct:/\"median_abs_dev_pct\":}"
stats="${stats//median_abs_dev:/\"median_abs_dev\":}"
stats="${stats//quartiles/\"quartiles\"}"
stats="${stats//iqr/\"iqr\"}"

echo -e $stats > stats.json
json-glib-validate stats.json
