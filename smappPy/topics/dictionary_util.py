"""
Utility functions for the gensim.corpora.Dictionary object
"""

from gensim.corpora import Dictionary


def create_dictionary(doc_iterator, dict_file, as_text=False):
    """
    Creates a gensim.corpora.Dictionary object from given document iterator 
    and serializes it to given dict_file (filename) in a memory efficient way.
    @Params:
      as_text   - flag: dictionary saved as text (default: binary)
    """    
    d = Dictionary(doc.strip().lower().split() for doc in doc_iterator)
    if as_text:
        d.save_as_text(dict_file)
    else:
        d.save(dict_file)