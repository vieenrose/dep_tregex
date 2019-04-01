#!/bin/sh

# debug
#set -vx

## identify serial verbal constructions in Naija
## using tregex
## tregex's documentation: https://yandex.github.io/dep_tregex/index.html

## todo:
## 1. export these verbal arguments in list
## 2. highlight these arguments in the html graph

## Ps. add --html in the second argument switch to HTML output in graphs.

## notaitons
# "A .<-- B" : A has a child (B) to the left
# "A <--. B" : A has a head (B) to the right
# "A .--> B" : A has a head (B) to the left
# "A -->. B" : A has a child (B) to the right

V2='v2 deprel /compound:svc/'
c="v1 -->. $V2"

# error when no filename
if [ -z "$1" ]
  then
    echo "Please specify the filename of a CoNLL-U file"
    exit 1
fi

file=$1
args=$2

basename=${file##*/}
basename=${basename%.*}

pats[1]="$c"
strs[1]='svc'

for i in 1
do
    # determine file extension : CoNLL (tabules) / HTML (graphs)
    if [[ $args == *"--html"* ]]; then
    ext='.html'
    else
    ext='.conll10'
    fi
    fileout2="$basename"_"${strs[$i]}""$ext"
    echo "${strs[$i]} -> $fileout2"
    # return and insert sentence ID
    python -m 'dep_tregex' grep "${pats[$i]}" < "$file" --cpostag --limit 10000 --print $args > "$fileout2"
done
