import numpy as np
import random
import time
import re
import xlsxwriter

c_border = 0
q_border = 0
qco = []
neighbour_sets = []
non_neighbours = []
index = []
best_clique = []
tightness = []
add_tabu = []
rem_tabu = []

def GetFile(filename):
    global neighbour_sets, non_neighbours, qco, index, tightness
    with open(filename) as file:
        fin = file.readlines()
            
    vertices = 0
    edges = 0
    for i in range(0, len(fin)):
        lst = re.findall(r'\w+', fin[i])
        if fin[i][0] == 'c':
            continue

        if fin[i][0] == 'p':
            vertices = int(lst[2])
            edges = int(lst[3])
            neighbour_sets = [set() for i in range(vertices)]
            qco = [0 for i in range(vertices)]
            non_neighbours = [set() for i in range(vertices)]
            index = [0 for i in range(vertices)]
            tightness = [0 for i in range(vertices)]
            
        else:
            start = int(lst[1])
            finish = int(lst[2])
            #Edges in DIMACS file can be repeated, but it is not a problem for our sets
            neighbour_sets[start - 1].add(finish - 1)
            neighbour_sets[finish - 1].add(start - 1)
            
    for i in range(vertices):
        for j in range(vertices):
            if j not in neighbour_sets[i] and i != j:
                non_neighbours[i].add(j)      
                
def RunSearch(starts):
    global neighbour_sets, qco, best_clique, c_border, q_border
    for i in range(starts):
        ClearClique()
        for i in range(len(neighbour_sets)):
            qco[i] = i
            index[i] = i
            
        RunInitialHeuristic()
        
        c_border = q_border
        swaps = 0
        
        while swaps < len(neighbour_sets) * 100:
            if Move() == False:
                if Swap1To1() == False:
                    break
                else:
                    swaps += 1
                    
        if q_border > len(best_clique):
            best_clique.clear()
            for i in range(q_border):
                best_clique.append(qco[i])
                
def SwapVertices(vertex, border):
    global qco, index
    vertex_at_border = qco[border]
    qco[index[vertex]], qco[border] = qco[border], qco[index[vertex]]
    index[vertex], index[vertex_at_border] = index[vertex_at_border], index[vertex]
    
def InsertToClique(i):
    global non_neighbours, c_border, q_border, tightness
    for j in non_neighbours[i]:
        if tightness[j] == 0:
            c_border -= 1
            SwapVertices(j, c_border)
        tightness[j] += 1
    
    SwapVertices(i, q_border)
    q_border += 1
    
def RemoveFromClique(k):
    global non_neighbours, c_border, q_border, tightness
    for j in non_neighbours[k]:
        if tightness[j] == 1:
            SwapVertices(j, c_border)
            c_border += 1

        tightness[j] -= 1
            
    q_border -= 1
    SwapVertices(k, q_border)
    
def Swap1To1():
    global non_neighbours, q_border, c_border, qco, tightness, add_tabu, rem_tabu
    for counter in range(q_border):
        vertex = qco[counter]
        if vertex in add_tabu:
            continue
        for i in non_neighbours[vertex]:
            if tightness[i] == 1 and i not in rem_tabu:
                RemoveFromClique(vertex)
                rem_tabu.append(vertex)
                add_tabu.append(i)
                InsertToClique(i)
                return True
            
    return False

def Move():
    global q_border, c_border, qco
    if c_border == q_border:
        return False
    
    vertex = qco[q_border]
    InsertToClique(vertex)
    return True

def RunInitialHeuristic():
    global q_border, neighbour_sets
    
    graph = {}
        
    for i in range(len(neighbour_sets)):
        graph[i] = neighbour_sets[i]
    
    vertices = sorted(graph, key=lambda x: len(graph[x]), reverse=True)
    
    best_clique_1 = []
    
    for i in range(int(len(vertices))):

        candidates = vertices.copy()
    
        clique = []
        
        index = random.randint(0, len(candidates)-1) 
        vert = candidates[index]
        clique.append(vert)
        
        #пересчитываем кандидатов
        for ver in candidates.copy():
                if ver not in graph[vert] and ver in candidates:
                    candidates.remove(ver)
    
        while len(candidates) != 0:
            #выбираем рандомного кандидата
            index = random.randint(0, int(len(candidates))-1)
            vert = candidates[index]
            clique.append(vert)
        
            #пересчитываем кандидатов
            for ver in candidates.copy():
                if ver not in graph[vert] and ver in candidates:
                    candidates.remove(ver)
                    
        
        #проверка на лучшую клику
        if len(clique) > len(best_clique_1):
            best_clique_1 = clique
                
    for vertex in best_clique_1:
        SwapVertices(vertex, q_border)
        q_border += 1
        
def Check():
    global neighbour_sets, best_clique
    for i in best_clique:
        for j in best_clique:
            if i != j and j not in neighbour_sets[i]:
                print("Returned subgraph is not clique\n")
                return False
            
    return True

def ClearClique():
    global q_border, c_border
    q_border = 0
    c_border = 0
    
files = ["brock200_1.clq", 
        "brock200_2.clq", 
        "brock200_3.clq", 
        "brock200_4.clq",
        "brock400_1.clq",
        "brock400_2.clq",
        "brock400_3.clq",
        "brock400_4.clq",
        "C125.9.clq", 
        "gen200_p0.9_44.clq",
        "gen200_p0.9_55.clq",
        "hamming8-4.clq",
        "johnson16-2-4.clq",
        "johnson8-2-4.clq",
        "keller4.clq",
        "MANN_a27.clq",
        "MANN_a9.clq", 
        "p_hat1000-1.clq",
        "p_hat1000-2.clq",
        "p_hat1500-1.clq",
        "p_hat300-3.clq",
        "p_hat500-3.clq",
        "san1000.clq",
        "sanr200_0.9.clq",
        "sanr400_0.7.clq"]

book = xlsxwriter.Workbook('clique_local_search_100_3.xlsx')
sheet = book.add_worksheet() 

row = 0
column = 0

for item in ["Instance", "Time (sec)", "Clique size", "Clique vertices"]:
    sheet.write(row, column, item)
    column += 1
    
row += 1
    
print("Instance", "Time (sec)", "Clique size", "Clique vertices")
    
for file in files:
    GetFile("C:\Users\Елена\Documents" + file)
        
    start = time.time()
        
    RunSearch(100)
        
    if Check() == False:
        print("*** WARNING: incorrect coloring: ***\n")
            
    finish = time.time()
    
    for item in [file, round((finish - start), 3), len(best_clique), str(best_clique), "\n"]:
        sheet.write(row, column, item)
        column += 1
        
    row += 1

    print("Instance: ", file, ";", "Time: ", round((finish - start), 3), ";", "Clique size: ", len(best_clique), ";", "Clique vertices: ", best_clique, "\n")

    print('---------------------------------')
        
    best_clique.clear()
            
book.close()