import nltk.data
import io
import csv
import spacy
import nltk
import re
from nltk.tree import Tree
from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')
nlp_spacy = spacy.load('en_core_web_sm')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def dependency_distance(input):
	doc = nlp_spacy(input)
	# for token in doc:
	#     print(token.text, token.dep_, token.head.text, token.head.pos_,
	#           [child for child in token.children])

	sum = 0

	for token in doc:
		parent_pos = get_pos(token,doc)
		for child in token.children:
			child_pos = get_pos(child,doc)
			arc_length = abs(parent_pos - child_pos)
			sum = sum + arc_length

	length = len(doc)
	return sum/length



def get_pos(x, doc):
	position = 1
	for token in doc:
		if token == x:
			return position
		position = position + 1	


def frazier_scoring(input_tree, current, current_label):
    if type(input_tree) == str:
        return current-1
    else:
        final_score = 0
        for i, child in enumerate(input_tree):
            score = 0
            if i == 0:
                my_lab = input_tree.label()
                if my_lab == "S":
                    score = (0 if current_label == "S" else current+1.5)
                elif my_lab != "":
                    score = current + 1
            final_score += frazier_scoring(child, score, my_lab)
        return final_score


def yngve_scoring(t, current):
	if type(t) == str:
		return current
	else:
		val = 0
		for i, child in enumerate(reversed(t)):
			val += yngve_scoring(child, current+i)
		return val


def print_results(results):
	with open("Data/Papers_only_him_FinalScores/sample.csv", "w") as csvFile:
		fieldnames = ['sentence', 'yngve_score', 'frazier_score', 'dependency_distance_score', 'count', 'year']
		writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
		writer.writeheader()

		for item in results:
			writer.writerow({
				'sentence': item[0], 
				'yngve_score': item[1], 
				'frazier_score' : item[2], 
				'dependency_distance_score': item[3],
				'count': item[4],
				'year' : 1996
				})

def count_words(input_tree):
    if type(input_tree) == str:
        return 1
    else:
        count = 0
        for child in input_tree:
            count += count_words(child)
        return count


def calculate_scores(list_of_sents):
	final_results = list()
	for item in list_of_sents:
		local_result = list()	
		output = nlp.annotate(item.encode('ascii','ignore'), properties={ 'annotators': 'parse', 'outputFormat': 'json' })
		print item
		tree = output['sentences'][0]['parse'] # tagged output sentence
		tree_string = tree.encode('ascii','ignore')
		input_tree_string = tree_string
		regex_remove_root = r"\(ROOT\s+(.+)\)" #regex to remove the root of the tree
		grouped_regex = re.search(regex_remove_root, input_tree_string.replace("\n", " "))
		input_tree = Tree.fromstring(grouped_regex.group(1))
		yngve_score = yngve_scoring(input_tree,0)
		frazier_score = frazier_scoring(input_tree, 0, "")
		count = count_words(input_tree)
		dependency_distance_score = dependency_distance(item)
		#print item.encode('ascii','ignore'), yngve_score, frazier_score, dependency_distance_score
		local_result.append(item.encode('ascii','ignore'))
		local_result.append(yngve_score/count)
		local_result.append(frazier_score/count)
		local_result.append(dependency_distance_score)
		local_result.append(count)
		final_results.append(local_result)
	print "out of for loop"
	print_results(final_results)


def get_sentences():
	print "Inside get_sentences function"
	with io.open("Data/Papers_only_him_in_txt/1996.txt", "r", encoding="utf-8") as my_file:
		my_unicode_string = my_file.read() 

	my_unicode_string = my_unicode_string.replace(":", ".")
	my_unicode_string = my_unicode_string.replace("-\n", "")
	my_unicode_string = my_unicode_string.replace("\n", " ")

	list_of_sents = tokenizer.tokenize(my_unicode_string)
	return list_of_sents

def main():
	print "Inside the main function"
	list_of_sents = get_sentences()
	calculate_scores(list_of_sents)

if __name__ == '__main__':
	main()
