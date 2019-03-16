import pprint
"""

You have to write the perc_train function that trains the feature weights using the perceptron algorithm for the CoNLL 2000 chunking task.

Each element of train_data is a (labeled_list, feat_list) pair.

Inside the perceptron training loop:

    - Call perc_test to get the tagging based on the current feat_vec and compare it with the true output from the labeled_list

    - If the output is incorrect then we have to update feat_vec (the weight vector)

    - In the notation used in the paper we have w = w_0, w_1, ..., w_n corresponding to \phi_0(x,y), \phi_1(x,y), ..., \phi_n(x,y)

    - Instead of indexing each feature with an integer we index each feature using a string we called feature_id

    - The feature_id is constructed using the elements of feat_list (which correspond to x above) combined with the output tag (which correspond to y above)

    - The function perc_test shows how the feature_id is constructed for each word in the input, including the bigram feature "B:" which is a special case

    - feat_vec[feature_id] is the weight associated with feature_id

    - This dictionary lookup lets us implement a sparse vector dot product where any feature_id not used in a particular example does not participate in the dot product

    - To save space and time make sure you do not store zero values in the feat_vec dictionary which can happen if \phi(x_i,y_i) - \phi(x_i,y_{perc_test}) results in a zero value

    - If you are going word by word to check if the predicted tag is equal to the true tag, there is a corner case where the bigram 'T_{i-1} T_i' is incorrect even though T_i is correct.

"""

import perc
import sys
import optparse
import os
from collections import defaultdict


def count_errors(test, truth):
    """
    Helper to count the amount of errors between the predicted output and the known truth reference.
    """
    count = 0
    for idx, item in enumerate(test):
        if item != truth[idx]:
            count += 1
    return count


def update_feat_vect(feat_vec, avg_feat_vec, iter_num, epoch, last_update, train_data_index, train_data_size, feat_list, z, truth):

    """
    Update the provided weighting feature vector based on the given feature list, predicted output, and the truth reference.
    """

    if iter_num != epoch-1 or train_data_index != train_data_size-1:
        for i in range(len(z)):
            if z[i] != truth[i]:
                for j in range(19):
                    yprime = (feat_list[20*i+j], z[i])
                    y = (feat_list[20*i+j], truth[i])

                    feat_vec[yprime] -= 1
                    feat_vec[y] += 1

                    if yprime in last_update:
                        scale = iter_num * train_data_size + train_data_index - last_update[yprime][1] * train_data_size - last_update[yprime][0]
                        avg_feat_vec[yprime] += scale * feat_vec[yprime]
                    else:
                        avg_feat_vec[yprime] -= 1
                        
                    
                    if y in last_update:
                        scale = iter_num * train_data_size + train_data_index - last_update[y][1] * train_data_size - last_update[y][0]
                        avg_feat_vec[y] += scale * feat_vec[y]
                    else:
                        avg_feat_vec[y] += 1

                    last_update[yprime] = (train_data_index,iter_num)
                    last_update[y] = (train_data_index,iter_num)

                for j in range(2):

                    if (i == 0 and j == 0) or (i == len(z) - 1 and j == 1):
                        continue

                    yprime = (feat_list[20*i+19] + ":" + z[i-1+j], z[i+j])
                    y = (feat_list[20*i+19] + ":" + truth[i-1+j], truth[i+j])

                    feat_vec[yprime] -= 1
                    feat_vec[y] += 1

                    if yprime in last_update:
                        scale = iter_num * train_data_size + train_data_index - last_update[yprime][1] * train_data_size - last_update[yprime][0]
                        avg_feat_vec[yprime] += scale * feat_vec[yprime]
                    else:
                        avg_feat_vec[yprime] -= 1
                        
                    
                    if y in last_update:
                        scale = iter_num * train_data_size + train_data_index - last_update[y][1] * train_data_size - last_update[y][0]
                        avg_feat_vec[y] += scale * feat_vec[y]
                    else:
                        avg_feat_vec[y] += 1 

                    last_update[yprime] = (train_data_index, iter_num)
                    last_update[y] = (train_data_index, iter_num)
                    
    else:
        for key, value in last_update.items():
            scale_factor = epoch * train_data_size + train_data_size - value[1] * train_data_size - value[0]
            avg_feat_vec[key] = scale_factor * feat_vec[key]

        for i in range(len(z)):
            if z[i] != truth[i]:
                for j in range(19):
                    yprime = (feat_list[20*i+j], z[i])
                    y = (feat_list[20*i+j], truth[i])

                    feat_vec[yprime] -= 1
                    feat_vec[y] += 1

                    if yprime not in last_update:
                        avg_feat_vec[yprime] -= 1
                        
                    
                    if y not in last_update:
                        avg_feat_vec[y] += 1

                for j in range(2):

                    if (i == 0 and j == 0) or (i == len(z) - 1 and j == 1):
                        continue

                    yprime = (feat_list[20*i+19] + ":" + z[i-1+j], z[i+j])
                    y = (feat_list[20*i+19] + ":" + truth[i-1+j], truth[i+j])

                    feat_vec[yprime] -= 1
                    feat_vec[y] += 1

                    if yprime not in last_update:
                        avg_feat_vec[yprime] -= 1
                        
                    
                    if y not in last_update:
                        avg_feat_vec[y] += 1 

    return feat_vec, avg_feat_vec, last_update


