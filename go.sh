set -vx


# "A .<-- B" : A have a child (B) in the left
# "A <--. B" : A have a head (B) in the left
# "A .--> B" : A have a head (B) in the right
# "A -->. B" : A have a child (B) in the right

# covert cleft: na PIDGIN we don grow wit
covert_cleft='x form /na/ and cpostag /PART/ and -->. t deprel /comp:cleft/ and -->. f deprel /comp:pred/'

# overt cleft: na PIDGIN wey we don grow wit
overt_cleft='x form /na/ and cpostag /PART/ and -->. f deprel /comp:pred/ and -->. w form /wey/ and cpostag /SCONJ/ and deprel /dep/'

# double cleft: na PIDGIN na im we don grow wit
double_cleft='x form /na/ and cpostag /PART/ and -->. y form /na/ and deprel /comp:cleft/ and cpostag /PART/ and -->. f2 form /im/ and deprel /comp:pred/ and cpostag /PRON/'

# pseudo-cleft: wetin we don grow wit na Pidgin
pseudo_cleft='x form /na/ and cpostag /PART/ and -->. f deprel /comp:pred/ and .<-- t deprel /dislocated/ and form /wetin/'

# revserse pseudo-cleft: Pidgin na wetin we don grow wit
reverse_pseudo_cleft='x form /na/ and cpostag /PART/ and -->. f deprel /comp:pred/ and form /wetin/ and .<-- t deprel /dislocated/'


pattern=$double_cleft
file='test2'
python -m 'dep_tregex' grep "$pattern" < $file --html
