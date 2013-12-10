from nltk import FreqDist, ConditionalFreqDist
import random
import math

class MLEProbDist:
    """A simple probability distribution class."""
    
    def __init__(self, freq_dist):
        """Creates a MLEProbDist from the given freq_dist."""
        self.fd = freq_dist

    def prob(self, event):
        """Returns the probability of a given event."""
        return self.fd.freq(event)

class AddGammaProbDist:
    """A probability distribution class that incorporates smoothing."""

    def __init__(self, freq_dist, bins, gamma):
        """Creates an AddGammaProbDist from the given input."""
        self.fd = freq_dist
        self.bins = bins
        self.gamma = 1. * gamma # Ensure that gamma is a float

    def prob(self, event):
        """Returns the smoothed probability of a given event."""
        return (self.fd[event] + self.gamma) / \
               (self.fd.N() + self.bins * self.gamma)

def make_ngram_tuples(samples, n):
    """Returns a list of words with their contexts (the previous n-1 words)."""
    the_list = []
    for i in range(n - 1, len(samples)):
        if n == 1:
            current_tuple = None
        else:
            current_tuple = tuple(samples[i-(n-1):i])
        the_list.append(tuple([current_tuple, samples[i]]))
    return the_list

class NGramModel:
    """An n-gram model class."""

    def __init__(self, training_data, n, full_data=None, gamma=1.0):
        """Creates an NGramModel class from the given input and n value
with optional smoothing specified by full_data and gamma."""
        self.cfd = ConditionalFreqDist(make_ngram_tuples(training_data, n))
        if full_data == None:
            self.full_cfd = None
        else:
            self.full_cfd = \
                ConditionalFreqDist(make_ngram_tuples(full_data, n))
        self.gamma = gamma

    def prob(self, context, event):
        """Returns the probability (smoothed or not, based on this instance
of NGramModel) of the given event in the given context."""
        if self.full_cfd == None:
            return MLEProbDist(self.cfd[context]).prob(event)
        else:
            return AddGammaProbDist(self.cfd[context], \
                                    self.full_cfd[context].B(), \
                                    self.gamma).prob(event)
        # If the context is not in the CFD, AddGammaProbDist treats this
        # like an event that hasn't happened; this is proper behavior

    def items(self):
        """Returns a list of the events in this NGramModel with their contexts
and probabilities."""
        if self.full_cfd == None:
            my_prob_dist = MLEProbDist
        else:
            my_prob_dist = AddGammaProbDist
            
        the_list = []
        for context in self.cfd.conditions():
            prob_dist = my_prob_dist(self.cfd[context])
            for event in self.cfd[context]:
                if prob_dist.prob(event) != 0:
                    the_list.append(tuple([context, event, \
                                       prob_dist.prob(event)]))
        return the_list

    def generate(self, n, context):
        """Generates a sentence up to n words long from the given context."""
        if context == None:
            generated = []
        else:
            generated = list(context)
        for i in range(n-len(context)):
            context = tuple(generated[i:i+n]) # update context as we go
            target = random.random() # float in range [0, 1)
            sum_to_date = 0.0
            vocabulary = self.cfd[context].keys()
            if len(vocabulary) == 0:
                break
            random.shuffle(vocabulary) # for a bit of added randomness
            for word in vocabulary:
                sum_to_date += self.cfd[context].freq(word)
                if sum_to_date > target:
                    generated.append(word)
                    break
        return generated[:n] # handles case where len(context) > n

def sweep_smoothing(full_words, train_words, test_words, n, min_smooth, \
                    max_smooth):
    """Gives the KL Divergence between an unsmoothed NGramModel and an
NGramModel smoothed with varying values of gamma."""
    non_smoothed = NGramModel(test_words, n)
    the_list = []
    for i in range(min_smooth, max_smooth + 1):
        smoothed = NGramModel(train_words, n, full_words, 1./i)
        the_list.append(tuple([1./i, KL_div(non_smoothed, smoothed)]))
    return the_list

def KL_div(non_smoothed, smoothed):
    """Returns the Kullback-Liebler divergence of two models"""
    kl_div = 0.
    # Iterate through n-grams from the non-smoothed model
    for item in non_smoothed.items():
        prob_1 = item[2] # probability in location 2
        prob_2 = smoothed.prob(item[0], item[1]) # context, word
        kl_div += prob_1 * math.log((prob_1 / prob_2), 2) # log base 2
    return kl_div

if __name__ == '__main__':
    samples = 'oh rio rio dance'.split()
    print make_ngram_tuples(samples, 2)
    print

    model = NGramModel(samples, 2)
    print model.prob(('rio',), 'rio')
    print model.items()
    for i in range(4):
        print model.generate(4, ('oh',))
    print

    train_words = [word.lower() for word in \
                   """Her name is Rio and she dances on the sand
Just like that river twists across a dusty land
And when she shines she really shows you all she can
Oh Rio Rio dance across the Rio Grande""".split()]
    test_words = [word.lower() for word in \
                  """Her name is Rio she don't need to understand
I might find her if I'm looking like I can
Oh Rio Rio hear them shout across the land
From mountains in the North down to the Rio Grande""".split()]
    full_words = train_words + test_words
    print sweep_smoothing(full_words, train_words, test_words, 2, 1, 4)
