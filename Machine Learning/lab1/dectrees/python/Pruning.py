import random

from collections import OrderedDict

import monkdata
import dtree
import drawtree_qt5


####################################################################
"""
                        Written by
                Tim Decuypere and Ryan D'souza
            Prunes a Decision Tree to improve accuracy          """
####################################################################


def partition(data, fraction):
    """ 
        Partitions the data based on the fraction

        :param data: monkeydata
        :param fraction: float value of fraction
        
        :return tuple: (first fraction of data, remaining data)
    """

    data_list = list(data)
    random.shuffle(data_list)

    breakpoint = int(len(data_list) * fraction)

    return data_list[:breakpoint], data_list[breakpoint:]


def prune_tree(monkdata_set, num_trials=50):
    """ 
        Randomizes data and then splits into partitions based on partition_fractions
        Creates a tree based on the first partition (training data)
        Prunes that tree multiple times to see effect of pruning and partition on accuracy 
        Returns a dict with partition_fraction mapped to best accuracy list

        :param monkdata_set: monkdata set from monkdata.py
        :param num_trials: number of trials to run

        :returns dict: partition_fraction mapped to a list of tuples
    """

    partition_fractions = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    #Key: partition_fraction. Value: list of max accuracy in the pruning
    partition_accuracy = OrderedDict()

    for i in range(0, num_trials):

        for partition_fraction in partition_fractions:

            monk_training, monk_validation = partition(monkdata_set, partition_fraction)
            tree = dtree.buildTree(monk_training, monkdata.attributes)
            accuracy = dtree.check(tree, monk_validation)

            prune_counter = 0
            max_accuracy = accuracy
            max_accuracy_prune = 0

            pruned_trees = dtree.allPruned(tree)

            for pruned_tree in pruned_trees:
                prune_counter += 1
                pruned_accuracy = dtree.check(pruned_tree, monk_validation)

                #Keep track of the largest prune_accuracy and number
                if pruned_accuracy > max_accuracy:
                    max_accuracy = pruned_accuracy
                    max_accuracy_prune = prune_counter


            #If we haven't stored the fraction yet, create a new array
            if not partition_fraction in partition_accuracy:
                partition_accuracy[partition_fraction] = list()

            #Add our most recent trial result there
            prune_result = (max_accuracy_prune, max_accuracy)
            partition_accuracy[partition_fraction].append(prune_result)


    return partition_accuracy


def print_csv_style(partition_accuracy):
    """ Given the partition_accuracy from prune_tree
        Prints the values in a CSV format

        :param partition_accuracy: dictionary returned from prune_tree()
    """

    partition_fractions = partition_accuracy.keys()
    num_rows = len(partition_accuracy[partition_fractions[0]])

    #Print out the partition_fractions --> they are headers
    for partition_fraction in partition_fractions:
        print str(partition_fraction) + ",",
    print("")


    for i in range(0, num_rows):
        for partition_fraction in partition_fractions:

            max_accuracy_prune, max_accuracy = partition_accuracy[partition_fraction][i]
            
            #Print only the max accuracy, do not new-line it 
            print(str(max_accuracy) + ","),

        #New line after every row
        print("")


if __name__ == "__main__":
    """ Main method """

    print("Monk 1\n\n")
    partition_accuracy_monk1 = prune_tree(monkdata.monk1)
    print_csv_style(partition_accuracy_monk1)

    print("\n\n\nMonk 3\n\n\n")
    partition_accuracy_monk3 = prune_tree(monkdata.monk3)
    print_csv_style(partition_accuracy_monk3)

    print("\n\n\nMonk 2\n\n\n")
    partition_accuracy_monk2 = prune_tree(monkdata.monk2)
    print_csv_style(partition_accuracy_monk2)

