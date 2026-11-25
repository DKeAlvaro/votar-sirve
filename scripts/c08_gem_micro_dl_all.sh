#!/bin/sh
# downloads main APS individual-level file for each year 2001-2022 (ids from data/raw/c08/gem_individual_ids.txt)
cd "$(dirname "$0")/.."
for p in 2022:51376 2020:50903 2019:50676 2018:50444 2017:50215 2016:50016 2015:49815 2014:49485 2013:50442 2012:48791 2011:48542 2010:48787 2009:48785 2008:48784 2007:48783 2006:48782 2005:48781 2004:48780 2003:48779 2002:48778 2001:48777; do
  y=${p%%:*}; i=${p##*:}
  [ -s data/raw/c08/gem_micro/gem${y}_ind.zip ] || python -I scripts/c08_gem_micro_dl.py $i data/raw/c08/gem_micro/gem${y}_ind.zip
done
echo done
