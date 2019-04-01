#set -vx

## identify the focalized part of cleft constructions in Naija
## using tregex
## ref: https://yandex.github.io/dep_tregex/index.html

## 
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

# covert cleft: na PIDGIN we don grow wit
c="$FOCALIZED and .--> ($COPULA and -->. $REST)"
# overt cleft: na PIDGIN wey we don grow wit
o="$FOCALIZED and -->. $RELATIVE"
# double cleft: na PIDGIN na im we don grow wit
d="$FOCALIZED and .--> ($COPULA and -->. ($COPULA2 and -->. $FOCALIZED2))"
# pseudo-cleft: wetin we don grow wit na Pidgin
p="$FOCALIZED and .--> ($COPULA and .<-- $DISLOCATED and form /wetin/)"
# revserse pseudo-cleft: Pidgin na wetin we don grow wit
r="$FOCALIZED and form /wetin/ and .--> ($COPULA and .<-- $DISLOCATED)"

file=$1
args=$2

fileout=${file##*/}
fileout=${fileout%.*}

## echo $fileout

pats[1]="$c"
pats[2]="$o"
pats[3]="$d"
pats[4]="$p"
pats[5]="$r"

strs[1]='covert'
strs[2]='overt'
strs[3]='double'
strs[4]='pseudo'
strs[5]='reverse'

for i in 1 2 3 4 5
do
    echo "${strs[$i]}"
    if [[ $args == *"--html"* ]]; then
    ext='.html'
    else
    ext='.conll10'
    fi
    python -m 'dep_tregex' grep "${pats[$i]}" < "$file" --cpostag --limit 10000 --print $args > "$fileout"_"${strs[$i]}""$ext"
done
