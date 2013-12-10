import nltk
try:
   import cPickle as pickle
except:
   import pickle

"""Returns a tuple containing the indices of the periods surrounding an index"""
def find_sentence_boundary(location):
    lower = location;
    upper = location + 1;
    
    for word in words[upper:]:
        if word == '.':
            break
        upper += 1

    for word in reversed(words[:lower]):
        if word == '.':
            break
        lower -= 1

    return (lower, upper)

"""Prints the words from indices lower to upper in the words array"""
def print_phrase(lower, upper):
    my_words = words[lower:upper+1]
    if len(my_words) < 1:
        return
    my_str = my_words[0]
    for word in my_words[1:]:
        if word not in punctuation_list:
            my_str += " "
        my_str += word
    print my_str

"""Locates instances of the target word and returns a list of indices"""
def find_instances(target):
    i = 0
    alist = []
    for word in words:
        if word.lower() == target:
            alist.append(i)
        i += 1
    return alist

"""Finds nearby (non-common) words in the same sentence as a given index"""
def within_k(index, k=5):
    (start, end) = find_sentence_boundary(index)
    
    if start < (index - k):
        lbound = index - k
    else:
        lbound = start

    if end > (index + k):
        ubound = index + k
    else:
        ubound = end

    return [word.lower() for word in words[lbound:ubound] if word not in
            punctuation_list and word.lower() not in common_word_list]

"""Identifies the most common words surrounding a given word"""
def aggregate_within_k(target, k=5):
    index = 0
    myset = set()
    words = get_corpus()
    
    for word in words:
        if word == target:
            myset.update(within_k(index, k))
        index += 1
    return myset

"""Writes a CFD to a file for safekeeping"""
def write_cfd_to_disk(subject, cfd):
    filename = "cfd_%s_%s" % (corpus, subject)
    output_file = open(filename, 'w')
    pickle.dump(cfd, output_file)
    output_file.close()

"""Reads a CFD from a file"""
def read_cfd_from_disk(subject):
    filename = "cfd_%s_%s" % (corpus, subject)
    input_file = open(filename, 'r')
    cfd = pickle.load(input_file)
    input_file.close()
    return cfd

"""Generates a CFD and writes it to a file"""
def generate_cfd(target):
    k = 5
    associated_words = aggregate_within_k(target, k)
    print "Done with aggregate_within_k()..."
    cfd = nltk.ConditionalFreqDist()
    index = 0
    words = get_corpus()
    for word in words:
        if word in associated_words:
            for nearby_word in within_k(index, k):
                if nearby_word in associated_words:
                    cfd[word].inc(nearby_word)
        index += 1
        if index % 100000 == 0:
            print "Passing word %d..." % index
    write_cfd_to_disk(target, cfd)
    return cfd

"""Finds words that correspond most to the target"""
def find_best_predictors(target, cfd, how_many=25):
    denominator = 1. * cfd[target][target] / len(words)
    mydict = {}
    for condition in cfd.conditions():
        numerator = 1. * cfd[condition][target] / cfd[condition][condition]
        if target != condition and numerator != 0:
            mydict[numerator / denominator] = condition
    return [(mydict[key], key) for key in \
            sorted(mydict.keys(), reverse=True)[:how_many]]

"""Populates a new CFD from the old CFD using only the words in word_list"""
def prune_cfd(word_list, cfd):
    newcfd = nltk.ConditionalFreqDist()
    for word in word_list:
        for sample in cfd[word].samples():
            if sample in word_list:
                newcfd[word].inc(sample, cfd[word][sample])
    return newcfd

"""Returns a list of the first items in a list of tuples"""
def get_words(the_list):
    return [word for (word, value) in the_list]

"""Returns the current corpus"""
def get_corpus:
    if corpus == 'gutenberg':
        return nltk.corpus.gutenberg.words()
    elif corpus == 'brown':
        return nltk.corpus.brown.words()
    else:
        corpus = 'reuters'
        return nltk.corpus.reuters.words()


"""Adds a word to the list of senses"""
def add_word(word1, word2, senses):
    for sense in senses:
        if (word1 in sense) or (word2 in sense):
            sense.update((word1, word2))
            return
    senses.append(set((word1, word2)))

"""Returns a list of sets of related words hopefully corresponding to senses"""
def get_senses(predictors, cfd):
    predictor_words = get_words(predictors)
    pruned_cfd = prune_cfd(predictor_words, cfd)
    mydict = {}
    for predictor in predictor_words:
        mydict[predictor] = find_best_predictors(predictor, pruned_cfd, 10)
        
    senses = []
    score_threshold = 3000 #Magic number, seems to work
    for predictor in mydict.keys():
        for (word, score) in mydict[predictor]:
            if score > score_threshold: 
                for (word1, score1) in mydict[word]:
                    if word1 == predictor:
                        if score1 > score_threshold:
                            add_word(word, word1, senses)
                    break
    return senses
    
"""The method behind the madness"""
def do_it_all(target):
    target = target.lower()
    print "\nProcessing \"%s\" in corpus \"%s\":" % (target, corpus)
    cfd = generate_cfd(target)
    #cfd = read_cfd_from_disk(target)
    predictors = find_best_predictors(target, cfd, 35)
    senses = get_senses(predictors, cfd)
    for sense in senses:
        print sense
    print ""
    
if __name__ == '__main__':
    punctuation_list = "!\"\'(),-.:;?[\\]^_`{|}~"
    common_word_list = ()#('and', 'in', 'of', 'the', 'a', 'an', 'to', 'at', 's', \
                       #'for', 'its', 'said')

    corpus = 'gutenberg'
    words = get_corpus()

    homographs = ['lead', 'plant', 'bow', 'close', 'refuse']
    for homograph in homographs:
        do_it_all(homograph)
