import numpy as np
import pandas as pd
import json
import pickle
import os

label_path = 'MLDS_hw2_1_data/training_label.json'
feat_path  = 'MLDS_hw2_1_data/training_data/feat'
test_path  = 'MLDS_hw2_1_data/testing_data/feat'


# label_path = 'drive/deep/hw2/MLDS_hw2_1_data/training_label.json'
# feat_path  = 'drive/deep/hw2/MLDS_hw2_1_data/training_data/feat'
# test_path  = 'drive/deep/hw2/MLDS_hw2_1_data/testing_data/feat'

def _removeNonAscii(s):
	return "".join([i for i in s if ord(i)<128])

word_collection = set()

mirror = pickle.load(open('mirror.pickle','rb'))
##############################
from termcolor import colored#
##############################
def word_preprocessing(x):
	white_space = ['..', '...', '/']
	none = ['.', ',', '"', '\n', '?', '!', '(', ')']
	x = [_removeNonAscii(s) for s in x]
	for _ in white_space: 
		x = [s.replace(_, ' ') for s in x]
	for _ in none: 
		x = [s.replace(_, '') for s in x]
	
	for sen in x:
		for word in sen.split():
			word_collection.add(word)
	'''
	for sen in x:
		if "ing" in sen:
			for word in sen.split():
				if "ing" in word:
					print(colored(word,'red'),end=' ')
				else:
					print(word , end=' ')
			print()
	'''
	final_x = []
	for sen in x:
		print(colored(sen,'cyan'))
		print(colored(' '.join([mirror[word] for word in sen.split()]),'red'))
		final_x.append(' '.join([mirror[word] for word in sen.split()]))
	#print(x)
	return final_x


from nltk.tokenize import word_tokenize
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
class sentence_repair:
	@staticmethod
	def trim_repeat(sentence):
		after = ['*HEAD*']
		for word in sentence.split():
			if word != after[-1]:
				after.append(word)
		return ' '.join(after[1:])
	@staticmethod
	def verb_repair(sentence):
		# be-V repair
		sentence = sentence.split()
		for idx in range(len(sentence)):
			if sentence[idx] == 'be':
				if 'a' in sentence[max(0,idx-3) : idx] or \
					'the' in sentence[max(0,idx-3) : idx] :
					sentence[idx] = 'is'
				else:
					sentence[idx] = 'are'
		# be-V + Ving repair
		for idx in range(len(sentence)):
			if sentence[idx] in ['is' ,'are']:
				if idx+1 < len(sentence):
					#print(nltk.pos_tag([sentence[idx+1]]))
					if nltk.pos_tag([sentence[idx+1]])[0][1] in ['VB','VBZ' , 'VBD' , 'VBN' , 'VBG' , 'NN']:
						if sentence[idx+1][-1] is not 'e':
							sentence[idx+1] = sentence[idx+1] + 'ing'
						else:
							sentence[idx+1] = sentence[idx+1][:-1] + 'ing'
				
		return ' '.join(sentence)
	@staticmethod
	def simple_repair(sentence):
		sentence = sentence_repair.trim_repeat(sentence)
		sentence = sentence_repair.verb_repair(sentence)
		return sentence


class caption_test:
	def __init__(self):
		file_lists = [ filename for filename in os.listdir(test_path)]
		self.file_lists = file_lists
		self.test_data = [np.load(test_path + '/' + filename) for filename in file_lists]
		self.N = len(file_lists)
		self.next_batch_counter = 0
		print('test_data initization finished.')
	def next_batch(self,batch_size):
		if self.next_batch_counter + batch_size < self.N:
			output = self.test_data[self.next_batch_counter:self.next_batch_counter+batch_size]
			self.next_batch_counter += batch_size
			if self.next_batch_counter == self.N:
				self.next_batch_counter = 0
		else:
			output = []
			for i in range(batch_size):
				output.append(self.test_data[self.next_batch_counter])
				self.next_batch_counter += 1
				if self.next_batch_counter >=self.N:
					self.next_batch_counter = 0
		return output
	
	def single_test(self):
		feat_name = self.file_lists[self.next_batch_counter]
		feat = self.test_data[self.next_batch_counter]
		self.next_batch_counter += 1
		if self.next_batch_counter >= self.N:
			self.next_batch_counter = 0
		return feat , feat_name

