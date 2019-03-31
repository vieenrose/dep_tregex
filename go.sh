set -vx

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
covert_cleft="$FOCALIZED and .--> ($COPULA and -->. $REST)"
# overt cleft: na PIDGIN wey we don grow wit
overt_cleft="$FOCALIZED and -->. $RELATIVE"
# double cleft: na PIDGIN na im we don grow wit
double_cleft="$FOCALIZED and .--> ($COPULA and -->. ($COPULA2 and -->. $FOCALIZED2))"
# pseudo-cleft: wetin we don grow wit na Pidgin
pseudo_cleft="$FOCALIZED and .--> ($COPULA and .<-- $DISLOCATED and form /wetin/)"
# revserse pseudo-cleft: Pidgin na wetin we don grow wit
reverse_pseudo_cleft="$FOCALIZED and form /wetin/ and .--> ($COPULA and .<-- $DISLOCATED)"

pattern=$double_cleft
file='test2'
python -m 'dep_tregex' grep "$pattern" < $file --html --cpostag
