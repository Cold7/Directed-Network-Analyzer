import networkx as nx
from os import listdir
import multiprocessing as mp
import argparse

def parallelProperties(name):
	print name
	#creating multi directed graph
	MG=nx.MultiGraph()
	
	#reading file and adding nodes - edges
	file=None
	if pathToFiles!=None:
		file=open(pathToFiles+"/"+name,"r")
	else:
		file=open("./"+name,"r")
	listOfInteractions=[] #i will save interactions to rebuild the directed digraph
	for line in file:
		splittedLine=line.split("\t")
		node1=splittedLine[0]
		node2=splittedLine[1]
		listOfInteractions.append(node1+":"+node2)
		MG.add_edge(node1, node2)

	file.close()
	#####################################
	##
	## dict to save measures
	##
	#####################################
	dictProp={}
	for node in MG.nodes():
		dictProp[node]={"average_shortest_path_length":'', "clustering_coefficient":'0',"closeness_centrality":'', "eccentricity":'',"stress":'0',"edge_count":'',"In_degree":'0',"Out_degree":'0',"Betweenness_centrality":'', "Neighborhood_conectivity":''}

	file=None
	if pathToFiles!=None:
		file=open(pathToFiles+"/"+name,"r")
	else:
		file=open("./"+name,"r")
	####################################################################
	##
	## for in degree and out degree
	##
	#################################################################### 
	for line in file:
		splittedLine=line.split("\t")
		node1=splittedLine[0]
		node2=splittedLine[1]
		dictProp[node1]["Out_degree"]=str(int(dictProp[node1]["Out_degree"])+1)
		dictProp[node2]["In_degree"]=str(int(dictProp[node2]["In_degree"])+1)
		
	file.close()			
				
	#we will see subgraphs
	subGS=list(nx.connected_component_subgraphs(MG))
	#now we will rebuild these graphs as multidigraphs
	for subG in list(nx.connected_component_subgraphs(MG)):
		#first step: create a multidigraph
		md=nx.MultiDiGraph()
		whitoutSL=nx.MultiGraph() #a graph without selfloops
		directed=nx.DiGraph()
		MDNoSelfLoop=nx.MultiDiGraph() #a graph without selfloops
		#the second step is to loop over the edges, searching for the direction of interaction
		for edge in nx.edges(subG):
			nodeX, nodeY=edge

			#if is a self interaction
			if nodeX==nodeY:
				md.add_edge(nodeX,nodeY)
				directed.add_edge(nodeX,nodeY)
			else:
				#if is not a self interaction I will look for the directions (if exist A:B and/or B:A) and Ill add the edge
				cont=0
				if nodeX+":"+nodeY in listOfInteractions:
					md.add_edge(nodeX,nodeY)
					directed.add_edge(nodeX,nodeY)
					whitoutSL.add_edge(nodeX,nodeY)
					MDNoSelfLoop.add_edge(nodeX,nodeY)
				if nodeY+":"+nodeX in listOfInteractions:
					md.add_edge(nodeY,nodeX)
					whitoutSL.add_edge(nodeY,nodeX)
					directed.add_edge(nodeY,nodeX)
					MDNoSelfLoop.add_edge(nodeY,nodeX)
					
					
		####################################################################
		##
		##							Metrics
		##
		####################################################################				

		for node in md.nodes():
			####################################################################
			##
			##					Edge count
			##
			####################################################################
			dictProp[node]["edge_count"]=str(int(dictProp[node]["Out_degree"])+int(dictProp[node]["In_degree"]))
		
			####################################################################
			##
			##					average shortest path length			
			##
			####################################################################
			
			#at this point we have directed subgraphs, so now is time to comute average shortest path of each subgraph
	
			#first we will compute shortest path of one node, then we will compute average shortest path length
			shortestPaths=nx.shortest_path_length(md, source=node)
			
			summatory=0
			cont=0
			for item in shortestPaths.items():
				summatory+=float(item[1])
				cont+=1
			if (cont-1)!=0:
				dictProp[node]["average_shortest_path_length"]=str(summatory/(cont-1))
				#print node,(summatory/(cont-1))
			else:
				dictProp[node]["average_shortest_path_length"]="0"
			####################################################################
			##
			##					eccentricity			
			##
			####################################################################
			higher=0
			for paths in shortestPaths.items():
				if int(paths[1])>higher:
					higher=int(paths[1])
			dictProp[node]["eccentricity"]=str(higher)
							

		
		####################################################################
		##
		##					closeness centrality			
		##
		####################################################################

		for item in (nx.closeness_centrality(md, normalized=False)).items():
			dictProp[item[0]]["closeness_centrality"]=str(item[1])		
			
		####################################################################
		##
		##					neighborhood connectivity			
		##
		####################################################################					
		
		for item in (nx.average_neighbor_degree(whitoutSL)).items():
			dictProp[item[0]]["Neighborhood_conectivity"]=str(item[1])

		####################################################################
		##
		##					stress centrality		
		##
		####################################################################		
		for Source in md.nodes():
			for Target in md.nodes():
				if Source!=Target:
					try:
						for path in nx.all_shortest_paths(md,source=Source,target=Target):
							if len(path)>2:
								for N in path[1:-1]:
									dictProp[N]["stress"]=str(int(dictProp[N]["stress"])+1)
					except:
						pass
					
		####################################################################
		##
		##					betweenness centrality		
		##
		####################################################################		
		for item in (nx.betweenness_centrality(md)).items():
			dictProp[item[0]]["Betweenness_centrality"]=str(item[1])
		 
		
		####################################################################
		##
		##					clustering coefficient			
		##
		####################################################################
		
		for node in MDNoSelfLoop.nodes():
			inPlusOut=float(dictProp[node]["Out_degree"])+float(dictProp[node]["In_degree"])
			division=(len(whitoutSL.neighbors(node))*(len(whitoutSL.neighbors(node))-1))	
			if len(whitoutSL.neighbors(node))>1: #if node has at least two neighbour
				connectedNeighbors=0
				neighbors=whitoutSL.neighbors(node)
				for neighbor in neighbors:
					#print neighbor
					neighborsOfNeighbors=MDNoSelfLoop.neighbors(neighbor)
					#print neighbor, neighborsOfNeighbors
					for n in neighborsOfNeighbors:
						#print n
						if n in neighbors:
							connectedNeighbors+=1
				dictProp[node]["clustering_coefficient"]=str(float(connectedNeighbors)/division)

	outFile=None
	if Result!=None:
		outFile=open(Result+"/"+name[:-4]+".csv","w")
	else:
		outFile=open("./"+name[:-4]+".csv","w")
		
	outFile.write("\"AverageShortestPathLength\",\"BetweennessCentrality\",\"ClosenessCentrality\",\"ClusteringCoefficient\",\"Eccentricity\",\"EdgeCount\",\"Indegree\",\"name\",\"NeighborhoodConnectivity\",\"Outdegree\",\"Stress\"\n")
	for item in dictProp.items():
		node=item[0]
		outFile.write("\""+dictProp[node]["average_shortest_path_length"]+"\",\""+dictProp[node]["Betweenness_centrality"]+"\",\""+dictProp[node]["closeness_centrality"]+"\",\""+dictProp[node]["clustering_coefficient"]+"\",\""+dictProp[node]["eccentricity"]+"\",\""+dictProp[node]["edge_count"]+"\",\""+dictProp[node]["In_degree"]+"\",\""+node+"\",\""+dictProp[node]["Neighborhood_conectivity"]+"\",\""+dictProp[node]["Out_degree"]+"\",\""+dictProp[node]["stress"]+"\"\n")

	outFile.close()
	



