import copy
import matplotlib.pyplot as plt
import random
import sys


k_value = 15
data_dimension = 2

dataset = []

p = 0
clusters = [ [] for _ in range(k_value) ]
means = [ [0]*data_dimension for _ in range(k_value) ]
prev_evaluation_value = 0

def load_data():
    if len(sys.argv) != 2:
        print('Wrong amount of arguments.\nUsage: python3 k-means.py [dataset_path]')
        exit()
    dataset_path = sys.argv[1]
    dataset_file = open(dataset_path,'r')
    dataset_raw = dataset_file.read().split()
    for i in range(int(len(dataset_raw)/data_dimension)):
        dataset.append((dataset_raw[i*data_dimension], dataset_raw[i*data_dimension+1]))
    dataset.sort()
        
def calculate_cluster():
    global p, clusters, means, prev_evaluation_value
    #Initial data assignment to cluster
    for data in dataset:
        clusters[random.randint(0, k_value-1)].append(data)
    while True:
        #Calculate mean values of clusters
        for i in range(k_value):
            sum = [0] * len(dataset[0])
            for data in clusters[i]:
                for j in range(data_dimension):
                    sum[j] += int(data[j])
            for j in range(data_dimension):
                if len(clusters[i]) > 0:
                    means[i][j] = sum[j]/len(clusters[i])
        #Move data to closer cluster
        moves = 0
        for i in range(k_value):
            for j in range(k_value):
                if i == j:
                    continue
                clusters_copy = copy.deepcopy(clusters)
                for data in clusters_copy[i]:
                    original_distance = 0
                    new_distance = 0
                    for k in range(data_dimension):
                        original_distance += (int(data[k]) - means[i][k]) ** 2
                        new_distance += (int(data[k]) - means[j][k]) ** 2
                    if original_distance > new_distance:
                        moves += 1
                        clusters[i].remove(data)
                        clusters[j].append(data)
        #Evaluate
        evaluation_value = 0
        for i in range(k_value):
            for data in clusters[i]:
                distance_sum = 0
                for j in range(data_dimension):
                    distance_sum += (int(data[j]) - means[i][j]) ** 2
                evaluation_value += distance_sum ** (1/2)
        print('Evaluation value is '+str(evaluation_value))
        print('Moved data: '+str(moves))
        print('Attempt: '+str(p))
        zero_data_cluster_count = 0
        for i in range(k_value):
            if len(clusters[i]) ==  0:
                zero_data_cluster_count += 1
        print('Clusters with no data: '+str(zero_data_cluster_count))
        if moves < 5:
            break
        else:
            prev_evaluation_value = evaluation_value
        p += 1
        
def display():
    x = [ [] for _ in range(k_value) ]
    y = [ [] for _ in range(k_value) ]
    for i in range(k_value):
        x[i] = [ int(data[0]) for data in clusters[i] ]
        y[i] = [ int(data[1]) for data in clusters[i] ]
    for i in range(k_value):
        if i % 5 == 0:
            color = 'r'
        elif i % 5 == 1:
            color = 'g'
        elif i % 5 == 2:
            color = 'b'
        elif i % 5 == 3:
            color = 'c'
        elif i % 5 == 4:
            color = 'm'
        if i % 3 == 0:
            shape = 'o'
        elif i % 3 == 1:
            shape = 'x'
        elif i % 3 == 2:
            shape = '*'
        plt.plot(x[i], y[i], color+shape)
    plt.show()
        
def main():
    load_data()
    calculate_cluster()
    display()

if __name__=='__main__':
    main()