pp = pprint.PrettyPrinter()


def perc_train(train_data, tagset, numepochs):

    """
    Perceptron training algorithm

    We run the provided training data and tagset for `numepoch` training runs over the entire training set.
    """   

    feat_vec = defaultdict(int)
    avg_feat_vec = defaultdict(int)
    z = []
    truth = []
    last_update = {}
    train_data_index = 0
    train_data_size = len(train_data)

    previous_error_count = 0

    for i in range(numepochs):
        final_z = []
        final_truth = []
        for (labeled_list, feat_list) in train_data:
            truth = [x.split(" ")[2] for x in labeled_list]
            z = perc.perc_test(feat_vec, labeled_list,
                               feat_list, tagset, tagset[0])

            final_z.append(z)
            final_truth.append(truth)

            if z != truth:
                feat_vec, avg_feat_vec, last_update = update_feat_vect(feat_vec, avg_feat_vec, i, numepochs,
                                            last_update, train_data_index, train_data_size, feat_list, z, truth)

            train_data_index += 1

        error_count = count_errors(final_truth, final_z)
        print("number of mistakes: ", error_count)

        if i > 0 and error_count >= previous_error_count:
            break

        previous_error_count = error_count
    # pp.pprint(feat_vec)

    return_value = {}

    for key, value in  avg_feat_vec.items():
        return_value[key]  = value/(train_data_size * numepochs)
    
    # please limit the number of iterations of training to n iterations
    return return_value


if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-t", "--tagsetfile", dest="tagsetfile", default=os.path.join("data", "tagset.txt"),
                         help="tagset that contains all the labels produced in the output, i.e. the y in \phi(x,y)")
    optparser.add_option("-i", "--trainfile", dest="trainfile", default=os.path.join(
        "data", "train.txt.gz"), help="input data, i.e. the x in \phi(x,y)")
    optparser.add_option("-f", "--featfile", dest="featfile", default=os.path.join("data", "train.feats.gz"),
                         help="precomputed features for the input data, i.e. the values of \phi(x,_) without y")
    optparser.add_option("-e", "--numepochs", dest="numepochs", default=int(10),
                         help="number of epochs of training; in each epoch we iterate over over all the training examples")
    optparser.add_option("-m", "--modelfile", dest="modelfile", default=os.path.join(
        "data", "default.model"), help="weights for all features stored on disk")
    (opts, _) = optparser.parse_args()

    # each element in the feat_vec dictionary is:
    # key=feature_id value=weight
    feat_vec = {}
    tagset = []
    train_data = []
    tagset = perc.read_tagset(opts.tagsetfile)
    print("reading data ...", file=sys.stderr)
    train_data = perc.read_labeled_data(
        opts.trainfile, opts.featfile, verbose=False)
    print("done.", file=sys.stderr)
    feat_vec = perc_train(train_data, tagset, int(opts.numepochs))
    # pp.pprint(feat_vec)
    perc.perc_write_to_file(feat_vec, opts.modelfile)
