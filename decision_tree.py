import pandas as pd
import operator
from math import log


data = pd.read_csv('heart.csv')
X = data.iloc[:,:13].values
features = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
            "exang", "oldpeak", "slope", "ca", "thal", "target"]


#Calulate the entropy
def cal_entropy(data):
    num_data = len(data)
    if num_data == 0:
        print("The dataset is empty.")
        return
    #Count the different label, use in probility
    label_dictionary = {}
    for i in data:
        #The label in the end of the column.
        label = i[-1]
        #If the label not in the dictionary, just add it.
        if label not in label_dictionary.keys():
            label_dictionary[label] = 0
        label_dictionary[label] += 1
    entropy = 0.0
    for key in label_dictionary.keys():
        prob = float(label_dictionary[key] / num_data)
        entropy -= prob * log(prob, 2)
    return entropy

#Divide the data set by features. Input the dataset and the split feature value, and return the list
def split_dataset(data,feature_index,val):
  #Divided data set
  data_split=[]
  #Traverse the data set and extract the current value feature of feature_index to divide the data.
  for i in data:
      if i[feature_index] == val:
        new_data = i[:feature_index]
        new_data.extend(i[feature_index+1:])
        data_split.append(new_data)
  return data_split

def choose_best_to_split(data):
    #Num of features without target
    num_feature = len(data[0]) - 1
    #sum of entropy
    entropy = cal_entropy(data)
    #Max info gain
    max_info_gain = 0.0
    #Index of max info gain
    max_info_gain_index = -1
    
    for i in range(num_feature):
        #Get all the value of column
        feature_element = [ele_index[i] for ele_index in data]
        #Remove all the duplicates
        uni_ele = set(feature_element)

        pro_entropy = 0.0
        pro_abs_entropy = 0.0
        #Check all the element and calculate the entropy
        for val in uni_ele:
            sub_data = split_dataset(data, i, val)
            pro = len(sub_data) / float(len(data))
            pro_entropy += pro * cal_entropy(sub_data)
            pro_abs_entropy += pro * abs(cal_entropy(sub_data))
        #Calculate the info gain
        info_gain = entropy - pro_entropy
        # Calculate the fair gain
        fair_gain = abs(entropy) - pro_abs_entropy
        #If fair gain not equal zero, info gain equal to info gain * fair gain.
        if fair_gain != 0:
            info_gain = info_gain * fair_gain
        #Update the max info gain index.
        if (info_gain > max_info_gain):
            max_info_gain = info_gain
            max_info_gain_index = i
    return max_info_gain_index

def vote_label(class_list):
    class_count = {}
    #Count each element in the list
    for vote in class_list:
        if vote not in class_count.keys():
            class_count[vote] = 0
        class_count[vote] += 1
        #Sorted the dictionary
        sorted_res = sorted(class_count.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_res[0][0]


def decesion_tree(data, features):
    feature = features[:]
    #The label for the node
    label_list = [i[-1] for i in data]
    #If it all belong one label, just return it
    if label_list.count(label_list[0]) == len(label_list):
        return label_list[0]
    #The last feature
    if len(data[0]) == 1:
        #Return the most occur
        return vote_label(label_list)
    #Choose best feature to split
    best_pos = choose_best_to_split(data)
    best_feature_name = feature[best_pos]
    #remove this feature name
    del(feature[best_pos])
    DecisionTree = {best_feature_name:{}}
    #Create the child
    all_child = [j[best_pos] for j in data]
    uni_child = set(all_child)
    sort_child = sorted(list(uni_child))
    for k in sort_child:
        featname = feature[:]
        DecisionTree[best_feature_name][k] = decesion_tree(split_dataset(data, best_pos, k), featname)
    return DecisionTree

def accuracy_test(DTree, data, features):
    class_label = ""
    feature = list(DTree.keys())[0]
    first_dict = DTree[feature]
    index = features.index(feature)
    #Based on value choice the child
    for i in first_dict.keys():
        if index == 12:
            index = index - 1
        if data[index] == i:
            if type(first_dict[i]) == dict:
                class_label = accuracy_test(first_dict[i], data, features)
            else:
                return first_dict[i]
    return class_label

X_train = X[800:]
X_test = X[:800]
decisiontree = decesion_tree(X_train.tolist(), features)
count = 0
xtest = X_test.tolist()
for test in xtest:
    label = accuracy_test(decisiontree, test, features)
    if (label == test[-1]):
        count = count + 1
accuracy = float(count / len(xtest))
print('The test accuracy of decision tree:{0: .2f}%'.format(accuracy * 100))


