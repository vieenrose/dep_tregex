#!/bin/sh

# debug
#set -vx

## identify the focalized part of cleft constructions in Naija using tregex
## tregex's documentation: https://yandex.github.io/dep_tregex/index.html

## by default, for each type of cleft, the matched sentences are exported
## in a indiviual files in CoNLL-U format (tables).
## Ps. add --html in the second argument switch to HTML output in graphs.

## notaitons
# "A .<-- B" : A has a child (B) to the left
# "A <--. B" : A has a head (B) to the right
# "A .--> B" : A has a head (B) to the left
# "A -->. B" : A has a child (B) to the right

COPULA='x form /na/ and cpostag /PART/'
COPULA2='y form /na/ and cpostag /PART/ and deprel /comp:cleft/'
FOCALIZED='f deprel /comp:pred/'
FOCALIZED2='f2 deprel /comp:pred/ and form /im/'
REST='t deprel /comp:cleft/'
RELATIVE='w form /wey/ and cpostag /SCONJ/ and deprel /dep/'
DISLOCATED='d deprel /dislocated/'

# covert and overt cleft (see sub-types in the below)
co="$FOCALIZED and .--> ($COPULA and -->. $REST)"

# double cleft: na PIDGIN na im we don grow wit
d="$FOCALIZED and .--> ($COPULA and -->. ($COPULA2 and -->. $FOCALIZED2))"
# overt cleft: na PIDGIN wey we don grow wit
o="$co;$FOCALIZED and -->. ($RELATIVE)"

# pseudo-cleft: wetin we don grow wit na Pidgin (tofix : attributive constructions are not excluded)
p="$FOCALIZED and .--> ($COPULA and .<-- $DISLOCATED and form /wetin/)"
# revserse pseudo-cleft: Pidgin na wetin we don grow wit
r="$FOCALIZED and form /wetin/ and .--> ($COPULA and .<-- $DISLOCATED)"

# covert cleft: na PIDGIN we don grow wit
# positive pattern = co
# negative pattern = o

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

#pats[1]="$c"
pats[2]="$o"
pats[3]="$d"
pats[4]="$p"
pats[5]="$r"

#strs[1]='covert'
strs[2]='overt'
strs[3]='double'
strs[4]='pseudo'
strs[5]='reverse'

# covert celft : co - o
if [[ $args == *"--html"* ]]; then
ext='.html'
else
ext='.conll10'
fi
fileout2="$basename"_"covert""$ext"
echo "covert -> $fileout2"
# return and insert sentence ID
python -m 'dep_tregex' grep "$co" < "$file" -np "$o" --cpostag --limit 10000 --print $args > "$fileout2"


#other clefts
for i in 2 3 4 5
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