def main():
	global Result, pathToFiles
	parser = argparse.ArgumentParser()
	#number of processors to use
	parser.add_argument("-P","--path", help="path where TSV files are located")
	parser.add_argument("-R","--results", help="/Path/where/resultfiles/will/be/saved (do not put / after path) If you do not specify a path, current path of script will be used")
	parser.add_argument("-I","--Input", help="A single TSV input file ")
	
	parser.add_argument("-N","--nproc",help="Number of processors to use. Default: all", default="all")
	args = parser.parse_args()
	
	if args.results==None and (args.path==None or args.Input==None):
		print "use --help option"
		exit()
	if args.path and args.Input:
		print "\nYou only can use one option between -R and -I\n"
		exit()
	if args.results:
		Result=args.results
	else:
		Result=None
	if args.path:
		pathToFiles=args.path
	else:
		pathToFiles=None
	pool=None
	if args.nproc=="all":
		pool=mp.Pool()#processes=int(nproc)) #for multiprocessing
	else:
		pool=mp.Pool(processes=int(args.nproc)) #for multiprocessing

	tsvList=[]
	if args.path:
		
		for file in listdir(str(args.path)):
			if file[-4:]==".tsv":
				tsvList.append(file)
	elif args.Input:
		#print args.Input
		tsvList.append(args.Input)
		
	processReturn=pool.map(parallelProperties,(tsvList))	
	
if __name__=="__main__":
	main()