class caption_data:

	def __init__(self , word_min_frequency=3 , verbose = True):
		# read file
		with open(label_path,'r') as fin:
			self.allData = pd.DataFrame(json.load(fin))

		# word preprocessing
		self.N = self.allData.shape[0]
		self.allData['caption'] = self.allData['caption'].apply(word_preprocessing)

		# build dictionary
		word_counter = np.zeros((20000))
		self.word_dim = 0	
		self.D = {}

		## add special character
		for voc in ['<bos>' , '<eos>' , '<pad>' , '<unk>']:
			self.D.update({voc:self.word_dim})
			word_counter[self.D[voc]] = 99999
			self.word_dim += 1

		## add vocab in dataframe
		def build_dictionary(x):
			for s in x:
				for voc in s.split():
					if voc not in self.D:
						self.D.update({voc:self.word_dim})
						self.word_dim += 1
					word_counter[self.D[voc]] += 1
		self.allData['caption'].apply(build_dictionary)

		# filter word_dim by frequency
		self.D = {i:self.D[i] for i in self.D if word_counter[self.D[i]] >= word_min_frequency}
		self.word_dim = len(self.D)
		self.D = {i:j for i, j in zip(self.D, [_ for _ in range(self.word_dim)])}
		self.inv_D = { self.D[key] : key for key in self.D}

		# Data Cleaning
		self.sen_max_length = 15
		def data_cleaning(x):
			cleaning = []
			for sen in x:
				new_sen = ['<bos>']
				for voc in sen.split():
					if voc not in self.D:
						new_sen.append('<unk>')
					else:
						new_sen.append(voc)
				s = " ".join(new_sen)
				cleaning.append(s)
			return cleaning

		self.allData['caption'] = self.allData['caption'].apply(data_cleaning)
		print('(data preprocessing) quantity of videos: ',self.N)
		print('(data preprocessing) quantity of vocs  : ',self.word_dim)
		print ("max_length = ", self.sen_max_length)
		## FOR OTHER METHOD TO USE ##
		self.next_batch_counter = 0
		self.inv_D = { self.D[key] : key for key in self.D}
		
	def getAFullCap(self,idx):
		filename = self.allData.loc[idx, 'id']
		print(self.allData.loc[idx, 'caption'])
		return np.load(feat_path + '/'+ filename+'.npy')


	def getASingleCap(self,idx):
		cur_len = 0
		while cur_len == 0 or cur_len > self.sen_max_length:
			sen_idx = np.random.randint(0,len(self.allData.loc[idx, 'caption']))
			now_sen_list = self.allData.loc[idx, 'caption'][sen_idx].split()
			cur_len = len(now_sen_list)

		output = []
		for i,voc in zip(range(len(now_sen_list)),now_sen_list):
			try:
				output.append(self.D[voc])
			except:
				output.append(self.D['<unk>'])
		filename = self.allData.loc[idx, 'id']
		#print(now_sen)
		return np.load(feat_path + '/'+ filename+'.npy'),output

	def next_batch(self,batch_size):
		output = []
		feat_output = []
		max_length = 0
		for _ in range(batch_size):
			if self.next_batch_counter >= self.N:
				self.next_batch_counter = 0
			#print('N:' , self.N , self.next_batch_counter)
			feat,sing = self.getASingleCap(self.next_batch_counter)
			max_length = max(max_length , len(sing))
			output.append(sing)
			feat_output.append(feat)
			self.next_batch_counter += 1
		
		for sing in output:
			sing.append(self.D['<eos>'])
			sing += [ self.D['<pad>'] for _ in range(max_length-len(sing)+1) ]
		#exit()
		return np.array(feat_output),np.array(output)

	def one_to_sen(self,one_hot):
		return  ' '.join([ self.inv_D[idx] for idx in one_hot])

	def predict(self, one_hot):
		word = []
		for idx in one_hot[1:]:
			if self.inv_D[idx] == '<pad>':
				pass
			elif self.inv_D[idx] == '<eos>':
				break
			else:
				word.append(self.inv_D[idx])
		s = sentence_repair.simple_repair(' '.join(word)) + '.'
		return s.capitalize()

if __name__ == '__main__':
	print(sentence_repair.trim_repeat("cat a a a a cat be be be sth"))
	print(sentence_repair.verb_repair("cat a a a a cat be be be sth"))
	print(sentence_repair.verb_repair("a cat be cook"))
	print(sentence_repair.simple_repair("a monkey be on a a "))
	print(sentence_repair.simple_repair("a be be peel shrimp"))
	print(sentence_repair.simple_repair("a be"))


	print()



	#C = caption_data(verbose = False)
	#import numpy as np
	#np.save('word_collection',word_collection)
	#print(word_collection)
	'''
	C.getAFullCap(790)
	print(C.getASingleCap(877)[1])
	for row in C.next_batch(10)[1]:
		print(row)
	'''
	#CC = caption_test()

	#print(CC.next_batch(50))
#for i in C.allData:
#	print(len(i['caption']))
#print(C.next_batch(10))
#print(C.next_batch(10))

