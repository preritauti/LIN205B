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

#Calculate the depedency distance of the input sentence
#Returns score = Sum of all the dependency distance / Total number of words
def dependency_distance(input):
	doc = nlp_spacy(input)
	total = 0
	for token in doc:
		parent_pos = get_pos(token,doc)
		for child in token.children:
			child_pos = get_pos(child,doc)
			arc_length = abs(parent_pos - child_pos)
			total = total + arc_length

	length = len(doc)
	return float(total)/length


#Get the position of a element x from doc
def get_pos(x, doc):
	position = 1
	for token in doc:
		if token == x:
			return position
		position = position + 1	


#Calculate the frazier score of the input tree.
#Returns the sum of scores
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


#Calculates the yngve score of the input tree
#Returns sum of scores
def yngve_scoring(t, current):
	if type(t) == str:
		return current
	else:
		val = 0
		for i, child in enumerate(reversed(t)):
			val += yngve_scoring(child, current+i)
		return val


#Prints the final result for one paper into a csv files
def print_results(results):
	with open("Data/Papers_only_him_FinalScores/2005.csv", "w") as csvFile:
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
				'year' : 2005
				})

#Counts the number of terminal nodes in a tree
def count_words(input_tree):
    if type(input_tree) == str:
        return 1
    else:
        count = 0
        for child in input_tree:
            count += count_words(child)
        return count

#Calculates the score of all the senetences in the list
def calculate_scores(list_of_sents):
	final_results = list()
	for item in list_of_sents:
		local_result = list()	
		#print item

		#Find the parse tree of the input tree
		output = nlp.annotate(item.encode('ascii','ignore'), properties={ 'annotators': 'parse', 'outputFormat': 'json' })
		tree = output['sentences'][0]['parse'] # tagged output sentence
		input_tree_string = tree.encode('ascii','ignore')
		regex_remove_root = r"\(ROOT\s+(.+)\)" #regex to remove the root of the tree
		grouped_regex = re.search(regex_remove_root, input_tree_string.replace("\n", " "))
		input_tree = Tree.fromstring(grouped_regex.group(1))

		#Calculate scores using all three measures
		yngve_score = yngve_scoring(input_tree,0)
		frazier_score = frazier_scoring(input_tree, 0, "")
		dependency_distance_score = dependency_distance(item)

		#Count the number of terminal in the root node
		count = count_words(input_tree)

		#Create a list of all the information
		local_result.append(item.encode('ascii','ignore'))
		local_result.append(float(yngve_score)/count)
		local_result.append(float(frazier_score)/count)
		local_result.append(dependency_distance_score)
		local_result.append(count)
		final_results.append(local_result)

	print "Completed parsing all the sentences in the paper"
	print_results(final_results)

#Gets a list of sentences from the file.
def get_sentences():
	with io.open("Data/Papers_only_him_in_txt/2005.txt", "r", encoding="utf-8") as my_file:
		my_unicode_string = my_file.read() 

	my_unicode_string = my_unicode_string.replace(":", ".")
	my_unicode_string = my_unicode_string.replace("-\n", "")
	my_unicode_string = my_unicode_string.replace("\n", " ")

	list_of_sents = tokenizer.tokenize(my_unicode_string)
	return list_of_sents


def main():
	list_of_sents = get_sentences()
	calculate_scores(list_of_sents)

if __name__ == '__main__':
	main()
