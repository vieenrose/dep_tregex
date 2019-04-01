from dep_tregex.tree import Tree
import re

def _valid(text, empty_allowed=False):
    """
    Return whether field in a tree (FORM, LEMMA, etc.) can be written to
    a CoNLL file.
    """

    # Whitespace is not allowed inside strings.
    #for c in u'\t\n ':
    for c in u'\t\n':
        if c in text:
            return False

    # Required field must not be empty.
    if not empty_allowed and not text:
        return False

    # Can't encode underscores: underscore means 'empty' in CoNLL format.
    if empty_allowed and text == u'_':
        return False

    return True

def read_trees_conll(filename_or_file, errors='strict'):
    """
    Read trees from CoNLL file and yield them one-by-one.

    filename_or_file: str or file object, where to read trees from.
    errors: how to handle unicode decode errors.
    """

    node = 1
    forms, lemmas, cpostags, postags, feats, heads, deprels, miscs, sent_id = \
        [], [], [], [], [], [], [], [], ''

    # Determine whether we have a filename or a file object.
    # If we have a filename, get a file object.
    file = filename_or_file
    if isinstance(file, str):
        file = open(file, rt)

    for line_no, line in enumerate(file):
        try:
            line = line.decode('utf-8', errors).strip(u'\n')

            # On empty line, yield the tree (if the tree is not empty).
            if not line:
                if forms:
                    try:
                        tree = Tree(
                        forms, lemmas, cpostags, postags, feats, heads, deprels, miscs, sent_id)
                        yield tree
                    except:
                        #print('error: try to yield a bad conncted tree ({}) !'.format(sent_id))
                        continue # just skip bad tree

                    node = 1
                    forms, lemmas, cpostags, postags, feats, heads, deprels, miscs = \
                        [], [], [], [], [], [], [], []
                continue

            # Split the line and check the format.
            parts = line.split(u'\t')
            if len(parts) != 10:
                try:
                    sent_id = re.match(u'.*sent_id\s*=\s*([^\n]*)', line).group(1)
                except:
                    pass

                continue

	    """
            for i, part in enumerate(parts):
                if part:
                    continue
                msg = 'field %i: empty'
                raise ValueError(msg % i)
            """
            # Parse the fields.
            node += 1
            if not parts[1]:
                parts[1] = u'_'
            form = parts[1]
            if not parts[2]:
                parts[2] = form
            lemma = parts[2]
            cpostag = parts[3]
            postag = parts[4]
            feat = parts[5].split(u'|')
            if parts[6] == u'_':
                head = 0
            else:
                head = int(parts[6])
            deprel = parts[7]

            if parts[2] == u'_':
                lemma = u''
            if parts[5] == u'_':
                feat = []
            misc = parts[9]


            # Append the fields to the current tree.
            forms.append(form)
            lemmas.append(lemma)
            cpostags.append(cpostag)
            postags.append(postag)
            feats.append(feat)
            heads.append(head)
            deprels.append(deprel)
            miscs.append(misc)

        # Catch all exceptions occurred while parsing, and report filename
        # and line number.
        except ValueError, e:
            msg = 'error while reading CoNLL file %r, line %i: %s'
	    ## skip connectedness / loopness issue
            if u'dicsonnected' in e: continue
            raise ValueError(msg % (filename_or_file, line_no, e))

    # On end-of-file, don't forget to yield the last tree.
    if forms:
        try:
            yield Tree(forms, lemmas, cpostags, postags, feats, heads, deprels, miscs, sent_id)
        except:
            #print('error: try to yield a bad conncted tree ({}) !'.format(sent_id))
            pass # skip bad tree

def write_tree_conll(file, tree):
    """
    Write a tree to a file in CoNLL format.

    file: file-like object.
    tree: a Tree.
    """
    sent_id = tree._sent_id
    if sent_id:
        file.write(u'# sent_id = {}\n'.format(sent_id))
    for i in range(len(tree)):
        node = i + 1
        form = tree.forms(node)
        lemma = tree.lemmas(node)
        cpostag = tree.cpostags(node)
        postag = tree.postags(node)
        feats = tree.feats(node)
        head = tree.heads(node)
        deprel = tree.deprels(node)
        misc = tree.miscs(node)

        if not _valid(form, empty_allowed=False):
            raise ValueError(u'invalid FORM: %r' % form)
        if not _valid(lemma, empty_allowed=True):
            raise ValueError(u'invalid LEMMA: %r' % lemma)
        if not _valid(cpostag, empty_allowed=False):
            raise ValueError(u'invalid CPOSTAG: %r' % cpostag)
        if not _valid(postag, empty_allowed=False):
            raise ValueError(u'invalid POSTAG: %r' % postag)
        if any(not _valid(feat, empty_allowed=False) for feat in feats):
            raise ValueError(u'invalid FEATS: %r' % feats)
        if not _valid(deprel, empty_allowed=False):
            raise ValueError(u'invalid DEPREL: %r' % deprel)

        id = unicode(node)
        lemma = lemma or u'_'
        head = unicode(head)
        feats = u'|'.join(feats) or u'_'

        parts = [id, form, lemma, cpostag, postag, feats, head, deprel, misc]
        file.write(u'\t'.join(parts[:-1]) + u'\t_\t' + parts[-1]  + u'\n')

    file.write(u'\n')
